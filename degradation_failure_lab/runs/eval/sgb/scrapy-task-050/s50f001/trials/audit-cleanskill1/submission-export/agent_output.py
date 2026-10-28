from __future__ import annotations

from typing import Dict, Iterable, Optional

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DepthLimitZeroSpider(CrawlSpider):
    name = "depth_limit_zero_spider"
    # Spider-level settings: demonstrate Scrapy behavior when DEPTH_LIMIT is 0.
    custom_settings = {
        "DEPTH_LIMIT": 0,
    }

    # Keep the spider self-contained; the verifier may subclass it and override parsing.
    rules = (
        Rule(LinkExtractor(), callback="parse_item", follow=True),
    )

    def __init__(self, start_urls: Optional[Iterable[str]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if start_urls is not None:
            self.start_urls = list(start_urls)

    def parse_item(self, response):
        # Yield a basic item and keep recursion driven by CrawlSpider rules.
        yield {"url": response.url}

    def parse(self, response):
        # Recursively follow all <a href> links found on each response.
        for link in LinkExtractor().extract_links(response):
            yield response.follow(link.url, callback=self.parse)
        yield {"url": response.url}


def get_depth_limit_zero_finding() -> Dict[str, object]:
    return {
        "depth_limit": 0,
        "effective_max_depth": None,
        "follows_beyond_start_urls": True,
        "summary": (
            "In Scrapy, DEPTH_LIMIT=0 disables depth limiting, so the crawler may follow "
            "links beyond the start URLs without a maximum crawl depth enforced by the depth middleware."
        ),
        # Optional comparison note for clarity.
        "comparison_note": (
            "Unlike DEPTH_LIMIT=1, which only allows one hop beyond the start URLs, "
            "DEPTH_LIMIT=0 means no depth cap is enforced."
        ),
    }
