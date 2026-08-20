# Contributing

Thanks for considering a contribution to `proxy-outcome`.

## Scope

Good contributions improve the public deterministic baseline without weakening its core rule: preserve observations without inventing root cause.

Useful changes include:

- clearer taxonomy or documentation;
- additional conservative classification cases;
- regression tests for ambiguous outcomes;
- CLI usability improvements;
- packaging or CI improvements;
- security and data-minimization hardening.

Private routing/scoring logic, provider-specific private configuration, credentials, production infrastructure, and non-public benchmark data do not belong in this repository.

## Development

```bash
python -m pip install .
python -m unittest discover -s tests -v
python scripts/public_hygiene_check.py
```

Keep runtime dependencies at zero unless there is a strong, documented reason to change that constraint.

## Pull requests

A good pull request should:

1. explain the observed problem before proposing attribution;
2. include tests for behavior changes;
3. avoid changing unrelated code;
4. preserve fail-closed behavior when evidence is insufficient;
5. keep examples synthetic and non-sensitive;
6. keep CI green across the supported Python matrix.

## Sensitive information

Do not post credentials, cookies, raw authorization headers, private URLs or IPs, internal hostnames, production logs, HAR/PCAP captures, customer data, or private infrastructure details.

See [`SECURITY.md`](SECURITY.md) for the repository security boundary.
