# FlowFeed 📡

<p align="center">
  <strong>轻量级智能新闻聚合引擎</strong>
</p>
<p align="center">
  面向开发者的 CLI 优先工具，可从 16+ 个来源聚合、筛选和导出热门新闻 — 支持终端、JSON、Markdown、HTML 仪表板及 RSS 订阅。
</p>

---

## ✨ 核心特性

- **🌍 多语言界面** — English、简体中文、繁體中文；通过 `--lang`、环境变量或配置文件切换
- **16 个内置数据源** — 微博、知乎、百度、抖音、哔哩哔哩、HackerNews、GitHub Trending、ProductHunt、V2EX、少数派、澎湃新闻等
- **智能去重** — 基于 MD5 指纹的跨源去重，保留最高分版本
- **综合评分** — 归一化热度 + 排名加权，按相关性排序
- **关键词与正则过滤** — 包含/排除模式、分类筛选、最低分数阈值
- **5 种导出格式** — 终端（Rich）、JSON、Markdown、HTML 仪表板、RSS 2.0
- **精美 HTML 仪表板** — 自包含深色主题 Web 报告，含统计与分组
- **异步并行** — 可配置并行度的并发抓取
- **零重度依赖** — 仅需 httpx、rich、click、pyyaml、jinja2
- **高度可配置** — YAML 配置文件支持每个数据源的独立配置

## 📡 数据源

| ID | 名称 | 分类 | 说明 |
|---|---|---|---|
| `weibo` | 微博热搜 | 社交 | 微博实时热搜榜 |
| `zhihu` | 知乎热榜 | 知识 | 知乎实时热门问题榜 |
| `baidu` | 百度热搜 | 综合 | 百度实时热搜榜 |
| `douyin` | 抖音热搜 | 社交 | 抖音热门视频 |
| `bilibili` | B站热搜 | 社交 | B站热门话题 |
| `hackernews` | Hacker News | 科技 | HN 热门技术讨论 |
| `github` | GitHub Trending | 科技 | GitHub 热门开源项目 |
| `producthunt` | Product Hunt | 科技 | PH 每日热门新产品 |
| `v2ex` | V2EX | 科技 | V2EX 创意工作者社区热帖 |
| `sspai` | 少数派 | 科技 | 少数派高质量科技生活文章 |
| `thepaper` | 澎湃新闻 | 新闻 | 澎湃新闻实时热榜 |
| `zhihu_daily` | 知乎日报 | 知识 | 知乎每日精选高质量文章 |
| `wechat` | 微信热搜 | 社交 | 微信热搜榜 |
| `headlines` | 今日头条 | 新闻 | 今日头条实时头条 |
| `netease` | 网易新闻 | 新闻 | 网易热门新闻 |
| `weibo_search` | 微博搜索榜 | 社交 | 微博搜索实时热搜关键词 |

## 🚀 快速开始

### 安装

```bash
# 使用 pip
pip install flowfeed

# 中国大陆镜像加速
pip install flowfeed -i https://mirrors.aliyun.com/pypi/simple/
```

### 从源码安装

```bash
git clone https://github.com/gitstq/flowfeed.git
cd flowfeed
pip install -e ".[dev]"
```

### 首次运行

```bash
# 抓取所有数据源并在终端显示
flowfeed

# 抓取指定数据源
flowfeed -s hackernews github weibo

# 导出为 HTML 仪表板
flowfeed -f html -o dashboard.html

# 导出为 RSS 订阅
flowfeed -f rss -o feed.xml

# 关键词过滤
flowfeed --filter-keyword AI "人工智能" LLM

# 排除关键词
flowfeed --exclude-keyword 广告 推广

# 按分类筛选
flowfeed --category tech social

# 设置最低热度分数
flowfeed --min-score 50
```

## 📖 使用指南

### 基本命令

```bash
# 显示帮助
flowfeed --help

# 列出所有可用数据源
flowfeed list-sources

# 生成示例配置文件
flowfeed init-config
```

### 输出格式

```bash
# 终端（默认）— 精美 Rich 表格
flowfeed

# JSON
flowfeed -f json -o news.json

# Markdown
flowfeed -f markdown -o digest.md

# HTML 仪表板
flowfeed -f html -o report.html

# RSS 订阅
flowfeed -f rss -o feed.xml
```

### 筛选功能

```bash
# 仅显示包含特定关键词的项目
flowfeed --filter-keyword AI Python

# 排除包含特定关键词的项目
flowfeed --exclude-keyword 广告 推广

# 正则包含
flowfeed --regex-include "(?i)(AI|LLM|GPT)"

# 正则排除
flowfeed --regex-exclude "(?i)(广告|推广)"

# 分类筛选
flowfeed --category tech social knowledge

# 最低热度分数
flowfeed --min-score 30
```

### 进阶用法

```bash
# 使用配置文件
flowfeed -c /path/to/config.yaml

# 设置代理
flowfeed --proxy http://127.0.0.1:7890

# 限制每个数据源的条目数
flowfeed -n 50
```

### 🌍 语言切换

FlowFeed 支持 3 种界面语言，优先级如下：

1. **CLI 参数** — `--lang`
2. **环境变量** — `FLOWFEED_LANG`
3. **配置文件** — `language` 字段
4. **自动检测** — 系统语言
5. **兜底** — 英文

```bash
# English（默认）
flowfeed --lang en list-sources

# 简体中文
flowfeed --lang zh-CN list-sources

# 繁體中文
flowfeed --lang zh-TW list-sources

# 通过环境变量设置
export FLOWFEED_LANG=zh-CN
flowfeed list-sources

# 语言设置同样适用于所有导出格式（HTML、Markdown、RSS）
flowfeed -f html -o dashboard.html
```

在配置文件（`~/.flowfeed/config.yaml`）中设置：

```yaml
language: "zh-CN"  # en | zh-CN | zh-TW（留空 = 自动检测）
```

### 配置文件

创建 `~/.flowfeed/config.yaml`：

```bash
flowfeed init-config
```

配置文件示例：

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
language: ""  # en | zh-CN | zh-TW（留空 = 自动检测）
```

## 💡 设计理念

### 为什么 CLI 优先？

作为开发者，我们生活在终端中。FlowFeed 的设计理念：

- **快速** — 毫秒级启动，无需浏览器
- **可编写脚本** — 可将输出管道传递给其他工具，集成到 CI/CD
- **可组合** — 导出为 JSON/RSS 并输入到其他应用程序
- **极简** — 无数据库、无服务器、无前端框架开销

### 差异化亮点

FlowFeed 灵感来自 [newsnow](https://github.com/ourongxing/newsnow) 等新闻聚合器，但采用根本不同的方式：

| | newsnow | FlowFeed |
|---|---|---|
| 界面 | Web UI (Vue+Nitro) | CLI 优先 + HTML 导出 |
| 语言 | TypeScript | Python |
| 部署 | Cloudflare/Vercel | 零配置，本机运行 |
| 目标用户 | 一般读者 | 开发者 |
| 输出 | 仅网页 | 终端/JSON/MD/HTML/RSS |
| 依赖 | pnpm + Node 20 + DB | Python 3.10+（5 个包）|

### 路线图

- [ ] 更多新闻来源（Reddit、Lobsters、InfoQ、36kr）
- [ ] WebSocket 实时推送模式
- [ ] MCP Server 集成
- [ ] TUI 交互模式（Textual）
- [ ] 插件系统支持自定义来源
- [ ] Docker 镜像

## 🤝 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

## 📄 授权

[MIT](LICENSE) © 2026 gitstq
