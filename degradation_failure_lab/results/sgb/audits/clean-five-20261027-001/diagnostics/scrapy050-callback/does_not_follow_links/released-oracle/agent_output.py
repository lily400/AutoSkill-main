import scrapy
class DepthLimitZeroSpider(scrapy.Spider):
    name='no_follow_counterexample'
    custom_settings={'DEPTH_LIMIT':0}
    def parse(self,response):
        yield {'url':response.url}
def get_depth_limit_zero_finding():
    return {'depth_limit':0,'effective_max_depth':None,'follows_beyond_start_urls':True,'summary':'DEPTH_LIMIT=0 means no depth limit and is unlimited.'}
