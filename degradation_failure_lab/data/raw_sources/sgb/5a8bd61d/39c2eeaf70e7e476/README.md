# Piper

A fast, local neural text-to-speech system that embeds espeak-ng for phonemization.

## Installation

```bash
pip install piper-tts
```

## Usage

### Command-Line

```bash
# Download a voice
python3 -m piper.download_voices en_US-lessac-medium

# Synthesize speech
python3 -m piper -m en_US-lessac-medium.onnx -f output.wav -- 'Welcome to piper!'
```

### Web Server

```bash
python3 -m piper.http_server --model en_US-lessac-medium.onnx
```

### Voice Models

Download voices from [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/main).

Each voice consists of:
- `.onnx` model file (VITS neural network)
- `.onnx.json` config file (metadata)

Voice naming convention: `{language_code}-{speaker}-{quality}.onnx`

Example: `en_US-lessac-medium.onnx`

Available qualities: `x_low`, `low`, `medium`, `high`

## License

GPL-3.0
