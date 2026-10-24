# soundfile seek notes

`SoundFile.tell()` reports the current frame index.
`SoundFile.seek(offset, whence=1)` can move the cursor relative to the current position.
In this task, the second read intentionally overlaps the end of the first read.
Use `always_2d=True` so the returned frame summaries have a stable shape.
