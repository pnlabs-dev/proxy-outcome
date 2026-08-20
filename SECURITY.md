# Security policy

`proxy-outcome` is designed to be safe to inspect and embed: the package performs local classification only and has no runtime dependencies, network I/O, telemetry, persistence, or credential storage.

## Never publish sensitive material

Do not put any of the following in issues, pull requests, examples, fixtures, benchmark artifacts, screenshots, or CI logs:

- API keys, access tokens, passwords, or private keys;
- proxy usernames/passwords or credential-bearing proxy URLs;
- session cookies, authorization headers, or authenticated request dumps;
- private endpoint URLs, private IP addresses, internal hostnames, or infrastructure topology;
- production HAR/PCAP captures or raw production logs;
- private datasets or personal data;
- non-public commercial implementation details.

Use synthetic placeholders and aggregate counts instead.

## CLI caution

Command-line arguments may be recorded in shell history or visible to local process inspection. Do not pass real secrets through `--header`, `--body-hint`, or `--error`. Use sanitized labels only.

## Output behavior

The classifier returns normalized evidence labels. It does not intentionally echo raw header values, body hints, or error strings into `Classification.evidence`.

The test suite includes a regression test that verifies a supplied sensitive header value is not emitted in serialized classifier output.

## Repository hygiene gate

CI runs `scripts/public_hygiene_check.py`. The checker searches public text files for common secret/token shapes, credential-bearing URLs, private IPv4 literals, sensitive filenames, and email addresses.

If it detects a problem, it reports only the rule and file path. **Matched values are never printed**, so CI logs do not become a secondary disclosure channel.

This check is defense-in-depth, not a substitute for review or dedicated secret-scanning controls.

## Reporting a security issue

Do not open a public issue containing security-sensitive material. Use the private/public contact channel provided by the PN Labs GitHub profile and share the minimum information needed to reproduce the issue.

Before sharing any reproduction, sanitize URLs, headers, identifiers, logs, and payloads.
