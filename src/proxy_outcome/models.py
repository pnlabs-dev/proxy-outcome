from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Attribution(str, Enum):
    """Best-supported root-cause scope for the observation.

    HTTP status codes alone do not identify the component that generated the
    response, so response-side outcomes normally remain ambiguous.
    """

    PROXY = "proxy"
    AMBIGUOUS = "ambiguous"
    NONE = "none"


class Outcome(str, Enum):
    SUCCESS = "SUCCESS"
    HTTP_REDIRECT = "HTTP_REDIRECT"
    HTTP_ACCESS_DENIED = "HTTP_ACCESS_DENIED"
    HTTP_RATE_LIMIT = "HTTP_RATE_LIMIT"
    HTTP_LEGAL_RESTRICTION = "HTTP_LEGAL_RESTRICTION"
    HTTP_OTHER_4XX = "HTTP_OTHER_4XX"
    HTTP_5XX = "HTTP_5XX"
    PROXY_AUTH_FAILURE = "PROXY_AUTH_FAILURE"
    PROXY_PATH_FAILURE = "PROXY_PATH_FAILURE"
    PROXY_ENDPOINT_UNHEALTHY = "PROXY_ENDPOINT_UNHEALTHY"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class Classification:
    outcome: Outcome
    attribution: Attribution
    confidence: float
    proxy_layer_evidence: bool
    proxy_endpoint_health_evidence: bool
    automatic_rotation_evidence: bool
    recommended_action: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["outcome"] = self.outcome.value
        data["attribution"] = self.attribution.value
        data["evidence"] = list(self.evidence)
        return data
