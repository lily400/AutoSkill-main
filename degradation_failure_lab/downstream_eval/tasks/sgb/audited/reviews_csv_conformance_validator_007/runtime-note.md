Write the single final submission to /workspace/agent_output.py.
Source documents and tests are unavailable in this container. Python syntax checks are available.
The task container has no external network.

Wire-format clarification (shared by both conditions; no document rule values):
A successful message is exactly `SUCCESS: Processed reviews CSV validated ({row_count} rows).` with the actual data-row count. For insufficient data rows, the Issue text is `Only {row_count} rows found, expected at least {minimum_rows}` with the minimum derived from the SOP. Return only the first invalid classification entry in details.invalid_values, checking columns in SOP order. Derive required columns, allowed values, minimum rows, and the complete ERROR template from the source-derived knowledge.
