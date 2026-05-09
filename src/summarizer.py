from __future__ import annotations

import json
import anthropic
from dataclasses import dataclass
from .fetchers.hackernews import Article

SYSTEM_PROMPT = """\
あなたはiOSエンジニア向けのAIニュースキュレーターです。
記事リストを受け取り、全記事をまとめて以下のJSON配列形式で返してください。

[
  {
    "index": <入力と同じ0始まりの整数>,
    "importance": <1〜5の整数 (iOSエンジニア視点での重要度)>,
    "summary": "<20字以内の一言サマリー>",
    "reason": "<なぜ今話題か1文>"
  },
  ...
]

JSON配列のみ返してください。説明文・コードブロック記号は不要です。"""


@dataclass
class SummarizedArticle:
    article: Article
    importance: int
    summary: str
    reason: str


def summarize_articles(articles: list[Article]) -> list[SummarizedArticle]:
    if not articles:
        return []

    client = anthropic.Anthropic()

    lines = [
        f"{i}. タイトル: {a.title} | ソース: {a.source}"
        for i, a in enumerate(articles)
    ]
    user_message = "以下の記事を評価・要約してください。\n\n" + "\n".join(lines)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    # コードブロックで囲まれていた場合に除去
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data_list: list[dict] = json.loads(raw)
    except json.JSONDecodeError:
        return []

    results = []
    for data in data_list:
        try:
            idx = int(data["index"])
            if idx < 0 or idx >= len(articles):
                continue
            results.append(SummarizedArticle(
                article=articles[idx],
                importance=int(data["importance"]),
                summary=data["summary"],
                reason=data["reason"],
            ))
        except (KeyError, ValueError, TypeError):
            continue

    return results
