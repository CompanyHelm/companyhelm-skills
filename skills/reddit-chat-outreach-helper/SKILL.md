---
name: reddit-chat-outreach-helper
description: Resolve Reddit chat targets through about.json and send chat messages with structured verification before writing outreach state back to Notion.
---

# Reddit Chat Outreach Helper

Use this skill for Reddit outreach runs when you need a more reliable send/verify flow than ad-hoc browser clicks.

## What this skill standardizes

- prefer `about.json` over profile UI scraping to resolve a Reddit chat target
- return structured outcomes: `sent`, `no_chat`, `blocked`, or `failed`
- distinguish captcha / human verification from ordinary send failures
- verify sends with evidence instead of assuming the chat composer succeeded

## Preconditions

- Reddit navigation must already be happening through the proxied browser session
- the browser should already be authenticated to Reddit if chat requires login
- a Chrome or Chromium session with remote debugging enabled must be reachable at `http://127.0.0.1:9222` unless you override `--cdp-url`

## 1) Resolve a chat target from `about.json`

```bash
node scripts/resolve_chat_target.mjs --username Embarrassed-Ad5546 --json
```

This opens `https://www.reddit.com/user/<username>/about.json` in the active proxied browser session, reads `data.id`, prefixes it as `t2_<id>`, and returns the canonical Reddit chat URL. `data.name` is only display metadata and must not be used as the chat target.

## 2) Send a message with structured verification

```bash
cat > /tmp/outreach.txt <<'EOF_MSG'
hey, saw your post about keeping several Claude Code sessions running across projects and checking them from mobile/iPad while the work stays on your own machines. i've been building CompanyHelm to help with remote coding-agent control and visibility into parallel sessions. if you're interested, happy to share more. appreciate your time.
EOF_MSG

node scripts/send_chat.mjs \
  --chat-url "https://chat.reddit.com/user/t2_exampleid" \
  --message-file /tmp/outreach.txt \
  --json
```

## Outcome handling

- `sent`: update Notion to `sent` and store the returned `chatUrl`
- `no_chat`: mark `no chat available` with the exact returned reason
- `blocked`: pause outreach and ask a human to resolve the captcha / human verification gate
- `failed`: record the returned reason and decide whether one low-risk retry is warranted

## Suggested verification policy

Treat the send as successful only when at least one of these is true:

- the exact outbound message text appears in the thread
- the composer clears after clicking Reddit chat’s `Send message` button and the page is still open on the intended direct-chat URL or room
- the helper returns `sent` with a concrete `verificationMethod`

If the helper returns `blocked`, do not keep retrying the same flow.

## Implementation notes

- Reddit `about.json` returns a display username in `data.name` and the chat target id in `data.id`. Always build chat URLs as `https://chat.reddit.com/user/t2_<data.id>`.
- The chat composer is a textarea with `aria-label="Write message"`; after filling it, wait for `button[aria-label="Send message"]` to become enabled before clicking.
- If the exact message is not visible after send, only treat composer clearing as positive evidence when the final URL is the intended `/chat/user/t2_...` target or a Reddit direct-chat room redirect.
