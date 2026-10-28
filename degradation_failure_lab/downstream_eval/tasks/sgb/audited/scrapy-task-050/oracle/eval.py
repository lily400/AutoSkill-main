"""Test cases for scrapy_task_050: Depth Limit Zero Behavior

This test file supports both local testing and Docker testing via the TEST_ROOT_DIR
environment variable. By default, it uses /root (Docker mode).

Local testing:
    TEST_ROOT_DIR=/path/to/solution pytest tests/eval.py

Docker testing:
    pytest tests/eval.py
"""

import os
import sys
import json
import inspect
import socket
import threading
import tempfile
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/root")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")


class TestDepthLimitZeroBehavior:
    def test_file_exists(self):
        assert os.path.exists(OUTPUT_FILE), f"agent_output.py not found at {OUTPUT_FILE}"

    def test_file_not_empty(self):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            code = f.read()
        assert len(code.strip()) > 50, "agent_output.py is empty or too short"

    def test_module_imports(self):
        sys.path.insert(0, ROOT_DIR)
        import agent_output  # noqa: F401

    def test_has_required_api(self):
        sys.path.insert(0, ROOT_DIR)
        import agent_output
        import scrapy

        assert hasattr(agent_output, "DepthLimitZeroSpider"), \
            "agent_output.py must define DepthLimitZeroSpider"

        spider_cls = agent_output.DepthLimitZeroSpider
        assert inspect.isclass(spider_cls), "DepthLimitZeroSpider must be a class"
        assert issubclass(spider_cls, scrapy.Spider), \
            "DepthLimitZeroSpider must inherit from scrapy.Spider"

        assert hasattr(agent_output, "get_depth_limit_zero_finding"), \
            "agent_output.py must define get_depth_limit_zero_finding()"
        assert callable(agent_output.get_depth_limit_zero_finding), \
            "get_depth_limit_zero_finding must be callable"

    def test_depth_limit_setting_is_zero(self):
        sys.path.insert(0, ROOT_DIR)
        import agent_output

        spider_cls = agent_output.DepthLimitZeroSpider
        settings = getattr(spider_cls, "custom_settings", None)

        assert isinstance(settings, dict), \
            "DepthLimitZeroSpider.custom_settings must be a dict"
        assert settings.get("DEPTH_LIMIT", None) == 0, \
            "DepthLimitZeroSpider.custom_settings must set DEPTH_LIMIT to 0"

    def test_finding_structure_and_semantics(self):
        sys.path.insert(0, ROOT_DIR)
        import agent_output

        result = agent_output.get_depth_limit_zero_finding()
        assert isinstance(result, dict), "get_depth_limit_zero_finding() must return a dict"

        required_keys = {
            "depth_limit",
            "effective_max_depth",
            "follows_beyond_start_urls",
            "summary",
        }
        missing = required_keys - set(result.keys())
        assert not missing, f"Missing keys in result: {sorted(missing)}"

        assert result["depth_limit"] == 0, "depth_limit should report the configured value 0"

        # Accept a small, explicit set of representations
        effective = result["effective_max_depth"]
        assert (
            effective is None
            or (isinstance(effective, str) and effective.strip().lower() in {"unlimited", "no limit"})
        ), "effective_max_depth should indicate that no depth cap is enforced"

        assert result["follows_beyond_start_urls"] is True, \
            "follows_beyond_start_urls should be True for DEPTH_LIMIT=0"

        assert isinstance(result["summary"], str) and result["summary"].strip(), \
            "summary must be a non-empty string"

    def test_runtime_behavior_crawls_beyond_depth_zero(self):
        """
        Run a real crawl against a tiny local website with multiple link depths.
        The probe spider inherits the agent spider's settings, but uses a known parse()
        implementation so this test measures DEPTH_LIMIT behavior rather than text matching.
        """
        script = textwrap.dedent(
            f"""
            import os
            import sys
            import json
            import socket
            import inspect
            import threading
            import tempfile
            from pathlib import Path
            from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

            sys.path.insert(0, {ROOT_DIR!r})
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
                start_urls = [f"http://127.0.0.1:{{port}}/index.html"]

                def parse(self, response):
                    depth = response.meta.get("depth", 0)
                    visited.append({{"url": response.url, "depth": depth}})
                    for href in response.css("a::attr(href)").getall():
                        yield response.follow(href, callback=self.parse)

            process = CrawlerProcess(settings={{
                "LOG_ENABLED": False,
            }})
            process.crawl(ProbeSpider)
            process.start()

            server.shutdown()
            server.server_close()
            tmpdir.cleanup()

            out = {{
                "visited_count": len(visited),
                "max_depth_seen": max((x["depth"] for x in visited), default=None),
                "depths": sorted(set(x["depth"] for x in visited)),
                "urls": [x["url"] for x in visited],
            }}
            print(json.dumps(out))
            """
        )

        completed = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
        )

        stdout = completed.stdout.strip().splitlines()
        assert stdout, f"No output from crawl subprocess. stderr={completed.stderr}"

        data = json.loads(stdout[-1])

        # Must at least reach depth 2 on our tiny site if DEPTH_LIMIT=0 means "no limit"
        assert data["visited_count"] >= 3, f"Expected multiple pages to be crawled, got: {data}"
        assert data["max_depth_seen"] is not None, f"Could not determine max depth: {data}"
        assert data["max_depth_seen"] >= 2, \
            f"Expected crawling beyond depth 0 with DEPTH_LIMIT=0, got: {data}"

    def test_finding_matches_runtime_behavior(self):
        sys.path.insert(0, ROOT_DIR)
        import agent_output

        result = agent_output.get_depth_limit_zero_finding()

        assert result["depth_limit"] == 0
        assert result["follows_beyond_start_urls"] is True

        effective = result["effective_max_depth"]
        assert (
            effective is None
            or (isinstance(effective, str) and effective.strip().lower() in {"unlimited", "no limit"})
        ), "Reported effective_max_depth is inconsistent with expected Scrapy behavior"
