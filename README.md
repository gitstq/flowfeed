# FlowFeed 📡

<p align="center">
  <strong>Lightweight Intelligent News Aggregation Engine</strong>
</p>
<p align="center">
  A CLI-first tool for developers to aggregate, filter, and export trending news from 16+ sources — in terminal, JSON, Markdown, HTML dashboard, or RSS feed.
</p>
<p align="center">
  <a href="#-quick-start">Quick Start</a> · <a href="#-features">Features</a> · <a href="#-sources">Sources</a> · <a href="#-installation">Installation</a> · <a href="#-usage">Usage</a>
</p>

---

## ✨ Features

- **🌍 Multi-Language UI** — English, 简体中文, 繁體中文; switch via `--lang`, env var, or config
- **16 Built-in Sources** — Weibo, Zhihu, Baidu, Douyin, Bilibili, HackerNews, GitHub Trending, ProductHunt, V2EX, Sspai, ThePaper, and more
- **Smart Deduplication** — Cross-source dedup with MD5 fingerprinting, keeps highest-score version
- **Composite Scoring** — Normalized hot score + rank bonus, sorted by relevance
- **Keyword & Regex Filters** — Include/exclude patterns, category filtering, minimum score threshold
- **5 Export Formats** — Terminal (Rich), JSON, Markdown, HTML Dashboard, RSS 2.0
- **Beautiful HTML Dashboard** — Self-contained dark-themed web report with stats and grouping
- **Async & Parallel** — Concurrent fetching with configurable concurrency limit
- **Zero Heavy Dependencies** — Only httpx, rich, click, pyyaml, jinja2
- **Configurable** — YAML config file with per-source settings

## 📡 Sources

| ID | Name | Category | Description |
|---|---|---|---|
| `weibo` | 微博热搜 | Social | Weibo real-time hot search |
| `zhihu` | 知乎热榜 | Knowledge | Zhihu trending questions |
| `baidu` | 百度热搜 | General | Baidu real-time hot search |
| `douyin` | 抖音热搜 | Social | Douyin trending videos |
| `bilibili` | B站热搜 | Social | Bilibili trending topics |
| `hackernews` | Hacker News | Tech | HN top stories |
| `github` | GitHub Trending | Tech | GitHub trending repos |
| `producthunt` | Product Hunt | Tech | PH daily top products |
| `v2ex` | V2EX | Tech | V2EX hot topics |
| `sspai` | 少数派 | Tech | Sspai quality articles |
| `thepaper` | 澎湃新闻 | News | ThePaper hot news |
| `zhihu_daily` | 知乎日报 | Knowledge | Zhihu daily curated articles |
| `wechat` | 微信热搜 | Social | WeChat trending searches |
| `headlines` | 今日头条 | News | Toutiao real-time headlines |
| `netease` | 网易新闻 | News | Netease hot news |
| `weibo_search` | 微博搜索榜 | Social | Weibo search trending |

## 🚀 Quick Start

### Install

```bash
# Using pip
pip install flowfeed

# China mainland mirror
pip install flowfeed -i https://mirrors.aliyun.com/pypi/simple/
```

### Or run from source

```bash
git clone https://github.com/gitstq/flowfeed.git
cd flowfeed
pip install -e ".[dev]"
```

### First Run

```bash
# Fetch all sources and display in terminal
flowfeed

# Fetch specific sources
flowfeed -s hackernews github weibo

# Export to HTML dashboard
flowfeed -f html -o dashboard.html

# Export to RSS feed
flowfeed -f rss -o feed.xml

# Filter by keyword
flowfeed --filter-keyword AI "人工智能" LLM

# Exclude keywords
flowfeed --exclude-keyword 广告 推广

# Filter by category
flowfeed --category tech social

# Set minimum hot score
flowfeed --min-score 50
```

## 📖 Usage

### Basic Commands

```bash
# Show help
flowfeed --help

# List all available sources
flowfeed list-sources

# Generate example config file
flowfeed init-config
```

### Output Formats

```bash
# Terminal (default) — beautiful Rich table
flowfeed

# JSON
flowfeed -f json -o news.json

# Markdown
flowfeed -f markdown -o digest.md

# HTML Dashboard
flowfeed -f html -o report.html

# RSS Feed
flowfeed -f rss -o feed.xml
```

### Filtering

```bash
# Include only items with specific keywords
flowfeed --filter-keyword AI Python

# Exclude items with specific keywords
flowfeed --exclude-keyword "clickbait" spam

# Regex include
flowfeed --regex-include "(?i)(AI|LLM|GPT)"

# Regex exclude
flowfeed --regex-exclude "(?i)(广告|推广)"

# Category filter
flowfeed --category tech social knowledge

# Minimum hot score
flowfeed --min-score 30
```

### Advanced

```bash
# Use config file
flowfeed -c /path/to/config.yaml

# Set proxy
flowfeed --proxy http://127.0.0.1:7890

# Limit items per source
flowfeed -n 50
```

### 🌍 Language Switching

FlowFeed supports 3 UI languages. Priority order:

1. **CLI flag** — `--lang`
2. **Environment variable** — `FLOWFEED_LANG`
3. **Config file** — `language` field
4. **Auto-detect** — System locale
5. **Fallback** — English

```bash
# English (default)
flowfeed --lang en list-sources

# 简体中文
flowfeed --lang zh-CN list-sources

# 繁體中文
flowfeed --lang zh-TW list-sources

# Via environment variable
export FLOWFEED_LANG=zh-CN
flowfeed list-sources

# FLOWFEED_LANG also applies to all export formats (HTML, Markdown, RSS)
flowfeed -f html -o dashboard.html
```

In config (`~/.flowfeed/config.yaml`):

```yaml
language: "zh-CN"  # en | zh-CN | zh-TW (empty = auto-detect)
```

### Configuration File

Create `~/.flowfeed/config.yaml`:

```bash
flowfeed init-config
```

Example config:

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
language: ""  # en | zh-CN | zh-TW (empty = auto-detect)
```

## 💡 Design Philosophy

### Why CLI-first?

As developers, we live in the terminal. FlowFeed is designed to be:
- **Fast** — Start in milliseconds, no browser needed
- **Scriptable** — Pipe output to other tools, integrate into CI/CD
- **Composable** — Export to JSON/RSS and feed into other applications
- **Minimal** — No database, no server, no frontend framework overhead

### Inspiration

FlowFeed is inspired by [newsnow](https://github.com/ourongxing/newsnow) and other news aggregators, but takes a fundamentally different approach:

| | newsnow | FlowFeed |
|---|---|---|
| Interface | Web UI (Vue+Nitro) | CLI-first + HTML export |
| Language | TypeScript | Python |
| Deployment | Cloudflare/Vercel | Zero-config, runs locally |
| Target Users | General readers | Developers |
| Output | Web page only | Terminal/JSON/MD/HTML/RSS |
| Dependencies | pnpm + Node 20 + DB | Python 3.10+ (5 packages) |

### Architecture

```
flowfeed/
├── flowfeed/              # Core package
│   ├── cli.py             # CLI entry point (Click)
│   ├── config.py          # YAML config management
│   ├── engine.py          # Aggregation engine (fetch/dedup/filter/score)
│   ├── i18n.py            # Internationalization (en/zh-CN/zh-TW)
│   ├── sources/           # 16 news source adapters
│   │   ├── base.py        # SourceBase abstract class + NewsItem model
│   │   ├── weibo.py       # Weibo Hot Search
│   │   ├── zhihu.py       # Zhihu Hot List
│   │   └── ...
│   └── exporters/         # 5 output format exporters
│       ├── terminal.py    # Rich terminal table
│       ├── json_export.py # JSON serialization
│       ├── markdown.py    # Markdown export
│       ├── html_report.py # HTML dashboard (Jinja2)
│       └── rss.py         # RSS 2.0 XML
├── tests/                 # Test suite
├── pyproject.toml         # Project config
└── LICENSE                # MIT License
```

### Roadmap

- [ ] More news sources (Reddit, Lobsters, InfoQ, 36kr)
- [ ] WebSocket real-time push mode
- [ ] MCP Server integration
- [ ] TUI interactive mode (Textual)
- [ ] Plugin system for custom sources
- [ ] Docker image

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

[MIT](LICENSE) © 2026 gitstq
