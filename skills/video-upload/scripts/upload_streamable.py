#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode


class StreamableUploader:
    API_BASE = "https://api-f.streamable.com/api/v1"

    def __init__(
        self,
        video_path: str,
        title: str | None,
        upload_source: str,
        poll_interval_seconds: float,
        timeout_seconds: float,
        version: str,
    ) -> None:
        self.video_path = Path(video_path).resolve()
        self.title = title or self.video_path.stem
        self.upload_source = upload_source
        self.poll_interval_seconds = poll_interval_seconds
        self.timeout_seconds = timeout_seconds
        self.version = version
        self.cookie_jar = tempfile.NamedTemporaryFile(prefix="streamable-cookies-", suffix=".txt", delete=False)
        self.cookie_jar.close()

    def upload(self) -> dict:
        self._validate_video()
        metadata = self._mint_shortcode()
        shortcode = metadata["shortcode"]
        self._upload_to_s3(metadata)
        self._initialize_video(shortcode)
        self._track_complete(shortcode)
        self._start_transcode(shortcode, metadata)
        return self._wait_for_video(shortcode)

    def cleanup(self) -> None:
        try:
            os.unlink(self.cookie_jar.name)
        except FileNotFoundError:
            pass

    def _validate_video(self) -> None:
        if not self.video_path.is_file():
            raise RuntimeError(f"Video file not found: {self.video_path}")

    def _mint_shortcode(self) -> dict:
        params = urlencode(
            {
                "size": str(self.video_path.stat().st_size),
                "version": self.version,
            }
        )
        return self._curl_json(
            [
                "-c",
                self.cookie_jar.name,
                f"{self.API_BASE}/uploads/shortcode?{params}",
                "-H",
                "Pragma: no-cache",
                "-H",
                "Cache-Control: no-cache",
            ]
        )

    def _upload_to_s3(self, metadata: dict) -> None:
        content_type = mimetypes.guess_type(self.video_path.name)[0] or "application/octet-stream"
        command = [
            "curl",
            "--max-time",
            "120",
            "-sS",
            "-o",
            os.devnull,
            "-w",
            "%{http_code}",
            "-X",
            "POST",
            metadata["url"],
        ]
        for key, value in metadata["fields"].items():
            command.extend(["-F", f"{key}={value}"])
        command.extend(["-F", f"file=@{self.video_path};type={content_type}"])
        http_code = self._run(command).strip()
        if http_code not in {"201", "204"}:
            raise RuntimeError(f"Streamable S3 upload failed with HTTP {http_code}")

    def _initialize_video(self, shortcode: str) -> None:
        payload = {
            "original_size": self.video_path.stat().st_size,
            "original_name": self.video_path.name,
            "upload_source": self.upload_source,
            "title": self.title,
        }
        self._curl_text(
            [
                "-b",
                self.cookie_jar.name,
                "-H",
                "Content-Type: application/json",
                "-H",
                "Pragma: no-cache",
                "-H",
                "Cache-Control: no-cache",
                "--data",
                json.dumps(payload),
                f"{self.API_BASE}/videos/{shortcode}/initialize",
            ]
        )

    def _track_complete(self, shortcode: str) -> None:
        self._curl_text(
            [
                "-b",
                self.cookie_jar.name,
                "-H",
                "Content-Type: application/json",
                "-H",
                "Pragma: no-cache",
                "-H",
                "Cache-Control: no-cache",
                "--data",
                json.dumps({"event": "complete"}),
                f"{self.API_BASE}/uploads/{shortcode}/track",
            ]
        )

    def _start_transcode(self, shortcode: str, metadata: dict) -> None:
        payload = {
            **metadata.get("options", {}),
            **metadata.get("transcoder_options", {}),
        }
        self._curl_json(
            [
                "-b",
                self.cookie_jar.name,
                "-H",
                "Content-Type: application/json",
                "--data",
                json.dumps(payload),
                f"{self.API_BASE}/transcode/{shortcode}",
            ]
        )

    def _wait_for_video(self, shortcode: str) -> dict:
        deadline = time.monotonic() + self.timeout_seconds
        last_status = None
        while time.monotonic() < deadline:
            video = self._curl_json(
                [
                    "-b",
                    self.cookie_jar.name,
                    "-H",
                    "Pragma: no-cache",
                    "-H",
                    "Cache-Control: no-cache",
                    f"{self.API_BASE}/videos/{shortcode}",
                ]
            )
            last_status = video
            if video.get("error"):
                raise RuntimeError(f"Streamable transcode failed: {video['error']}")
            if video.get("status") == 2 and video.get("files"):
                return {
                    "shortcode": shortcode,
                    "title": video.get("title"),
                    "url": video.get("url"),
                    "thumbnail_url": video.get("thumbnail_url"),
                    "mp4_url": ((video.get("files") or {}).get("mp4") or {}).get("url"),
                    "status": video.get("status"),
                    "visibility": ((video.get("privacy_settings") or {}).get("visibility")),
                }
            time.sleep(self.poll_interval_seconds)
        raise RuntimeError(f"Timed out waiting for Streamable video to finish processing: {last_status}")

    def _curl_json(self, args: list[str]) -> dict:
        output = self._curl_text(args)
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Expected JSON from curl but got: {output[:500]}") from exc

    def _curl_text(self, args: list[str]) -> str:
        return self._run(["curl", "--max-time", "30", "--fail-with-body", "-sS", *args])

    def _run(self, command: list[str]) -> str:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command[:4])} ... {detail}")
        return result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a local video file to Streamable.")
    parser.add_argument("video_path", nargs="?", help="Local path to the video file.")
    parser.add_argument("--video-path", dest="video_path_flag", help="Local path to the video file.")
    parser.add_argument("--title", "--name", dest="title", help="Optional Streamable title. Defaults to the file stem.")
    parser.add_argument("--upload-source", default="desktop", help="Upload source label sent to Streamable.")
    parser.add_argument("--version", default="unknown", help="Client version sent when minting the upload.")
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0, help="Polling interval.")
    parser.add_argument("--timeout-seconds", type=float, default=120.0, help="Overall processing timeout.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON instead of just the URL.")
    args = parser.parse_args()
    args.video_path = args.video_path_flag or args.video_path
    if not args.video_path:
        parser.error("a video path is required")
    return args


def main() -> int:
    args = parse_args()
    uploader = StreamableUploader(
        video_path=args.video_path,
        title=args.title,
        upload_source=args.upload_source,
        poll_interval_seconds=args.poll_interval_seconds,
        timeout_seconds=args.timeout_seconds,
        version=args.version,
    )
    try:
        result = uploader.upload()
    finally:
        uploader.cleanup()

    if args.json:
        print(json.dumps(result))
    else:
        print(result["url"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
