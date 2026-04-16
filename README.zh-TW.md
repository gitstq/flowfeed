# FlowFeed 📡

<p align="center">
  <strong>輕量級智慧新聞聚合引擎</strong>
</p>
<p align="center">
  面向開發者的 CLI 優先工具，可從 16+ 個來源聚合、篩選和匯出熱門新聞 — 支援終端、JSON、Markdown、HTML 儀表板及 RSS 訂閱。
</p>

---

## ✨ 核心特性

- **16 個內建資料源** — 微博、知乎、百度、抖音、嗶哩嗶哩、HackerNews、GitHub Trending、ProductHunt、V2EX、少數派、澎湃新聞等
- **智慧去重** — 基於 MD5 指紋的跨源去重，保留最高分版本
- **綜合評分** — 歸一化熱度 + 排名加權，按相關性排序
- **關鍵字與正則過濾** — 包含/排除模式、分類篩選、最低分數閾值
- **5 種匯出格式** — 終端（Rich）、JSON、Markdown、HTML 儀表板、RSS 2.0
- **精美 HTML 儀表板** — 自包含深色主題 Web 報告，含統計與分組
- **非同步並行** — 可配置並行度的並發抓取
- **零重度依賴** — 僅需 httpx、rich、click、pyyaml、jinja2
- **高度可配置** — YAML 設定檔支援每個資料源的獨立配置

## 📡 資料源

| ID | 名稱 | 分類 | 說明 |
|---|---|---|---|
| `weibo` | 微博熱搜 | 社交 | 微博即時熱搜榜 |
| `zhihu` | 知乎熱榜 | 知識 | 知乎即時熱門問題榜 |
| `baidu` | 百度熱搜 | 綜合 | 百度即時熱搜榜 |
| `douyin` | 抖音熱搜 | 社交 | 抖音熱門影片 |
| `bilibili` | B站熱搜 | 社交 | B站熱門話題 |
| `hackernews` | Hacker News | 科技 | HN 熱門技術討論 |
| `github` | GitHub Trending | 科技 | GitHub 熱門開源專案 |
| `producthunt` | Product Hunt | 科技 | PH 每日熱門新產品 |
| `v2ex` | V2EX | 科技 | V2EX 創意工作者社群熱帖 |
| `sspai` | 少數派 | 科技 | 少數派高品質科技生活文章 |
| `thepaper` | 澎湃新聞 | 新聞 | 澎湃新聞即時熱榜 |
| `zhihu_daily` | 知乎日報 | 知識 | 知乎每日精選高品質文章 |
| `wechat` | 微信熱搜 | 社交 | 微信熱搜榜 |
| `headlines` | 今日頭條 | 新聞 | 今日頭條即時頭條 |
| `netease` | 網易新聞 | 新聞 | 網易熱門新聞 |
| `weibo_search` | 微博搜尋榜 | 社交 | 微博搜尋即時熱門關鍵詞 |

## 🚀 快速開始

### 安裝

```bash
# 使用 pip
pip install flowfeed

# 中國大陸鏡像加速
pip install flowfeed -i https://mirrors.aliyun.com/pypi/simple/
```

### 從原始碼安裝

```bash
git clone https://github.com/gitstq/flowfeed.git
cd flowfeed
pip install -e ".[dev]"
```

### 首次執行

```bash
# 抓取所有資料源並在終端顯示
flowfeed

# 抓取指定資料源
flowfeed -s hackernews github weibo

# 匯出為 HTML 儀表板
flowfeed -f html -o dashboard.html

# 匯出為 RSS 訂閱
flowfeed -f rss -o feed.xml

# 關鍵字過濾
flowfeed --filter-keyword AI "人工智能" LLM

# 排除關鍵字
flowfeed --exclude-keyword 廣告 推廣

# 按分類篩選
flowfeed --category tech social

# 設定最低熱度分數
flowfeed --min-score 50
```

## 📖 使用指南

### 基本指令

```bash
# 顯示說明
flowfeed --help

# 列出所有可用資料源
flowfeed list-sources

# 產生範例設定檔
flowfeed init-config
```

### 輸出格式

```bash
# 終端（預設）— 精美 Rich 表格
flowfeed

# JSON
flowfeed -f json -o news.json

# Markdown
flowfeed -f markdown -o digest.md

# HTML 儀表板
flowfeed -f html -o report.html

# RSS 訂閱
flowfeed -f rss -o feed.xml
```

### 篩選功能

```bash
# 僅顯示包含特定關鍵字的項目
flowfeed --filter-keyword AI Python

# 排除包含特定關鍵字的項目
flowfeed --exclude-keyword 廣告 推廣

# 正則包含
flowfeed --regex-include "(?i)(AI|LLM|GPT)"

# 正則排除
flowfeed --regex-exclude "(?i)(廣告|推廣)"

# 分類篩選
flowfeed --category tech social knowledge

# 最低熱度分數
flowfeed --min-score 30
```

### 進階用法

```bash
# 使用設定檔
flowfeed -c /path/to/config.yaml

# 設定代理
flowfeed --proxy http://127.0.0.1:7890

# 限制每個資料源的條目數
flowfeed -n 50
```

### 設定檔

建立 `~/.flowfeed/config.yaml`：

```bash
flowfeed init-config
```

設定檔範例：

```yaml
sources:
  weibo:
    enabled: true
    count: 30
    timeout: 15
  hackernews:
    enabled: true
    count: 30
  github:
    enabled: true
    count: 20

filter:
  keywords: []
  exclude_keywords: []
  regex_include: ""
  regex_exclude: ""
  categories: []
  min_hot_score: 0

export:
  format: "terminal"
  output_dir: "./output"

proxy: ""
max_concurrent: 5
```

## 💡 設計理念

### 為什麼 CLI 優先？

身為開發者，我們生活在終端中。FlowFeed 的設計理念：

- **快速** — 毫秒級啟動，無需瀏覽器
- **可編寫腳本** — 可將輸出管道傳遞給其他工具，整合至 CI/CD
- **可組合** — 匯出為 JSON/RSS 並輸入至其他應用程式
- **極簡** — 無資料庫、無伺服器、無前端框架開銷

### 差異化亮點

FlowFeed 靈感來自 [newsnow](https://github.com/ourongxing/newsnow) 等新聞聚合器，但採用根本不同的方式：

| | newsnow | FlowFeed |
|---|---|---|
| 介面 | Web UI (Vue+Nitro) | CLI 優先 + HTML 匯出 |
| 語言 | TypeScript | Python |
| 部署 | Cloudflare/Vercel | 零配置，本機執行 |
| 目標使用者 | 一般讀者 | 開發者 |
| 輸出 | 僅網頁 | 終端/JSON/MD/HTML/RSS |
| 依賴 | pnpm + Node 20 + DB | Python 3.10+（5 個套件）|

### 路線圖

- [ ] 更多新聞來源（Reddit、Lobsters、InfoQ、36kr）
- [ ] WebSocket 即時推送模式
- [ ] MCP Server 整合
- [ ] TUI 互動模式（Textual）
- [ ] 外掛系統支援自訂來源
- [ ] Docker 映像

## 🤝 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

## 📄 授權

[MIT](LICENSE) © 2026 gitstq
