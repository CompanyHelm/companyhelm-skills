---
name: video-upload
description: Upload a local demo video to Streamable with a single script call and use the returned link in a PR or task. Use when a user wants the fastest no-key hosted video flow from the CLI.
---

# Video Upload

Use the script. It handles the full Streamable guest upload flow.

```bash
python3 scripts/upload_streamable.py /absolute/path/to/video.webm
```

- Add `--title "demo name"` to override the page title.
- Add `--json` if a caller needs structured output.
- The script prints the Streamable URL by default.
- Streamable guest uploads are public URLs, not private or password-protected.
