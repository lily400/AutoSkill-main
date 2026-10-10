---
id: "096d66d1-41a5-5907-8567-9bb37b5579b3"
name: "CSV Duplicate Row Removal"
description: "Reads a CSV file, removes exact duplicate rows based on all columns, and writes the deduplicated data to a new file while preserving the original."
version: "0.1.0"
tags:
  - "csv"
  - "deduplication"
  - "data cleaning"
  - "file transformation"
triggers:
  - "user needs to clean CSV data"
  - "input has suspected duplicate rows"
  - "original file must remain unmodified"
---

# CSV Duplicate Row Removal

Reads a CSV file, removes exact duplicate rows based on all columns, and writes the deduplicated data to a new file while preserving the original.

## Prompt

Load the input CSV file into memory; identify and remove rows that are exact duplicates across all columns; write the resulting unique rows to a new CSV file with the same schema and encoding as the input; ensure the original file is never modified or overwritten.

## Objective

data cleaning
## Applicable Signals

- input file path provided
- output file path specified
- no fuzzy matching criteria requested

## Contraindications

- data requires fuzzy or partial-row deduplication
- row order must be preserved for time-series analysis
- memory-constrained environment where full load is unsafe

## Intervention Moves

- read_csv
- drop_duplicates
- to_csv

## Workflow Steps

- Validate input CSV file existence and readability.
- Load CSV into tabular structure (e.g., pandas DataFrame).
- Apply exact row-wise deduplication (keep='first').
- Validate output file path is writable and does not overwrite input.
- Write deduplicated data to new CSV file with identical dialect and encoding.
- Confirm original file checksum or mtime remains unchanged.

## Constraints

- Input and output files must be on accessible local or mounted filesystem.
- All columns participate in duplicate detection — no column subset override supported.

## Cautions

- Large files may exceed memory limits; warn before loading if size > 500MB.
- Empty or malformed CSV may raise parsing errors — validate structure first.

## Output Contract

- A new CSV file containing only unique rows, with identical column structure, encoding, and dialect as input; original file byte-identical and unmodified.

## Triggers

- user needs to clean CSV data
- input has suspected duplicate rows
- original file must remain unmodified
