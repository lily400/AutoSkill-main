import os
os.write(1,b'not-json\n')
import scrapy
from pathlib import Path
Path("/tmp/scrapy041-candidate-marker").write_text("candidate container only")

class DemoSpider(scrapy.Spider):
    name = "demo"
    allowed_domains = ["example.com"]

    def start_requests(self):
        yield scrapy.Request("http://other.com/resource", meta={"allow_offsite": True})
