# F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching

[![python](https://img.shields.io/badge/Python-3.10-brightgreen)](https://github.com/SWivid/F5-TTS)
[![arXiv](https://img.shields.io/badge/arXiv-2410.06885-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2410.06885)
[![demo](https://img.shields.io/badge/GitHub-Demo-blue)](https://swivid.github.io/F5-TTS)

F5-TTS is a non-autoregressive text-to-speech system based on flow matching with Diffusion Transformer (DiT). It supports:

- **F5-TTS**: Diffusion Transformer with ConvNeXt V2, faster trained and inference.
- **E2 TTS**: Flat-UNet Transformer, closest reproduction.
- **Sway Sampling**: Improved inference strategy for better quality.

## Installation

```bash
# Create environment
conda create -n f5-tts python=3.10
conda activate f5-tts

# Install PyTorch (pick one)
pip install torch torchaudio  # NVIDIA GPU
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu  # CPU

# Install F5-TTS
pip install f5-tts
```

## Inference

### 1) Gradio App

```bash
f5-tts_infer-gradio
```

### 2) CLI Inference

```bash
# Basic usage
f5-tts_infer-cli \
--model F5TTS_v1_Base \
--ref_audio "ref.wav" \
--ref_text "Reference transcription." \
--gen_text "Text to synthesize."

# With config file
f5-tts_infer-cli -c custom.toml
```

### 3) More instructions

See [inference guide](src/f5_tts/infer/SHARED.md).

## Training

```bash
# Prepare dataset and finetune
f5-tts_finetune-gradio
```

## Evaluation

```bash
# Seed-TTS test set evaluation
f5-tts_eval
```

## Acknowledgements

- [E2-TTS](https://arxiv.org/abs/2406.18009) for foundational architecture.
- [Emilia](https://huggingface.co/datasets/amphion/Emilia-Dataset) and [Wenetspeech4TTS](https://huggingface.co/datasets/Wenetspeech4TTS/WenetSpeech4TTS) for datasets.
- [Vocos](https://huggingface.co/charactr/vocos-mel-24khz) for vocoder.

## Citation

```bibtex
@article{chen2024f5tts,
  title={F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching},
  author={Yushen Chen and others},
  journal={arXiv preprint arXiv:2410.06885},
  year={2024}
}
```
