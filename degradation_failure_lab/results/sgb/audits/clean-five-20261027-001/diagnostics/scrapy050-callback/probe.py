import functools,json,sys,tempfile,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from scrapy.crawler import CrawlerProcess
from scrapy import signals
sys.path.insert(0,'/candidate')
import agent_output
root=Path(tempfile.mkdtemp())
for i in range(4):
    link=('<a href="/page%d.html">next</a>'%(i+1)) if i<3 else 'done'
    (root/('index.html' if i==0 else 'page%d.html'%i)).write_text(link,encoding='utf-8')
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
class Probe(agent_output.DepthLimitZeroSpider):
    name='diagnostic_original_callbacks'
    start_urls=['http://127.0.0.1:%d/index.html'%server.server_port]
seen=[]
def received(response,request,spider):
    seen.append({'url':response.url,'depth':response.meta.get('depth',0),'status':response.status})
process=CrawlerProcess(settings={'LOG_ENABLED':False,'TELNETCONSOLE_ENABLED':False,'DOWNLOAD_TIMEOUT':3,'CLOSESPIDER_TIMEOUT':10,'CLOSESPIDER_PAGECOUNT':8,'CONCURRENT_REQUESTS':1})
crawler=process.create_crawler(Probe)
crawler.signals.connect(received,signal=signals.response_received,weak=False)
process.crawl(crawler)
process.start()
server.shutdown();server.server_close()
print(json.dumps({'counted_via':'response_received signal; candidate callbacks preserved','visited_count':len(seen),'max_depth_seen':max((x['depth'] for x in seen),default=None),'responses':seen}))
