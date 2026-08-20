from __future__ import annotations

from collections.abc import Mapping

from .models import Attribution, Classification, Outcome


def _header_names(headers: Mapping[str, str] | None) -> set[str]:
    if not headers:
        return set()
    return {str(k).lower() for k in headers}


def _text(*parts: str | None) -> str:
    return " ".join(p for p in parts if p).lower()


def classify(
    *,
    status_code: int | None = None,
    error: str | None = None,
    body_hint: str | None = None,
    headers: Mapping[str, str] | None = None,
    endpoint_probe_failed: bool = False,
) -> Classification:
    """Classify one retrieval observation conservatively.

    The function separates the observed outcome from root-cause attribution.
    HTTP status codes alone do not prove which component generated the
    response, and proxy-path errors do not automatically prove that a proxy
    endpoint itself is unhealthy.

    Header values are intentionally not inspected or copied. Only normalized
    header names are used for signals such as ``Retry-After`` and
    ``Proxy-Authenticate``.

    ``endpoint_probe_failed`` is intentionally explicit: callers should set it
    only when a dedicated, independent proxy endpoint health probe has failed.
    """

    header_names = _header_names(headers)
    text = _text(error, body_hint)

    proxy_auth_tokens = (
        "proxy authentication required",
        "proxy authentication expired",
        "proxy auth failed",
        "proxy_authentication",
        "err_proxy_auth",
    )
    proxy_path_tokens = (
        "err_proxy_connection_failed",
        "cannot connect to proxy",
        "could not connect to proxy",
        "proxy connection failed",
        "proxy connect error",
        "proxy tunnel failed",
    )
    challenge_tokens = (
        "captcha",
        "datadome",
        "cloudflare challenge",
        "access denied",
        "security verification",
    )

    if endpoint_probe_failed:
        return Classification(
            outcome=Outcome.PROXY_ENDPOINT_UNHEALTHY,
            attribution=Attribution.PROXY,
            confidence=0.99,
            proxy_layer_evidence=True,
            proxy_endpoint_health_evidence=True,
            automatic_rotation_evidence=True,
            recommended_action="quarantine_endpoint_and_verify_provider_health",
            evidence=("dedicated proxy endpoint health probe failed",),
        )

    proxy_auth_text = any(token in text for token in proxy_auth_tokens)
    proxy_auth_header = "proxy-authenticate" in header_names
    if status_code == 407 or proxy_auth_header or proxy_auth_text:
        return Classification(
            outcome=Outcome.PROXY_AUTH_FAILURE,
            attribution=Attribution.PROXY,
            confidence=0.99,
            proxy_layer_evidence=True,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="refresh_proxy_credentials_before_endpoint_demotion",
            evidence=tuple(
                x
                for x in (
                    "HTTP 407" if status_code == 407 else None,
                    "Proxy-Authenticate header present" if proxy_auth_header else None,
                    "proxy-authentication error signal" if proxy_auth_text else None,
                )
                if x
            ),
        )

    if any(token in text for token in proxy_path_tokens):
        return Classification(
            outcome=Outcome.PROXY_PATH_FAILURE,
            attribution=Attribution.AMBIGUOUS,
            confidence=0.98,
            proxy_layer_evidence=True,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="validate_client_protocol_credentials_and_endpoint_before_rotation",
            evidence=("explicit proxy-path connection failure",),
        )

    if status_code is not None and 200 <= status_code <= 299:
        return Classification(
            outcome=Outcome.SUCCESS,
            attribution=Attribution.NONE,
            confidence=1.0,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="keep_current_policy",
            evidence=(f"HTTP {status_code}",),
        )

    if status_code is not None and 300 <= status_code <= 399:
        return Classification(
            outcome=Outcome.HTTP_REDIRECT,
            attribution=Attribution.AMBIGUOUS,
            confidence=1.0,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="evaluate_redirect_destination_before_counting_usable_success",
            evidence=(f"HTTP {status_code}",),
        )

    if status_code == 429:
        return Classification(
            outcome=Outcome.HTTP_RATE_LIMIT,
            attribution=Attribution.AMBIGUOUS,
            confidence=0.99,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="respect_retry_after_and_backoff_without_proxy_demotion",
            evidence=tuple(
                x
                for x in (
                    "HTTP 429",
                    "Retry-After present" if "retry-after" in header_names else None,
                )
                if x
            ),
        )

    if status_code == 451:
        return Classification(
            outcome=Outcome.HTTP_LEGAL_RESTRICTION,
            attribution=Attribution.AMBIGUOUS,
            confidence=0.99,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="treat_as_legal_restriction_signal_without_proxy_demotion",
            evidence=("HTTP 451",),
        )

    if status_code == 403:
        challenged = any(token in text for token in challenge_tokens)
        extra = ("challenge/access-control hint present",) if challenged else ()
        return Classification(
            outcome=Outcome.HTTP_ACCESS_DENIED,
            attribution=Attribution.AMBIGUOUS,
            confidence=0.99,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="inspect_response_origin_policy_and_request_context_before_proxy_action",
            evidence=("HTTP 403", *extra),
        )

    if status_code is not None and 500 <= status_code <= 599:
        return Classification(
            outcome=Outcome.HTTP_5XX,
            attribution=Attribution.AMBIGUOUS,
            confidence=1.0,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="retry_with_backoff_without_proxy_demotion",
            evidence=(f"HTTP {status_code}",),
        )

    if status_code is not None and 400 <= status_code <= 499:
        return Classification(
            outcome=Outcome.HTTP_OTHER_4XX,
            attribution=Attribution.AMBIGUOUS,
            confidence=1.0,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="inspect_response_and_request_context_before_proxy_action",
            evidence=(f"HTTP {status_code}",),
        )

    if error:
        return Classification(
            outcome=Outcome.AMBIGUOUS,
            attribution=Attribution.AMBIGUOUS,
            confidence=0.45,
            proxy_layer_evidence=False,
            proxy_endpoint_health_evidence=False,
            automatic_rotation_evidence=False,
            recommended_action="collect_more_transport_and_response_evidence",
            evidence=("unclassified network/application error",),
        )

    return Classification(
        outcome=Outcome.AMBIGUOUS,
        attribution=Attribution.AMBIGUOUS,
        confidence=0.20,
        proxy_layer_evidence=False,
        proxy_endpoint_health_evidence=False,
        automatic_rotation_evidence=False,
        recommended_action="collect_status_error_headers_or_sanitized_body_hint",
        evidence=("insufficient evidence",),
    )
