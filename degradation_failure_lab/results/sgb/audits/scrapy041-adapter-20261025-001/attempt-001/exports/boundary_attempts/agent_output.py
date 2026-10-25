from pathlib import Path
for name in ["/oracle/eval.py", "/bridge/oracle_bridge.py", "/observations/envelope.json",
             "/results/junit.xml", "/tests/eval.py", "/var/run/docker.sock"]:
    assert not Path(name).exists(), name
try:
    Path("/runtime/worker.py").write_text("tampered")
except OSError:
    pass
else:
    raise AssertionError("worker was writable")
try:
    Path("/oracle/eval.py").write_text("tampered")
except OSError:
    pass
else:
    raise AssertionError("Oracle was writable")
import scrapy
from pathlib import Path
Path("/tmp/scrapy041-candidate-marker").write_text("candidate container only")

class DemoSpider(scrapy.Spider):
    name = "demo"
    allowed_domains = ["example.com"]

    def start_requests(self):
        yield scrapy.Request("http://other.com/resource", meta={"allow_offsite": True})
