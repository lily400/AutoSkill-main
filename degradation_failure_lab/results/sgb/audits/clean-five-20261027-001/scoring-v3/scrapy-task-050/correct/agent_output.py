import scrapy

class DepthLimitZeroSpider(scrapy.Spider):
    name = 'depth_zero'
    custom_settings = {'DEPTH_LIMIT': 0}
    def parse(self, response):
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, callback=self.parse)

def get_depth_limit_zero_finding():
    return {'depth_limit': 0, 'effective_max_depth': None, 'follows_beyond_start_urls': True, 'summary': 'Zero disables the depth cap.'}
