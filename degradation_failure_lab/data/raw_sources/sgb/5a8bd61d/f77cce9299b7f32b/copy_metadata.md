# SoundFile copy_metadata

This task checks the metadata helper on `soundfile.SoundFile`.

The important behavior is:
- open the file with `soundfile.SoundFile(...)`
- call `copy_metadata()` to get a dictionary-like snapshot of available metadata
- extract the requested fields from that result
