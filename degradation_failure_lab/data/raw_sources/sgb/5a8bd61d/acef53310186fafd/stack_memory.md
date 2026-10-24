# librosa stack_memory notes

`librosa.feature.stack_memory` augments a feature matrix with delayed or advanced context.
A negative `delay` means future frames are pulled into the stacked representation.
For this task, keep the input array in feature-major shape and report values from the returned stacked matrix directly.
