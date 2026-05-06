import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_reddit_rss.py"


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Python</title>
  <updated>2026-05-06T05:40:43+00:00</updated>
  <entry>
    <title>Hello Reddit</title>
    <id>t3_abc123</id>
    <updated>2026-05-06T05:00:00+00:00</updated>
    <published>2026-05-06T04:59:00+00:00</published>
    <link href="https://www.reddit.com/r/python/comments/abc123/hello_reddit/" />
    <author>
      <name>/u/example</name>
      <uri>https://www.reddit.com/user/example</uri>
    </author>
    <category term="Python" label="r/Python"/>
    <content type="html"><![CDATA[<div class="md"><p>Hello <strong>world</strong>.</p><p>Second line.</p></div>]]></content>
  </entry>
</feed>
"""


def load_module():
    spec = importlib.util.spec_from_file_location("fetch_reddit_rss", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RedditRssFetchSkillScriptTest(unittest.TestCase):
    def test_normalize_subreddit_shorthand(self):
        module = load_module()
        self.assertEqual(
            module.normalize_target_to_rss_url("r/python"),
            "https://www.reddit.com/r/python/.rss",
        )

    def test_normalize_user_url(self):
        module = load_module()
        self.assertEqual(
            module.normalize_target_to_rss_url("https://old.reddit.com/user/spez/"),
            "https://www.reddit.com/user/spez/.rss",
        )

    def test_normalize_post_url_to_comments_feed(self):
        module = load_module()
        self.assertEqual(
            module.normalize_target_to_rss_url(
                "https://www.reddit.com/r/python/comments/1t3x7ba/whos_going_to_pycon_us_next_week/"
            ),
            "https://www.reddit.com/comments/1t3x7ba/.rss",
        )

    def test_normalize_search_target(self):
        module = load_module()
        self.assertEqual(
            module.normalize_target_to_rss_url("python packaging", search=True),
            "https://www.reddit.com/search.rss?q=python+packaging",
        )

    def test_html_to_text_strips_tags_and_unescapes(self):
        module = load_module()
        self.assertEqual(
            module.html_to_text("<p>Hello &amp; goodbye<br/>world</p>"),
            "Hello & goodbye world",
        )

    def test_parse_feed_extracts_entries(self):
        module = load_module()
        feed = module.parse_feed(SAMPLE_FEED, source_url="https://www.reddit.com/r/python/.rss")
        self.assertEqual(feed["title"], "Python")
        self.assertEqual(feed["item_count"], 1)
        self.assertEqual(feed["items"][0]["author"]["name"], "/u/example")
        self.assertEqual(feed["items"][0]["categories"], ["r/Python"])
        self.assertEqual(feed["items"][0]["snippet"], "Hello world. Second line.")

    def test_render_markdown_includes_source_and_snippet(self):
        module = load_module()
        feed = module.parse_feed(SAMPLE_FEED, source_url="https://www.reddit.com/r/python/.rss")
        markdown = module.render_markdown(feed, limit=1)
        self.assertIn("Source: https://www.reddit.com/r/python/.rss", markdown)
        self.assertIn("[Hello Reddit](https://www.reddit.com/r/python/comments/abc123/hello_reddit/)", markdown)
        self.assertIn("Hello world. Second line.", markdown)


if __name__ == "__main__":
    unittest.main()
