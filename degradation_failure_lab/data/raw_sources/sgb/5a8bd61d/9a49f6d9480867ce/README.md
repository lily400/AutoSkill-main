# Trafilatura

A Python package and command-line tool for gathering text on the Web.

It includes discovery, extraction, and text processing components. Its main application is web corpus construction and target text extraction from web pages.

## Features

- Web crawling and feed discovery
- Robust text extraction from HTML pages
- Metadata extraction (title, author, date, etc.)
- Support for multiple output formats (TXT, CSV, JSON, XML)
- Language detection
- Deduplication
- URL management

## Installation

```bash
pip install trafilatura
```

## Usage

### Python

```python
import trafilatura

downloaded = trafilatura.fetch_url('https://example.org')
result = trafilatura.extract(downloaded)
```

### Command-line

```bash
trafilatura -u "https://example.org"
```

### Key Parameters

```python
trafilatura.extract(
    downloaded,
    output_format='txt',      # txt, csv, json, xml
    favor_precision=False,     # prioritize precision over recall
    include_comments=True,     # include user comments
    include_tables=True,       # include table content
    deduplicate=False,         # remove duplicate content
    with_metadata=False,       # include metadata in output
    target_language=None,      # filter by language
    no_fallback=False,         # disable fallback extraction
)
```

## How It Works

Trafilatura uses a combination of readability heuristics and rule-based extraction to identify the main content area of a web page. It processes HTML to find the primary text while filtering out navigation, ads, and boilerplate.

## Citation

```
@article{barbaresi-2021-trafilatura,
  title = {Trafilatura: A Web Scraping Library and Command-Line Tool for Text Discovery and Extraction},
  author = {Barbaresi, Adrien},
  year = {2021}
}
```

## License

Apache License 2.0
