import scrapy


class AgentSpider(scrapy.Spider):
    name = "agent_spider"
    allowed_domains = ["example.com"]

    def start_requests(self):
        yield scrapy.Request(
            "http://other.com/resource",
            meta={"allow_offsite": True},
        )
