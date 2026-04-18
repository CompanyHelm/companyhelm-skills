---
name: temp-sh-image-upload
description: Upload a local image to temp.sh and print a shareable URL or markdown snippet for PR comments and descriptions.
---

# temp.sh Image Upload

Use the bundled script to upload a local image to temp.sh.

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png
```

By default, the script prints the uploaded temp.sh URL.

## Comment on a PR with a screenshot

This mirrors the raw curl flow:

```bash
url="$(python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png)"
gh pr comment "$PR_NUMBER" --body "![screenshot]($url)"
```

## Add a screenshot to a PR description

```bash
existing_body="$(gh pr view "$PR_NUMBER" --json body --jq .body)"
markdown="$(python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --markdown --alt screenshot)"
gh pr edit "$PR_NUMBER" --body "${existing_body}

${markdown}"
```

## Print markdown directly

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --markdown --alt screenshot
```

## Comment on a PR directly from the script

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --comment-pr "$PR_NUMBER" --alt screenshot
```

If you are not running inside the target repository, add `--repo owner/name`.

## Structured output

```bash
python3 scripts/upload_temp_sh.py /absolute/path/to/screenshot.png --json --alt screenshot
```

## Notes

- temp.sh links are public and temporary.
- The script validates that the file looks like an image unless `--allow-non-image` is passed.
- `gh` is only required when using `--comment-pr`.
