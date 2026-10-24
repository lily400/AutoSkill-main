======
eparse
======

Description
===========
Excel spreadsheet crawler and table parser for data extraction and querying.

Features
========
* Command-line interface
* Recursive Excel file discovery
* Sub-tabular data extraction (logical tables)
* SQLite and PostgreSQL database interfaces
* CLI query tool
* Summary data metrics

Usage
=====
eparse can be used as either a Python library or from the command line.

Python example::

   from eparse.core import get_df_from_file

   print([table for table in get_df_from_file("myfile.xlsx")])

CLI commands include:
* ``scan`` for discovering Excel files and sheets
* ``parse`` for finding tables and optionally serializing them
* ``query`` for querying persisted output
* ``migrate`` for database migrations

Parsing notes
=============
eparse identifies table corners as cells that have empty cells above and to the left
and are followed by a dense or sparse 2x2 region. It can also adjust for rowspan
labels and empty corners while extracting logical tables from workbooks.
