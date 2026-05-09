from __future__ import annotations

import re
import feedparser
import httpx
from .hackernews import Article

RSS_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI",   "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("OpenAI",        "https://openai.com/news/rss.xml"),
]

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ai-news-streamer/1.0)"}


def _fetch_anthropic_articles() -> list[Article]:
    """Anthropicは公式RSSなし。トップページの静的HTMLからフィーチャー記事を抽出する。"""
    try:
        resp = httpx.get("https://www.anthropic.com/news", headers=_HEADERS, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return []

    articles = []
    seen: set[str] = set()
    blocks = re.findall(r'(<a href="/news/[a-z0-9][a-z0-9\-]+".*?</a>)', resp.text, re.DOTALL)
    for block in blocks:
        href = re.search(r'href="(/news/[^"]+)"', block)
        title_tag = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', block, re.DOTALL)
        if not (href and title_tag):
            continue
        path = href.group(1)
        title = re.sub(r"<[^>]+>", "", title_tag.group(1)).strip()
        if path in seen or not title or len(title) < 5:
            continue
        seen.add(path)
        articles.append(Article(
            title=title,
            url=f"https://www.anthropic.com{path}",
            source="Anthropic",
        ))
    return articles


def _is_valid_url(url: str) -> bool:
    return url.startswith("http") and "." in url.split("/")[2] if url else False


def fetch_rss_ai_articles() -> list[Article]:
    articles: list[Article] = []
    for source, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if title and _is_valid_url(link):
                articles.append(Article(title=title, url=link, source=source))

    articles.extend(_fetch_anthropic_articles())
    return articles
