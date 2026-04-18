---
name: temp-sh-image-upload
description: Upload a local image to temp.sh and print a shareable URL or markdown snippet for screenshots, docs, chat, and PRs.
---

# temp.sh Image Upload

Use the bundled script to upload a local image to temp.sh.

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png
```

By default, the script prints the uploaded temp.sh URL.

## Common use cases

- Attach a screenshot to a pull request description or comment.
- Paste a temporary image URL into team chat or tickets.
- Embed markdown into docs, notes, or issue reports.

The skill just uploads the file and returns a URL or markdown snippet so the caller can use it however they want.

## Print markdown directly

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --markdown --alt screenshot
```

## Structured output

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --json --alt screenshot
```

## Notes

- temp.sh links are public and temporary.
- The script validates that the file looks like an image unless `--allow-non-image` is passed.
