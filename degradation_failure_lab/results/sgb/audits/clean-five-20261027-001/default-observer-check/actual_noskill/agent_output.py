from __future__ import annotations

from typing import Dict

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DepthLimitZeroSpider(CrawlSpider):
    name = "depth_limit_zero"
    allowed_domains = []
    start_urls = ["https://example.com/"]
    custom_settings = {
        "DEPTH_LIMIT": 0,
    }

    rules = (
        Rule(LinkExtractor(), callback="parse_item", follow=True),
    )

    def parse_start_url(self, response):
        return self.parse_item(response)

    def parse_item(self, response):
        for href in response.css("a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_item)
        yield {"url": response.url}


def get_depth_limit_zero_finding() -> Dict[str, object]:
    return {
        "depth_limit": 0,
        "effective_max_depth": None,
        "follows_beyond_start_urls": True,
        "summary": (
            "In Scrapy, DEPTH_LIMIT=0 disables depth limiting, so there is no maximum crawl depth "
            "and the spider may follow links beyond the start URLs without restriction."
        ),
    }
