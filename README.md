# proxy-outcome

**403 ≠ bad proxy. 429 ≠ bad proxy. 451 ≠ bad proxy.**

`proxy-outcome` is a small, deterministic classification library for HTTP and proxy-path observations in scraping and web-retrieval systems.

Its job is deliberately narrow: preserve evidence without inventing a root cause.

Built by **PN Labs**.

## Why this exists

A common reliability mistake is:

```text
unsuccessful request
        ↓
   "bad proxy"
        ↓
 rotate / demote
```

That collapses different layers into one conclusion. An HTTP status, a proxy-authentication error, a browser/client compatibility problem, and a failed endpoint health probe are different observations and should not automatically share the same health consequence.

`proxy-outcome` keeps the pipeline explicit:

```text
observation
    ↓
outcome classification
    ↓
root-cause attribution (only when supported)
    ↓
proxy-layer / endpoint-health evidence
    ↓
caller policy
```

## Install

The project is alpha and can be installed from source:

```bash
python -m pip install .
```

Runtime dependencies: **none**.

## Python API

```python
from proxy_outcome import classify

result = classify(status_code=451)

print(result.outcome.value)
# HTTP_LEGAL_RESTRICTION

print(result.attribution.value)
# ambiguous

print(result.proxy_endpoint_health_evidence)
# False
```

A proxy-path failure is evidence that the proxy path failed, but it is not enough to declare the endpoint unhealthy:

```python
result = classify(error="net::ERR_PROXY_CONNECTION_FAILED")

assert result.proxy_layer_evidence is True
assert result.proxy_endpoint_health_evidence is False
assert result.automatic_rotation_evidence is False
```

Automatic rotation evidence is reserved for stronger evidence supplied by the caller, such as a failed dedicated endpoint probe:

```python
result = classify(endpoint_probe_failed=True)

assert result.proxy_endpoint_health_evidence is True
assert result.automatic_rotation_evidence is True
```

## CLI

```bash
proxy-outcome classify --status 429 --header 'Retry-After: 60'
```

Example output:

```json
{
  "attribution": "ambiguous",
  "automatic_rotation_evidence": false,
  "confidence": 0.99,
  "evidence": [
    "HTTP 429",
    "Retry-After present"
  ],
  "outcome": "HTTP_RATE_LIMIT",
  "proxy_endpoint_health_evidence": false,
  "proxy_layer_evidence": false,
  "recommended_action": "respect_retry_after_and_backoff_without_proxy_demotion"
}
```

## Current taxonomy

| Observation | Classification | Root cause | Endpoint-health evidence? |
|---|---|---|---:|
| HTTP 2xx | `SUCCESS` | none | no |
| HTTP 3xx | `HTTP_REDIRECT` | ambiguous | no |
| HTTP 407 / explicit proxy-auth signal | `PROXY_AUTH_FAILURE` | proxy | no |
| explicit proxy-path connection failure | `PROXY_PATH_FAILURE` | ambiguous | no |
| failed dedicated endpoint probe | `PROXY_ENDPOINT_UNHEALTHY` | proxy | **yes** |
| HTTP 429 | `HTTP_RATE_LIMIT` | ambiguous | no |
| HTTP 451 | `HTTP_LEGAL_RESTRICTION` | ambiguous | no |
| HTTP 403 | `HTTP_ACCESS_DENIED` | ambiguous | no |
| other HTTP 4xx | `HTTP_OTHER_4XX` | ambiguous | no |
| HTTP 5xx | `HTTP_5XX` | ambiguous | no |
| unknown network/application error | `AMBIGUOUS` | ambiguous | no |

See [`docs/TAXONOMY.md`](docs/TAXONOMY.md).

## Design principles

- **Observation before attribution** — status codes classify what was observed, not who caused it.
- **Evidence before action** — rotation/demotion requires stronger evidence than a generic failure.
- **Endpoint health is a separate claim** — proxy-path/auth problems do not automatically mean the endpoint is unhealthy.
- **Redirects are not usable-success by default** — 3xx remains a distinct outcome.
- **Ambiguity is allowed** — the library prefers `AMBIGUOUS` over false certainty.
- **Zero runtime dependencies** — easy to embed in workers, gateways, and test harnesses.
- **No network or telemetry** — the package performs local classification only.

## Security and public boundary

The library does not make network requests, store credentials, inspect raw header values, emit raw headers/body hints, or send telemetry.

Do not pass real credentials, session cookies, private endpoint URLs, private IP addresses, or personal data into examples/issues. CLI arguments can also appear in shell history or process listings, so use only sanitized hints.

This repository intentionally contains only the transparent local baseline. Commercial control-plane implementation, private routing/scoring logic, private infrastructure details, provider credentials/configuration, and non-public datasets are out of scope.

See [`SECURITY.md`](SECURITY.md) and [`docs/PUBLIC-BOUNDARY.md`](docs/PUBLIC-BOUNDARY.md).

## Validation

```bash
python -m pip install .
python -m unittest discover -s tests -v
python scripts/public_hygiene_check.py
```

CI installs the package before testing, runs CLI smoke tests, and executes a non-echoing, vendor-neutral public-repository hygiene gate that checks for common secret/token shapes, credential-bearing URLs, private IPv4 literals, and email addresses.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Design partners

If you operate a legitimate scraping/web-retrieval workload and want to compare naive rotation against evidence-based classification, see [`DESIGN-PARTNER.md`](DESIGN-PARTNER.md).

Preferred benchmark inputs are sanitized aggregate counts or a synthetic reproducer. Do not submit production logs, credentials, private URLs, endpoint IPs, cookies, or personal data.

## Responsible use

Use this project only for workloads you are authorized to run. Respect applicable target policies, rate limits, robots directives where relevant, and law.

## License

MIT.
