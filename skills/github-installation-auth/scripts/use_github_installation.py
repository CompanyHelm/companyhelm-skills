#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_AGENT_CONFIG_PATH = Path.home() / ".config" / "companyhelm-agent-cli" / "config.json"


class AgentApiError(RuntimeError):
    pass


def resolve_agent_config() -> tuple[str, str]:
    api_url_override = os.environ.get("COMPANYHELM_AGENT_API_URL", "").strip()
    token_override = os.environ.get("COMPANYHELM_AGENT_TOKEN", "").strip()
    if api_url_override and token_override:
        return api_url_override.rstrip("/"), token_override

    config_path = Path(os.environ.get("COMPANYHELM_AGENT_CONFIG_PATH", str(DEFAULT_AGENT_CONFIG_PATH))).expanduser()
    if not config_path.exists():
        raise AgentApiError(f"agent config not found: {config_path}")

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    api_url = str(payload.get("agent_api_url") or "").strip().rstrip("/")
    token = str(payload.get("token") or "").strip()
    if not api_url:
        raise AgentApiError(f"agent config is missing 'agent_api_url': {config_path}")
    if not token:
        raise AgentApiError(f"agent config is missing 'token': {config_path}")
    return api_url, token


def agent_request(method: str, path: str) -> Any:
    api_url, token = resolve_agent_config()
    request = urllib.request.Request(
        url=f"{api_url}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    if method.upper() == "POST":
        request.add_header("Content-Type", "application/json")
        body = b"{}"
    else:
        body = None

    try:
        with urllib.request.urlopen(request, data=body) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(response_body)
            error = parsed.get("error") or {}
            code = str(error.get("code") or exc.code)
            message = str(error.get("message") or response_body or exc.reason)
            raise AgentApiError(f"{code}: {message}") from exc
        except json.JSONDecodeError:
            raise AgentApiError(f"HTTP {exc.code}: {response_body or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise AgentApiError(f"failed to reach agent API: {exc.reason}") from exc


def configure_git_helper(gh_path: str, host: str) -> None:
    helper = f"!{gh_path} auth git-credential"
    helper_key = f"credential.{host}.helper"
    subprocess.run(["git", "config", "--global", "--replace-all", helper_key, ""], check=True)
    subprocess.run(["git", "config", "--global", "--add", helper_key, helper], check=True)


def configure_installation_auth(installation_id: str) -> dict[str, Any]:
    payload = agent_request("POST", f"/github/installations/{installation_id}/access-token")
    access_token = str(payload.get("accessToken") or "").strip()
    if not access_token:
        raise AgentApiError(f"installation {installation_id} returned an empty access token")

    gh_path = shutil.which("gh") or ""
    if not gh_path:
        raise AgentApiError("gh CLI is not available in PATH")

    subprocess.run(["gh", "auth", "logout", "--hostname", "github.com", "--yes"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["gh", "auth", "login", "--hostname", "github.com", "--with-token"], input=access_token, text=True, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["gh", "auth", "setup-git"], check=True, stdout=subprocess.DEVNULL)
    configure_git_helper(gh_path, "https://github.com")
    configure_git_helper(gh_path, "https://gist.github.com")
    return payload


def print_installations(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, indent=2))
        return

    installations = payload.get("installations") or []
    if not installations:
        print("No GitHub installations are available.")
        return

    for installation in installations:
        installation_id = str(installation.get("installationId") or "").strip()
        repositories = installation.get("repositories") or []
        print(f"Installation {installation_id}")
        if repositories:
            print("  Repositories:")
            for repository in repositories:
                print(f"    - {repository}")
        else:
            print("  Repositories: none")
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure GitHub installation auth from the CompanyHelm agent REST API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List GitHub installations visible to the current thread.")
    list_parser.add_argument("--json", action="store_true", help="Print raw JSON.")

    use_parser = subparsers.add_parser("use", help="Configure gh and git auth for a GitHub installation.")
    use_parser.add_argument("installation_id", help="GitHub installation id.")
    use_parser.add_argument("--json", action="store_true", help="Print the REST response as JSON after configuration.")
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        payload = agent_request("GET", "/github/installations")
        print_installations(payload, args.json)
        return 0

    payload = configure_installation_auth(args.installation_id)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        expiration = str(payload.get("accessTokenExpiration") or "unknown").strip()
        print(f"Configured gh auth for installation {args.installation_id} (token expires at {expiration}).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except AgentApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
