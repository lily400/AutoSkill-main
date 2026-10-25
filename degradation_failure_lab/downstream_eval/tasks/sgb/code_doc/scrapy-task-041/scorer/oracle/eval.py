import os
import sys
import ast
import importlib.util

import pytest
import scrapy

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/root")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")


def load_agent_module():
    assert os.path.exists(OUTPUT_FILE), f"agent_output.py not found at {OUTPUT_FILE}"

    spec = importlib.util.spec_from_file_location("agent_output", OUTPUT_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def read_code():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def parse_code():
    return ast.parse(read_code())


def find_spiders(module):
    spiders = []

    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, scrapy.Spider) and obj != scrapy.Spider:
            spiders.append(obj)

    return spiders


def collect_requests(spider):
    requests = []

    if hasattr(spider, "start_requests"):
        try:
            requests.extend(list(spider.start_requests()))
        except Exception:
            pass

    return requests


class MiddlewareVisitor(ast.NodeVisitor):

    def __init__(self):
        self.bad = []

    def visit_Constant(self, node):
        if isinstance(node.value, str):

            if node.value in [
                "SPIDER_MIDDLEWARES",
                "DOWNLOADER_MIDDLEWARES",
                "OffsiteMiddleware",
            ]:
                self.bad.append(node.value)

        self.generic_visit(node)


class TestScrapyOffsiteBypass:

    def test_file_exists(self):
        assert os.path.exists(OUTPUT_FILE)

    def test_can_import(self):
        load_agent_module()

    def test_imports_scrapy(self):
        code = read_code()
        assert "scrapy" in code

    def test_has_spider_class(self):
        module = load_agent_module()

        spiders = find_spiders(module)

        assert spiders, "No scrapy.Spider subclass found"

    def test_allowed_domains(self):
        module = load_agent_module()

        spiders = find_spiders(module)

        matched = False

        for spider in spiders:
            allowed = getattr(spider, "allowed_domains", None)

            if allowed == ["example.com"]:
                matched = True

        assert matched, "Spider must define allowed_domains=['example.com']"

    def test_spider_produces_requests(self):
        module = load_agent_module()

        spiders = find_spiders(module)

        found = False

        for spider_cls in spiders:
            spider = spider_cls()

            requests = collect_requests(spider)

            if requests:
                found = True

        assert found, "Spider does not produce any Request objects"

    def test_request_to_other_domain(self):
        module = load_agent_module()

        spiders = find_spiders(module)

        found = False

        for spider_cls in spiders:

            spider = spider_cls()

            requests = collect_requests(spider)

            for req in requests:

                if getattr(req, "url", "") == "http://other.com/resource":

                    found = True

        assert found, "Spider must produce request to http://other.com/resource"

    def test_allow_offsite_meta(self):

        module = load_agent_module()

        spiders = find_spiders(module)

        found = False

        for spider_cls in spiders:

            spider = spider_cls()

            requests = collect_requests(spider)

            for req in requests:

                if req.url == "http://other.com/resource":

                    meta = getattr(req, "meta", {})

                    if meta.get("allow_offsite") is True:
                        found = True

        assert found, "Request must include meta={'allow_offsite': True}"

    def test_allow_offsite_is_boolean(self):

        module = load_agent_module()

        spiders = find_spiders(module)

        for spider_cls in spiders:

            spider = spider_cls()

            requests = collect_requests(spider)

            for req in requests:

                if req.url == "http://other.com/resource":

                    assert req.meta.get("allow_offsite") is True

    def test_no_middleware_modification(self):

        tree = parse_code()

        visitor = MiddlewareVisitor()

        visitor.visit(tree)

        assert not visitor.bad, "Middleware configuration must not be modified"