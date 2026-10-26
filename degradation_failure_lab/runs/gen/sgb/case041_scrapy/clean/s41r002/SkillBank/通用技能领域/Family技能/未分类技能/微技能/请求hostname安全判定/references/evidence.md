# 请求hostname安全判定 Evidence

- family: 未分类技能
- skill_id: d18ce1e0-736d-55d1-8960-8bee27f14091
- support_count: 1

## Evidence 1

- support_id: c95ebfa6-0c76-52d0-b88e-8655b01a26f2
- relation_type: support
- document: input001\offsite.md
- doc_id: 97f9fa22-9557-5601-8e90-c1ac6c978f0c
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input001\offsite.md
- section: # Source code for scrapy.downloadermiddlewares.offsite
- span: 204:2592
- confidence: 0.80
- quote: ```
from __future__ import annotations

import logging
import re
import warnings
from typing import TYPE_CHECKING

from scrapy import Request, Spider, signals
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.decorators import _warn_spider_arg
from scrapy.utils.httpobj import urlparse_cached

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self

from scrapy.crawler import Crawler
    from scrapy.statscollectors import StatsCollector

logger = logging.getLogger(__name__)

[docs]
class OffsiteMiddleware:
    crawler: Crawler

def __init__(self, stats: StatsCollector):
        self.stats = stats
        self.domains_seen: set[str] = set()

def spider_opened(self, spider: Spider) -> None:
        self.host_regex: re.Pattern[str] = self.get_host_regex(spider)

def request_scheduled(self, request: Request, spider: Spider) -> None:
        self.process_request(request)

def should_follow(self, request: Request, spider: Spider) -> bool:
        regex = self.host_regex
        # hostname can be None for wrong urls (like javascript links)
        host = urlparse_cached(request).hostname or ""
        return bool(regex.search(host))
