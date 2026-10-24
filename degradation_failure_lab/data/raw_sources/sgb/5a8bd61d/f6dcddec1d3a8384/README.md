# pdfplumber

pdfplumber is a Python library for exploring and extracting information from PDF files.

## Relevant capability for this task

- `pdfplumber.open(...)`
- `pdf.pages`
- `page.extract_text()`
- `page.extract_words()`

## Notes

- pdfplumber is commonly used for page-level text extraction and word-level layout inspection.
- The library builds on top of `pdfminer.six`.
- For deterministic code_repo tasks, page text and word counts are easier to validate than rendered output.
