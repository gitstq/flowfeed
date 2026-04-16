"""News source adapters for FlowFeed."""

from flowfeed.sources.base import NewsItem, SourceBase
from flowfeed.sources.weibo import WeiboHotSource
from flowfeed.sources.zhihu import ZhihuHotSource
from flowfeed.sources.baidu import BaiduHotSource
from flowfeed.sources.douyin import DouyinHotSource
from flowfeed.sources.bilibili import BilibiliHotSource
from flowfeed.sources.hackernews import HackerNewsSource
from flowfeed.sources.producthunt import ProductHuntSource
from flowfeed.sources.github_trending import GitHubTrendingSource
from flowfeed.sources.v2ex import V2EXSource
from flowfeed.sources.sspai import SspaiSource
from flowfeed.sources.thepaper import ThePaperSource
from flowfeed.sources.zhihu_daily import ZhihuDailySource
from flowfeed.sources.wechat import WeChatHotSource
from flowfeed.sources.headlines import HeadlinesSource
from flowfeed.sources.netease import NeteaseSource
from flowfeed.sources.weibo_search import WeiboSearchSource

ALL_SOURCES: list[type[SourceBase]] = [
    WeiboHotSource,
    ZhihuHotSource,
    BaiduHotSource,
    DouyinHotSource,
    BilibiliHotSource,
    HackerNewsSource,
    ProductHuntSource,
    GitHubTrendingSource,
    V2EXSource,
    SspaiSource,
    ThePaperSource,
    ZhihuDailySource,
    WeChatHotSource,
    HeadlinesSource,
    NeteaseSource,
    WeiboSearchSource,
]

SOURCE_REGISTRY: dict[str, type[SourceBase]] = {
    cls.source_id: cls for cls in ALL_SOURCES
}

__all__ = [
    "NewsItem",
    "SourceBase",
    "ALL_SOURCES",
    "SOURCE_REGISTRY",
]
