#!/usr/bin/env python3
import argparse
import json
import mimetypes
import subprocess
import sys
from pathlib import Path


TEMP_SH_UPLOAD_URL = "https://temp.sh/upload"


def validate_file(file_path: Path, allow_non_image: bool) -> None:
    if not file_path.is_file():
        raise RuntimeError(f"file not found: {file_path}")

    content_type, _encoding = mimetypes.guess_type(file_path.name)
    if not allow_non_image and (not content_type or not content_type.startswith("image/")):
        raise RuntimeError(
            "file does not look like an image based on its extension; pass --allow-non-image to override"
        )


def run(command: list[str], stdin_text: str | None = None) -> str:
    result = subprocess.run(
        command,
        input=stdin_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise RuntimeError(detail)
    return result.stdout


def upload_file(file_path: Path) -> str:
    output = run([
        "curl",
        "--fail-with-body",
        "-sS",
        "-F",
        f"file=@{file_path}",
        TEMP_SH_UPLOAD_URL,
    ])
    url = output.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise RuntimeError(f"unexpected temp.sh response: {output[:500]}")
    return url


def build_markdown(url: str, alt: str) -> str:
    return f"![{alt}]({url})"


def comment_on_pr(pr_number: str, body: str, repo: str | None) -> None:
    command = ["gh", "pr", "comment", pr_number]
    if repo:
        command.extend(["--repo", repo])
    command.extend(["--body", body])
    run(command)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a local image to temp.sh.")
    parser.add_argument("file_path", nargs="?", help="Path to the image file.")
    parser.add_argument("--file-path", dest="file_path_flag", help="Path to the image file.")
    parser.add_argument("--alt", default="screenshot", help="Alt text used for markdown output.")
    parser.add_argument("--markdown", action="store_true", help="Print markdown instead of the raw URL.")
    parser.add_argument("--comment-pr", help="PR number to comment on with the uploaded screenshot markdown.")
    parser.add_argument("--repo", help="Optional owner/name repo for gh pr comment.")
    parser.add_argument("--allow-non-image", action="store_true", help="Allow uploading non-image files.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    args = parser.parse_args(argv)
    args.file_path = args.file_path_flag or args.file_path
    if not args.file_path:
        parser.error("a file path is required")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    file_path = Path(args.file_path).expanduser().resolve()
    validate_file(file_path, allow_non_image=args.allow_non_image)
    url = upload_file(file_path)
    markdown = build_markdown(url, args.alt)

    if args.comment_pr:
        comment_on_pr(args.comment_pr, markdown, args.repo)

    if args.json:
        print(json.dumps({
            "file_path": str(file_path),
            "url": url,
            "markdown": markdown,
            "commented_pr": args.comment_pr,
            "repo": args.repo,
        }, indent=2))
    elif args.markdown or args.comment_pr:
        print(markdown)
    else:
        print(url)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
