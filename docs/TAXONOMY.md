# Outcome taxonomy

`proxy-outcome` separates three questions that are often collapsed together:

1. **What was observed?**
2. **What root cause is actually supported?**
3. **Is there enough evidence to change proxy health/rotation policy?**

The core rule is conservative:

> An HTTP status or proxy-path error is not, by itself, proof that a proxy endpoint is unhealthy.

## Outcomes

| Outcome | Default attribution | Proxy-layer evidence? | Endpoint-health evidence? | Notes |
|---|---|---:|---:|---|
| `SUCCESS` | none | no | no | HTTP 2xx only |
| `HTTP_REDIRECT` | ambiguous | no | no | HTTP 3xx; not counted as usable success automatically |
| `PROXY_AUTH_FAILURE` | proxy | yes | no | HTTP 407 or explicit proxy-auth signal |
| `PROXY_PATH_FAILURE` | ambiguous | yes | no | explicit proxy connection/path failure; root cause can still be client/protocol/config/network/endpoint |
| `PROXY_ENDPOINT_UNHEALTHY` | proxy | yes | yes | requires an explicit failed dedicated endpoint probe supplied by the caller |
| `HTTP_RATE_LIMIT` | ambiguous | no | no | HTTP 429; response origin is not inferred from the status alone |
| `HTTP_LEGAL_RESTRICTION` | ambiguous | no | no | HTTP 451; no automatic geo interpretation |
| `HTTP_ACCESS_DENIED` | ambiguous | no | no | HTTP 403; may include sanitized challenge/access-control hints |
| `HTTP_OTHER_4XX` | ambiguous | no | no | other HTTP 4xx observations |
| `HTTP_5XX` | ambiguous | no | no | HTTP 5xx observations; origin/root cause remains unresolved |
| `AMBIGUOUS` | ambiguous | no | no | insufficient or non-specific evidence |

## Why HTTP responses remain attribution-ambiguous

A received HTTP status describes the transaction observed by the client. It does not reliably identify which component generated the response. Depending on the path, an origin server, CDN, WAF, reverse proxy, gateway, intermediary, or another component may have produced it.

The library therefore classifies the HTTP outcome while leaving root-cause attribution ambiguous unless stronger evidence exists.

## Why proxy-path failure is not endpoint-health proof

Errors such as `ERR_PROXY_CONNECTION_FAILED` identify a failure while establishing or using the proxy path. They do not distinguish among:

- client/browser compatibility;
- protocol mismatch;
- credential/configuration errors;
- local/network path problems;
- an unhealthy endpoint.

For that reason `PROXY_PATH_FAILURE` is proxy-layer evidence but not endpoint-health evidence and does not automatically justify rotation.

## Dedicated endpoint probes

`endpoint_probe_failed=True` is an explicit caller assertion that a dedicated, independent endpoint health probe failed. Only this stronger signal produces `PROXY_ENDPOINT_UNHEALTHY` and `automatic_rotation_evidence=True` in v0.1.

The library does not perform that probe itself.

## Confidence

`confidence` expresses confidence in the **outcome classification from the supplied observation**, not:

- probability that a retry will succeed;
- probability that a proxy is bad;
- probability that a target generated the response.

For example, `HTTP 429` can classify as `HTTP_RATE_LIMIT` with high confidence while attribution remains `ambiguous`.

## Policy boundary

`proxy-outcome` is stateless and deterministic. It does not contain adaptive routing, provider scoring, cross-workload learning, private infrastructure data, or commercial control-plane policy.
