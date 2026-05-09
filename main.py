import asyncio
import os
from dotenv import load_dotenv

from src.fetchers.hackernews import fetch_hn_ai_articles
from src.fetchers.rss import fetch_rss_ai_articles
from src.summarizer import summarize_articles
from src.slack_notifier import post_to_slack

load_dotenv()


async def main() -> None:
    print("=== AI News Streamer ===")

    print("[1/3] 記事を収集中...")
    hn_articles = await fetch_hn_ai_articles()
    rss_articles = fetch_rss_ai_articles()
    all_articles = hn_articles + rss_articles
    print(f"  HN: {len(hn_articles)}件, RSS: {len(rss_articles)}件 → 計{len(all_articles)}件")

    print("[2/3] Claude Haikuで要約中...")
    summarized = summarize_articles(all_articles)
    high_priority = [a for a in summarized if a.importance >= 4]
    print(f"  要約完了: {len(summarized)}件 / 重要度★4以上: {len(high_priority)}件")

    print("[3/3] Slackに投稿中...")
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    post_to_slack(webhook_url, high_priority)


if __name__ == "__main__":
    asyncio.run(main())
