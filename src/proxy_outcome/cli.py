from __future__ import annotations

import argparse
import json

from .classifier import classify


def _headers(values: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in values or []:
        if ":" not in item:
            # Do not echo the malformed value: CLI input may contain sensitive
            # material and error output can end up in shell/CI logs.
            raise SystemExit("invalid --header value; expected 'Name: Value'")
        key, value = item.split(":", 1)
        out[key.strip()] = value.strip()
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proxy-outcome",
        description="Classify HTTP/proxy observations without inventing endpoint-health evidence.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    classify_cmd = sub.add_parser("classify", help="classify one retrieval observation")
    classify_cmd.add_argument("--status", type=int, dest="status_code")
    classify_cmd.add_argument("--error", help="sanitized error label/message; do not pass secrets")
    classify_cmd.add_argument("--body-hint", help="sanitized hint only; do not pass response bodies or secrets")
    classify_cmd.add_argument(
        "--header",
        action="append",
        help="sanitized response header as 'Name: Value'; may be repeated",
    )
    classify_cmd.add_argument(
        "--endpoint-probe-failed",
        action="store_true",
        help="assert that an independent dedicated proxy endpoint health probe failed",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "classify":
        result = classify(
            status_code=args.status_code,
            error=args.error,
            body_hint=args.body_hint,
            headers=_headers(args.header),
            endpoint_probe_failed=args.endpoint_probe_failed,
        )
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
