# FunASR

FunASR is an end-to-end speech recognition toolkit covering speech recognition, VAD, punctuation, speaker tasks, and related postprocessing utilities.

## Relevant capability for this task

- Python entrypoint via `AutoModel`
- Rich transcription output with language, event, and emotion special tokens
- Postprocessing utility `funasr.utils.postprocess_utils.rich_transcription_postprocess`
- Timestamp and sentence postprocessing helpers in `funasr.utils`

## Notes

- The full toolkit often downloads or loads pretrained models for inference tasks.
- The rich transcription postprocessing utilities are deterministic string transformations and do not require model weights.
- These utilities map FunASR special tokens such as `<|en|>`, `<|Applause|>`, and `<|HAPPY|>` into human-readable text with event or emotion markers.
