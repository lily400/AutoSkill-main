# ScrapeGraphAI

[![PyPI version](https://badge.fury.io/py/scrapegraphai.svg)](https://badge.fury.io/py/scrapegraphai)
[![Python Version](https://img.shields.io/pypi/pyversions/scrapegraphai)](https://pypi.org/project/scrapegraphai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ScrapeGraphAI is a Python web scraping library that uses LLM and direct graph logic to create scraping pipelines for websites and local documents (XML, HTML, JSON, Markdown, etc.).

## Features

- LLM-powered extraction with natural language prompts
- Multiple scraping pipeline types (SmartScraperGraph, SearchGraph, SpeechGraph, etc.)
- Support for local documents (HTML, XML, JSON, Markdown)
- Multiple LLM providers (OpenAI, Groq, Azure, Gemini, Ollama)
- Integration with LangChain, LlamaIndex, Crew AI

## Installation

```bash
pip install scrapegraphai
playwright install
```

## Quick Start

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage",
    source="https://scrapegraphai.com/",
    config=graph_config
)

result = smart_scraper_graph.run()
```

## Pipeline Types

### SmartScraperGraph
Single-page extraction from a URL or local file using LLM.

### SearchGraph
Multi-page extraction from search engine results.

### SpeechGraph
Extraction with audio file generation.

### ScriptCreatorGraph
Generates Python extraction scripts from web pages.

## Supported LLM Providers

- OpenAI (GPT-4, GPT-3.5)
- Groq
- Azure OpenAI
- Google Gemini
- Ollama (local models)

## License

MIT License
