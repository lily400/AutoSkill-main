# Coqui TTS

Coqui TTS is a library for advanced Text-to-Speech generation. It provides pretrained models in 1100+ languages and supports training new models.

## Installation

```bash
pip install torch torchaudio
pip install coqui-tts
```

## Python API

```python
from TTS.api import TTS

# List available models
print(TTS().models)

# Single speaker model
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
tts.tts_to_file(text="Hello world!", file_path="output.wav")

# Multi-speaker + multilingual
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
tts.tts_to_file(text="Hello!", speaker_wav="ref.wav", language="en", file_path="output.wav")
```

## CLI

```bash
# List models
tts --list_models

# Synthesize
tts --text "Text for TTS" --out_path output.wav

# With specific model
tts --text "Text" --model_name "tts_models/en/ljspeech/glow-tts" --out_path output.wav

# Multi-speaker
tts --model_name "tts_models/en/vctk/vits" --list_speaker_idxs
tts --text "Text" --model_name "tts_models/en/vctk/vits" --speaker_idx p225 --out_path output.wav
```

## Supported Models

### Spectrogram Models
Tacotron, Tacotron2, Glow-TTS, FastPitch, SpeedySpeech, etc.

### End-to-End Models
VITS, XTTS, YourTTS, Bark, Tortoise

### Vocoders
HiFiGAN, MelGAN, WaveRNN, WaveGrad, UnivNet, etc.

### Voice Conversion
FreeVC, kNN-VC, OpenVoice

## License

MPL 2.0
