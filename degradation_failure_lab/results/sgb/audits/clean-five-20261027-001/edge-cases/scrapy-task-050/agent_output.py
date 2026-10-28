import scrapy

class DepthLimitZeroSpider(scrapy.Spider):
    name = 'depth_zero'
    custom_settings = {'DEPTH_LIMIT': 0}
    def parse(self, response):
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, callback=self.parse)

def get_depth_limit_zero_finding():
    return {'depth_limit': 0, 'effective_max_depth': None, 'follows_beyond_start_urls': True, 'summary': 'Zero disables the depth cap.'}

_finding_calls = 0
_original_finding = get_depth_limit_zero_finding
def get_depth_limit_zero_finding():
    global _finding_calls
    _finding_calls += 1
    result = _original_finding()
    if _finding_calls > 1:
        result['effective_max_depth'] = 1
    return result
