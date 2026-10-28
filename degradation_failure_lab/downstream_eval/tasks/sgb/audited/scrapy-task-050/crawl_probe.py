
import os
import sys
import json
import socket
import inspect
import threading
import tempfile
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.path.insert(0, '/submission')
import agent_output
import scrapy
from scrapy.crawler import CrawlerProcess

# Create a tiny website with depth 0 -> 1 -> 2 -> 3
tmpdir = tempfile.TemporaryDirectory()
root = Path(tmpdir.name)

(root / "index.html").write_text('<html><body><a href="/page1.html">p1</a></body></html>', encoding="utf-8")
(root / "page1.html").write_text('<html><body><a href="/page2.html">p2</a></body></html>', encoding="utf-8")
(root / "page2.html").write_text('<html><body><a href="/page3.html">p3</a></body></html>', encoding="utf-8")
(root / "page3.html").write_text('<html><body>done</body></html>', encoding="utf-8")

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

os.chdir(root)

sock = socket.socket()
sock.bind(("127.0.0.1", 0))
host, port = sock.getsockname()
sock.close()

server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

visited = []

base_cls = agent_output.DepthLimitZeroSpider

class ProbeSpider(base_cls):
    name = "probe_depth_limit_zero"
    start_urls = [f"http://127.0.0.1:{port}/index.html"]

    def parse(self, response):
        depth = response.meta.get("depth", 0)
        visited.append({"url": response.url, "depth": depth})
        for href in response.css("a::attr(href)").getall():
            yield response.follow(href, callback=self.parse)

process = CrawlerProcess(settings={
    "LOG_ENABLED": False,
})
process.crawl(ProbeSpider)
process.start()

server.shutdown()
server.server_close()
tmpdir.cleanup()

out = {
    "visited_count": len(visited),
    "max_depth_seen": max((x["depth"] for x in visited), default=None),
    "depths": sorted(set(x["depth"] for x in visited)),
    "urls": [x["url"] for x in visited],
}
print(json.dumps(out))
