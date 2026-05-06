#!/usr/bin/env python3
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
DEFAULT_USER_AGENT = "CompanyHelmRedditRSS/1.0"
DEFAULT_LIMIT = 10


def normalize_target_to_rss_url(target: str, *, search: bool = False, sort: str | None = None) -> str:
    target = target.strip()
    if not target:
        raise RuntimeError("target is required")

    if search:
        return build_search_rss_url(target, sort=sort)

    if target.startswith(("r/", "/r/")):
        subreddit = target.split("/r/", 1)[-1] if "/r/" in target else target[2:]
        subreddit = subreddit.strip("/")
        if not subreddit:
            raise RuntimeError("subreddit target is missing a name")
        return add_query_params(f"https://www.reddit.com/r/{subreddit}/.rss", sort=sort)

    if target.startswith(("u/", "/u/", "user/", "/user/")):
        username = extract_username_from_shorthand(target)
        return add_query_params(f"https://www.reddit.com/user/{username}/.rss", sort=sort)

    parsed = urllib.parse.urlparse(target)
    if parsed.scheme and parsed.netloc:
        return normalize_reddit_url_to_rss(parsed, sort=sort)

    raise RuntimeError(
        "unsupported target; use r/<subreddit>, u/<username>, a Reddit URL, or pass --search for search queries"
    )


def extract_username_from_shorthand(target: str) -> str:
    cleaned = target.strip("/")
    for prefix in ("u/", "user/"):
        if cleaned.startswith(prefix):
            username = cleaned[len(prefix):].strip("/")
            if username:
                return username
    raise RuntimeError("user target is missing a username")


def build_search_rss_url(query: str, *, sort: str | None = None) -> str:
    params = {"q": query}
    if sort:
        params["sort"] = sort
    return f"https://www.reddit.com/search.rss?{urllib.parse.urlencode(params)}"


def normalize_reddit_url_to_rss(parsed: urllib.parse.ParseResult, *, sort: str | None = None) -> str:
    host = parsed.netloc.lower()
    if host not in {"reddit.com", "www.reddit.com", "old.reddit.com", "np.reddit.com"}:
        raise RuntimeError(f"unsupported host for Reddit RSS fetch: {parsed.netloc}")

    path = parsed.path or "/"
    stripped_path = path.rstrip("/")

    if stripped_path.endswith(".rss"):
        return add_query_params(
            f"https://www.reddit.com{stripped_path}",
            existing_query=parsed.query,
            sort=sort,
        )

    segments = [segment for segment in path.split("/") if segment]

    if segments[:1] == ["search"]:
        query_params = urllib.parse.parse_qs(parsed.query)
        query = first_query_value(query_params, "q")
        if not query:
            raise RuntimeError("Reddit search URL is missing the q query parameter")
        preserved_sort = sort or first_query_value(query_params, "sort")
        return build_search_rss_url(query, sort=preserved_sort)

    if len(segments) >= 2 and segments[0] in {"u", "user"}:
        return add_query_params(f"https://www.reddit.com/user/{segments[1]}/.rss", sort=sort)

    if len(segments) >= 2 and segments[0] == "r":
        subreddit = segments[1]
        if len(segments) >= 4 and segments[2] == "comments":
            post_id = segments[3]
            return add_query_params(f"https://www.reddit.com/comments/{post_id}/.rss", sort=sort)
        return add_query_params(f"https://www.reddit.com/r/{subreddit}/.rss", sort=sort)

    if len(segments) >= 2 and segments[0] == "comments":
        post_id = segments[1]
        return add_query_params(f"https://www.reddit.com/comments/{post_id}/.rss", sort=sort)

    raise RuntimeError(f"unsupported Reddit URL path for RSS conversion: {parsed.path}")


def first_query_value(query_params: dict[str, list[str]], key: str) -> str | None:
    values = query_params.get(key)
    if not values:
        return None
    return values[0]


def add_query_params(base_url: str, *, existing_query: str | None = None, sort: str | None = None) -> str:
    parsed = urllib.parse.urlparse(base_url)
    query_params = urllib.parse.parse_qs(existing_query or parsed.query)
    if sort:
        query_params["sort"] = [sort]
    encoded_query = urllib.parse.urlencode(query_params, doseq=True)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", encoded_query, ""))


def fetch_feed_xml(rss_url: str, *, timeout_seconds: int = 20) -> str:
    request = urllib.request.Request(
        rss_url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Reddit RSS request failed with HTTP {exc.code} for {rss_url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Reddit RSS request failed for {rss_url}: {exc.reason}") from exc


def parse_feed(xml_text: str, *, source_url: str) -> dict:
    root = ET.fromstring(xml_text)
    title = root.findtext("atom:title", default="", namespaces=ATOM_NS).strip()
    updated = root.findtext("atom:updated", default="", namespaces=ATOM_NS).strip()
    entries = []

    for entry in root.findall("atom:entry", ATOM_NS):
        entries.append(parse_entry(entry))

    return {
        "source_url": source_url,
        "title": title,
        "updated": updated,
        "item_count": len(entries),
        "items": entries,
    }


def parse_entry(entry: ET.Element) -> dict:
    title = entry.findtext("atom:title", default="", namespaces=ATOM_NS).strip()
    item_id = entry.findtext("atom:id", default="", namespaces=ATOM_NS).strip()
    updated = entry.findtext("atom:updated", default="", namespaces=ATOM_NS).strip()
    published = entry.findtext("atom:published", default="", namespaces=ATOM_NS).strip()
    author_name = entry.findtext("atom:author/atom:name", default="", namespaces=ATOM_NS).strip()
    author_url = entry.findtext("atom:author/atom:uri", default="", namespaces=ATOM_NS).strip()

    link = ""
    for link_element in entry.findall("atom:link", ATOM_NS):
        href = link_element.attrib.get("href", "").strip()
        if href:
            link = href
            break

    content = entry.findtext("atom:content", default="", namespaces=ATOM_NS)
    summary = entry.findtext("atom:summary", default="", namespaces=ATOM_NS)
    snippet = html_to_text(content or summary or "")

    categories = []
    for category in entry.findall("atom:category", ATOM_NS):
        label = category.attrib.get("label") or category.attrib.get("term")
        if label:
            categories.append(label)

    return {
        "title": title,
        "id": item_id,
        "link": link,
        "updated": updated,
        "published": published,
        "author": {
            "name": author_name,
            "url": author_url,
        },
        "categories": categories,
        "snippet": snippet,
    }


def html_to_text(value: str) -> str:
    value = value.replace("<br/>", "\n").replace("<br />", "\n").replace("<br>", "\n")
    value = value.replace("</p>", "\n").replace("</div>", "\n")
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+([.,;:!?])", r"\1", value)
    return value.strip()


def render_markdown(feed: dict, *, limit: int) -> str:
    lines = [f"# {feed['title'] or 'Reddit RSS Feed'}", "", f"Source: {feed['source_url']}"]
    if feed.get("updated"):
        lines.append(f"Updated: {feed['updated']}")
    lines.append("")

    for item in feed["items"][:limit]:
        headline = item["title"] or item["id"] or "Untitled entry"
        line = f"- [{headline}]({item['link']})" if item["link"] else f"- {headline}"
        meta_parts = []
        if item["author"]["name"]:
            meta_parts.append(item["author"]["name"])
        if item["published"]:
            meta_parts.append(item["published"])
        elif item["updated"]:
            meta_parts.append(item["updated"])
        if meta_parts:
            line += " — " + " — ".join(meta_parts)
        lines.append(line)
        if item["snippet"]:
            lines.append(f"  {item['snippet']}")
        if item["categories"]:
            lines.append(f"  Categories: {', '.join(item['categories'])}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch public Reddit RSS feeds and normalize them.")
    parser.add_argument("target", help="Reddit target: r/<sub>, u/<user>, Reddit URL, or a search query with --search.")
    parser.add_argument("--search", action="store_true", help="Treat target as a Reddit search query.")
    parser.add_argument("--sort", help="Optional Reddit sort parameter to add to the RSS request.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Number of items to print (default: {DEFAULT_LIMIT}).")
    parser.add_argument("--json", action="store_true", help="Print structured JSON instead of markdown.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.limit <= 0:
        raise RuntimeError("--limit must be greater than 0")

    rss_url = normalize_target_to_rss_url(args.target, search=args.search, sort=args.sort)
    xml_text = fetch_feed_xml(rss_url)
    feed = parse_feed(xml_text, source_url=rss_url)

    if args.json:
        trimmed_feed = dict(feed)
        trimmed_feed["items"] = feed["items"][: args.limit]
        trimmed_feed["item_count"] = len(trimmed_feed["items"])
        print(json.dumps(trimmed_feed, indent=2))
    else:
        print(render_markdown(feed, limit=args.limit), end="")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
