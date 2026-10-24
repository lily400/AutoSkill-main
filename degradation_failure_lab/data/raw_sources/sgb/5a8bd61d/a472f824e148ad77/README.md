# invisible-watermark

InvisibleWatermark is a Python library and CLI for embedding and decoding hidden watermarks in images.

## Relevant capability for this task

- `WatermarkEncoder` and `WatermarkDecoder`
- default frequency method `dwtDct`
- bytes watermark payloads
- image-only decoding without the original carrier

## Notes

- The project also includes slower or heavier variants such as `dwtDctSvd` and `rivaGan`.
- The default `dwtDct` path is the practical CPU-friendly option described by the project.
- Carrier images should be larger than `256x256`.
