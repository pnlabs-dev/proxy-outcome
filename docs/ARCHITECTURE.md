# Architecture

`proxy-outcome` is a local, dependency-free observation-classification layer.

```text
sanitized HTTP status / error / header names / body hint
                           |
                           v
                  deterministic rules
                           |
                           v
                   observed outcome
                           |
                  +--------+--------+
                  |                 |
                  v                 v
          supported attribution   evidence flags
                  |                 |
                  +--------+--------+
                           |
                           v
                      caller policy
```

## Design goals

1. **Observation before attribution** — classify the signal without inventing who caused it.
2. **Evidence before action** — do not convert generic failures into endpoint demotion/rotation.
3. **Separate proxy layer from endpoint health** — proxy-path/auth evidence is not automatically endpoint-health evidence.
4. **Conservative defaults** — ambiguous root causes remain ambiguous.
5. **Zero runtime dependencies** — easy to embed in workers, gateways, and test harnesses.
6. **Machine-readable output** — every result exposes outcome, attribution, confidence, evidence flags, and a conservative policy hint.
7. **Local-only execution** — no network I/O, telemetry, persistence, or credential storage.

## Evidence model

The public API intentionally separates:

- `outcome`: what the supplied observation supports;
- `attribution`: root-cause scope, only when supported;
- `proxy_layer_evidence`: whether the observation points to the proxy layer/path;
- `proxy_endpoint_health_evidence`: whether the observation supports a claim about endpoint health;
- `automatic_rotation_evidence`: whether v0.1 considers the evidence strong enough to justify automatic endpoint rotation.

For example, a proxy connection/path error can set `proxy_layer_evidence=True` while leaving endpoint-health and automatic-rotation evidence false.

## Dedicated endpoint probes

`endpoint_probe_failed=True` is an explicit caller-supplied assertion. The library does not implement, schedule, or transmit endpoint probes. This preserves a strict boundary between classification and active network operations.

## Data handling

Header **values are intentionally ignored** by the classifier; only normalized header names are inspected for signals such as `Retry-After` or `Proxy-Authenticate`.

Sanitized `error` and `body_hint` strings are used transiently in memory for token matching. Returned `evidence` contains normalized labels, not raw error strings, header values, or body hints.

The library does not log, persist, transmit, or phone home. Callers remain responsible for not supplying secrets or personal data unnecessarily.

## Public / commercial boundary

This repository intentionally contains only a transparent deterministic baseline. It excludes commercial control-plane implementation details, private scoring/routing heuristics, provider configuration, infrastructure topology, credentials, and non-public datasets.

See [`PUBLIC-BOUNDARY.md`](PUBLIC-BOUNDARY.md).

## Non-goals

This repository is not a proxy provider, CAPTCHA bypass system, browser-stealth package, or access-control bypass toolkit. It does not attempt to defeat technical restrictions.

## Intended integrations

The classifier can sit behind normal HTTP clients, browser workers, scraping frameworks, custom proxy pools, and benchmark/observability pipelines.

The caller remains responsible for complying with applicable terms, rate limits, robots policies where relevant, and law.
