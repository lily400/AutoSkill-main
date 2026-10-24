# soundfile dtype conversion notes

`soundfile.read(path, dtype="int32")` converts decoded samples to 32-bit integers.
For this task, compute the summary from the actual returned array instead of assuming a normalization rule.
Flatten the array before taking the first values so the output format is independent of channel count.
