---
name: reddit-rss-fetch
description: Use when you need public Reddit posts, comments, subreddit listings, user activity, or search results without browser automation, login repair, or API credentials.
---

# Reddit RSS Fetch

Prefer Reddit's public RSS feeds before browser automation or API work.

Use the bundled script for public subreddit feeds, user feeds, comment threads, and search results.

```bash
python3 scripts/fetch_reddit_rss.py r/python --limit 5
```

## Common targets

```bash
# subreddit feed
python3 scripts/fetch_reddit_rss.py r/python --limit 5

# user feed
python3 scripts/fetch_reddit_rss.py u/spez --limit 5

# comment thread feed from a post URL
python3 scripts/fetch_reddit_rss.py https://www.reddit.com/r/python/comments/1t3x7ba/whos_going_to_pycon_us_next_week/ --limit 10

# search feed
python3 scripts/fetch_reddit_rss.py "python packaging" --search --limit 5
```

## Output modes

Print markdown by default:

```bash
python3 scripts/fetch_reddit_rss.py r/python --limit 3
```

Print structured JSON:

```bash
python3 scripts/fetch_reddit_rss.py r/python --limit 3 --json
```

## Notes

- Works for public Reddit content only.
- Prefer this path when the task is just fetching Reddit content, not interacting with Reddit.
- Post URLs are converted to the comments feed automatically through `/comments/<post_id>/.rss`.
- Search queries can be passed with `--search`, or use a Reddit search URL directly.
- If Reddit returns a 404 or a blocked feed, fall back to browser-based workflows only when RSS cannot answer the request.
