import argparse
import sys


DEFAULT_SERVER = "http://127.0.0.1:18080"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ffmpeg-remote",
        description="CLI client for the ffmpeg client/server project (Phase 0 scaffold).",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER,
        help=f"Server base URL (default: {DEFAULT_SERVER})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ping", help="Check server health endpoint")
    subparsers.add_parser("submit", help="Placeholder for future job submission")

    return parser


def cmd_ping(server: str) -> int:
    try:
        import requests
    except ImportError:
        print(
            "Missing dependency: requests. Install with: python -m pip install -r client/requirements.txt",
            file=sys.stderr,
        )
        return 1

    url = f"{server.rstrip('/')}/health"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Ping failed: {exc}", file=sys.stderr)
        return 1

    print(response.json())
    return 0


def cmd_submit() -> int:
    print("Submit command is not implemented yet (Phase 0 scaffold).")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ping":
        return cmd_ping(args.server)

    if args.command == "submit":
        return cmd_submit()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
