# Kokoro

Kokoro is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient.

## Installation

```bash
pip install kokoro>=0.9.4 soundfile
apt-get -qq -y install espeak-ng > /dev/null 2>&1
```

## Basic Usage

```python
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')
text = 'Hello, this is a test of the Kokoro text to speech system.'

generator = pipeline(text, voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    sf.write(f'{i}.wav', audio, 24000)
```

## Language Codes

| Code | Language |
|------|----------|
| `a` | American English |
| `b` | British English |
| `e` | Spanish |
| `f` | French |
| `h` | Hindi |
| `i` | Italian |
| `j` | Japanese |
| `p` | Brazilian Portuguese |
| `z` | Mandarin Chinese |

## Advanced Usage

```python
generator = pipeline(
    text,
    voice='af_heart',
    speed=1,
    split_pattern=r'\n+'
)

for i, (gs, ps, audio) in enumerate(generator):
    print(i)      # index
    print(gs)     # graphemes/text
    print(ps)     # phonemes
    sf.write(f'{i}.wav', audio, 24000)
```

## Voices

Voice names follow a pattern: the first letter indicates language, the second indicates gender (m=male, f=female), then an underscore and a descriptive name. Example: `af_heart` (American female, heart style).

## Key Dependencies

- `misaki` — grapheme-to-phoneme conversion
- `soundfile` — audio file I/O
- `espeak-ng` — phoneme backend

## License

Apache-2.0
