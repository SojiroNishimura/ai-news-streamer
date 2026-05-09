# AI News Streamer

Hacker NewsとAI系RSSフィードから記事を収集し、Claude Haiku APIで要約してSlackに投稿するPythonパイプライン。

## 動作フロー

```
[Hacker News Top100]  [TechCrunch / VentureBeat / The Verge / OpenAI]  [Anthropic]
        ↓                          ↓                                            ↓
   AIキーワードフィルタ          RSS最新20件/フィード                      HTMLスクレイプ
        └──────────────────────┬─────────────────────────────────────────────┘
                   ↓
          Claude Haiku API (全記事を1リクエストで要約)
                   ↓
          重要度★4以上のみ抽出
                   ↓
            Slack Webhook 投稿
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して2つの値を設定する。

```
ANTHROPIC_API_KEY=sk-ant-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
```

**Anthropic APIキーの取得**: https://console.anthropic.com/  
**Slack Webhook URLの取得**: Slack → App管理 → Incoming Webhooks

### 3. 実行

```bash
python main.py
```

## Slack投稿フォーマット

```
🤖 AI News Digest — 2026-05-08
重要度★4以上: 3件

★★★★★ GPT-5がリリース
　OpenAIが次世代モデルを突然発表し業界に衝撃。
　https://... (OpenAI Blog)

★★★★☆ AppleがCore MLを強化
　iOS向けオンデバイスLLM推論が大幅に改善。
　https://... (TechCrunch AI)
```

## ソース設定

### Hacker News (`src/fetchers/hackernews.py`)

Top100件からAI関連をキーワードフィルタで抽出。対象キーワード:

```
ai, llm, gpt, claude, ml, model, agent, openai, anthropic,
gemini, mistral, llama, transformer, neural, diffusion,
embedding, inference, fine-tun, machine learning, deep learning, generative
```

### RSSフィード (`src/fetchers/rss.py`)

| ソース | 取得方法 | 件数/回 |
|---|---|---|
| TechCrunch AI | RSS | 最新20件 |
| VentureBeat AI | RSS | 最新20件 |
| The Verge AI | RSS | 最新20件 |
| OpenAI | RSS | 最新20件 |
| Anthropic | HTMLスクレイプ | フィーチャー3〜5件 |

RSSフィードの追加・削除は `RSS_FEEDS` リストを編集する。

> **Anthropicについて**: 公式RSSフィードが存在しないため、トップページの静的HTMLからフィーチャー記事を抽出している。JSレンダリングされる記事は対象外。

## カスタマイズ

### 重要度の閾値を変更 (`main.py:24`)

```python
# ★3以上に下げる場合
high_priority = [a for a in summarized if a.importance >= 3]
```

### 要約の観点を変更 (`src/summarizer.py`)

`SYSTEM_PROMPT` の「iOSエンジニア視点」の部分を書き換えると、重要度の評価軸が変わる。

## コスト目安

1日1回実行した場合のClaude Haiku APIコスト:

| 条件 | トークン数 | 料金目安 |
|---|---|---|
| 記事30〜60件 | input ~2,000 / output ~3,000 | $0.001〜$0.002/回 |

全記事を1リクエストにバッチ処理しているため、記事ごとに個別呼び出しするより約80%コスト削減。

## ファイル構成

```
ai-news-streamer/
├── main.py                      # エントリーポイント
├── requirements.txt
├── .env.example                 # 環境変数テンプレート
└── src/
    ├── fetchers/
    │   ├── hackernews.py        # HN API (非同期並列取得 + フィルタ)
    │   └── rss.py               # RSS取得 (feedparser)
    ├── summarizer.py            # Claude Haiku APIバッチ要約
    └── slack_notifier.py        # Slack Webhook投稿
```
