import httpx
from datetime import date
from .summarizer import SummarizedArticle

STARS = {1: "★☆☆☆☆", 2: "★★☆☆☆", 3: "★★★☆☆", 4: "★★★★☆", 5: "★★★★★"}


def _format_message(articles: list[SummarizedArticle]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"*🤖 AI News Digest — {today}*", f"重要度★4以上: {len(articles)}件\n"]
    for a in sorted(articles, key=lambda x: x.importance, reverse=True):
        stars = STARS.get(a.importance, "★" * a.importance)
        lines.append(
            f"{stars} *{a.summary}*\n"
            f"　{a.reason}\n"
            f"　<{a.article.url}|{a.article.title}> _{a.article.source}_"
        )
    return "\n".join(lines)


def post_to_slack(webhook_url: str, articles: list[SummarizedArticle]) -> None:
    if not articles:
        print("投稿対象なし (重要度★4以上の記事がありませんでした)")
        return

    text = _format_message(articles)
    resp = httpx.post(webhook_url, json={"text": text}, timeout=10.0)
    resp.raise_for_status()
    print(f"Slack投稿完了 ({len(articles)}件)")
