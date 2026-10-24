# Crawl4AI: Open-source LLM Friendly Web Crawler & Scraper

[![PyPI version](https://badge.fury.io/py/crawl4ai.svg)](https://badge.fury.io/py/crawl4ai)
[![Python Version](https://img.shields.io/pypi/pyversions/crawl4ai)](https://pypi.org/project/crawl4ai/)
[![Downloads](https://static.pepy.tech/badge/crawl4ai/month)](https://pepy.tech/project/crawl4ai)
[![License](https://img.shields.io/github/license/unclecode/crawl4ai)](https://github.com/unclecode/crawl4ai/blob/main/LICENSE)

Crawl4AI is a production-grade, open-source web crawler and scraper designed specifically for LLMs, AI agents, and data pipelines. It converts web content into clean, well-structured Markdown with high speed and accuracy.

## Features

- **LLM-Ready Markdown**: Generates clean markdown with smart filtering, citation preservation, and media handling
- **Structured Data Extraction**: LLM-driven extraction with custom schemas, CSS-based selectors, or chunking strategies
- **Browser Automation**: Full Playwright integration with JavaScript execution, session management, lazy-load handling
- **Deep Crawling**: BFS, DFS, and best-first search strategies for multi-page crawls with crash recovery
- **Fast Performance**: Optimized for speed, with `prefetch=True` mode for 5-10x faster URL discovery
- **Multiple Output Formats**: Clean markdown, fit markdown (filtered for AI), raw HTML, screenshots, and structured JSON

## Installation

```bash
pip install -U crawl4ai
crawl4ai-setup  # Install Playwright browsers
```

## Quick Start

### Python API

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        print(result.markdown)        # Clean markdown
        print(result.fit_markdown)    # Filtered markdown for AI
        print(result.links)           # Extracted links
        print(result.media)           # Extracted media

asyncio.run(main())
```

### With Raw HTML (No Browser Required)

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        bypass_cache=True
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="raw://",
            config=config,
            raw_html="<html><body><h1>Hello</h1></body></html>"
        )
        print(result.markdown)

asyncio.run(main())
```

### CLI

```bash
crwl https://example.com -o markdown
crwl https://docs.example.com --deep-crawl bfs --max-pages 10
```

## CrawlResult Object

The `arun()` method returns a `CrawlResult` object containing:

- `result.markdown` — Full clean markdown of the page
- `result.fit_markdown` — Filtered/condensed markdown optimized for AI consumption
- `result.html` — Raw HTML content
- `result.links` — Dictionary with `internal` and `external` link lists
- `result.media` — Dictionary with `images`, `videos`, `audios` lists
- `result.metadata` — Page metadata (title, description, etc.)
- `result.success` — Boolean indicating crawl success
- `result.status_code` — HTTP status code

### Link Structure

Each link in `result.links["internal"]` and `result.links["external"]` is a dict:
```json
{"href": "https://...", "text": "link text", "title": "..."}
```

### Media Structure

Each image in `result.media["images"]` is a dict:
```json
{"src": "https://...", "alt": "description", "score": 5}
```

## Structured Extraction

### CSS-Based Extraction

```python
from crawl4ai.extraction_strategy import CSSExtractionStrategy

schema = {
    "name": "Products",
    "baseSelector": "div.product",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "price", "selector": ".price", "type": "text"},
    ]
}
strategy = CSSExtractionStrategy(schema)
```

### LLM-Based Extraction

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4",
    instruction="Extract all product names and prices"
)
```

## Deployment

### Docker

```bash
docker pull unclecode/crawl4ai
docker run -p 11235:11235 unclecode/crawl4ai
```

### Self-Hosted API

Crawl4AI includes a FastAPI server with JWT auth, WebSocket streaming, and Prometheus metrics.

## License

Apache 2.0
