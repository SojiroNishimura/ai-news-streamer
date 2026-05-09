import httpx
from datetime import date
from .summarizer import SummarizedArticle

STARS = {1: "★☆☆☆☆", 2: "★★☆☆☆", 3: "★★★☆☆", 4: "★★★★☆", 5: "★★★★★"}
TOP_N = 5


def _format_message(
    high_priority: list[SummarizedArticle],
    all_summarized: list[SummarizedArticle],
) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [
        f"*🤖 AI News Digest — {today}*",
        f"収集: {len(all_summarized)}件 / 重要度★4以上: {len(high_priority)}件\n",
    ]

    if high_priority:
        lines.append("*📌 注目記事 (★4以上)*")
        for a in sorted(high_priority, key=lambda x: x.importance, reverse=True):
            stars = STARS.get(a.importance, "★" * a.importance)
            lines.append(
                f"{stars} *{a.summary}*\n"
                f"　{a.reason}\n"
                f"　<{a.article.url}|{a.article.title}> _{a.article.source}_"
            )
        lines.append("")

    top5 = sorted(all_summarized, key=lambda x: x.importance, reverse=True)[:TOP_N]
    lines.append(f"*📊 スコア上位{TOP_N}件*")
    for a in top5:
        stars = STARS.get(a.importance, "★" * a.importance)
        lines.append(f"{stars} <{a.article.url}|{a.article.title}> _{a.article.source}_")

    return "\n".join(lines)


def post_to_slack(
    webhook_url: str,
    high_priority: list[SummarizedArticle],
    all_summarized: list[SummarizedArticle],
) -> None:
    text = _format_message(high_priority, all_summarized)
    resp = httpx.post(webhook_url, json={"text": text}, timeout=10.0)
    resp.raise_for_status()
    print(f"Slack投稿完了 (★4以上: {len(high_priority)}件 / 上位{TOP_N}件掲載)")
