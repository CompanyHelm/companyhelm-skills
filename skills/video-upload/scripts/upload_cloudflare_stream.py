#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local video file to Cloudflare Stream via direct creator upload.",
    )
    parser.add_argument("--api-token", required=True, help="Cloudflare API token with Stream access.")
    parser.add_argument("--account-id", required=True, help="Cloudflare account id.")
    parser.add_argument("--video-path", required=True, help="Local path to the video file.")
    parser.add_argument("--name", help="Stream video name. Defaults to the input file name.")
    parser.add_argument("--max-duration-seconds", type=int, default=3600, help="Max duration for direct upload.")
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0, help="Readiness polling interval.")
    parser.add_argument("--timeout-seconds", type=float, default=180.0, help="Readiness polling timeout.")
    parser.add_argument("--json", action="store_true", help="Print the final result as JSON.")
    return parser.parse_args()


def request_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc


def upload_file(upload_url: str, video_path: str) -> None:
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            "-F",
            f"file=@{video_path}",
            upload_url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"curl upload failed with exit code {result.returncode}: {result.stderr.strip() or result.stdout.strip()}",
        )


def ensure_success(response: dict, context: str) -> dict:
    if response.get("success") is True and response.get("result") is not None:
        return response["result"]
    raise RuntimeError(f"{context} failed: {json.dumps(response)}")


def poll_until_ready(token: str, account_id: str, video_uid: str, interval: float, timeout: float) -> dict:
    deadline = time.monotonic() + timeout
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/stream/{video_uid}"

    while True:
        response = request_json("GET", url, token)
        result = ensure_success(response, "Video status lookup")
        if result.get("readyToStream") is True:
            return result
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Timed out waiting for Cloudflare Stream video {video_uid} to become ready.",
            )
        time.sleep(interval)


def main() -> int:
    args = parse_args()

    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        raise RuntimeError(f"Video file not found: {video_path}")

    video_name = args.name or os.path.basename(video_path)
    create_response = request_json(
        "POST",
        f"https://api.cloudflare.com/client/v4/accounts/{args.account_id}/stream/direct_upload",
        args.api_token,
        {
            "maxDurationSeconds": args.max_duration_seconds,
            "meta": {"name": video_name},
        },
    )
    create_result = ensure_success(create_response, "Direct upload creation")

    upload_url = create_result["uploadURL"]
    video_uid = create_result["uid"]
    upload_file(upload_url, video_path)

    final_result = poll_until_ready(
        args.api_token,
        args.account_id,
        video_uid,
        args.poll_interval_seconds,
        args.timeout_seconds,
    )

    output = {
        "uid": video_uid,
        "name": final_result.get("meta", {}).get("name", video_name),
        "watch_url": final_result.get("preview"),
        "thumbnail_url": final_result.get("thumbnail"),
        "duration_seconds": final_result.get("duration"),
        "ready_to_stream": final_result.get("readyToStream"),
    }

    if args.json:
        print(json.dumps(output))
    else:
        print(output["watch_url"])

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
