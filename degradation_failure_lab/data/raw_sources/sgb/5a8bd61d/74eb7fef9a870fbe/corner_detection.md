# Harris corner detection notes

`corner_harris` produces a response image of the same spatial shape as the input.
`corner_peaks` extracts coordinate pairs from that response map.
For reproducible output in this task, sort the returned coordinates in row-major order before truncating the list.
