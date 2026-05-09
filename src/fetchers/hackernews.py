from __future__ import annotations

import asyncio
import httpx
from dataclasses import dataclass

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
TOP_N = 100
CONCURRENCY = 20

AI_KEYWORDS = {
    "ai", "llm", "gpt", "claude", "ml", "model", "agent", "agents",
    "openai", "anthropic", "gemini", "mistral", "llama", "transformer",
    "neural", "diffusion", "embedding", "inference", "fine-tun",
    "machine learning", "deep learning", "generative",
}


@dataclass
class Article:
    title: str
    url: str
    source: str = "Hacker News"


def _is_ai_related(title: str) -> bool:
    lower = title.lower()
    return any(kw in lower for kw in AI_KEYWORDS)


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    try:
        resp = await client.get(HN_ITEM_URL.format(item_id), timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


async def fetch_hn_ai_articles() -> list[Article]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(HN_TOP_STORIES_URL, timeout=10.0)
        resp.raise_for_status()
        top_ids: list[int] = resp.json()[:TOP_N]

        sem = asyncio.Semaphore(CONCURRENCY)

        async def fetch_with_sem(item_id: int) -> dict | None:
            async with sem:
                return await _fetch_item(client, item_id)

        items = await asyncio.gather(*[fetch_with_sem(i) for i in top_ids])

    articles = []
    for item in items:
        if not item:
            continue
        title = item.get("title", "")
        url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}"
        if _is_ai_related(title):
            articles.append(Article(title=title, url=url))

    return articles
