# Transparent Background

Background remover that works on any image.

## Features

- Remove background from images with a single line of code
- Support for multiple output types: rgba, green screen, blur, overlay, white, alpha map
- Fast mode with ONNX optimization
- JIT compilation support
- Works with both images and videos
- CLI and Python API

## Installation

```bash
pip install transparent-background
```

## Usage

### Python

```python
from transparent_background import Remover

remover = Remover()  # default mode
remover = Remover(mode='fast')  # ONNX mode

# Process image
img = Image.open('input.jpg').convert('RGB')
out = remover.process(img)  # default: rgba output
out = remover.process(img, type='green')  # green screen
out = remover.process(img, type='map')  # alpha map only
```

### CLI

```bash
transparent-background --source input.jpg --dest output --type rgba
transparent-background --source input.jpg --dest output --type map
transparent-background --source video.mp4 --dest output --type rgba
```

### Options

- `--type`: Output type (`rgba`, `green`, `blur`, `overlay`, `white`, `map`)
- `--fast`: Use ONNX for faster inference
- `--jit`: Enable JIT compilation
- `--ckpt`: Custom checkpoint path

## Model

Uses InSPyReNet architecture for accurate image matting. The model processes images at a configurable resolution (default 1024) and uses guided filtering for alpha refinement.

## Citation

```
@InProceedings{kim2022revisiting,
  title={Revisiting Image Pyramid Structure for High Resolution Salient Object Detection},
  author={Kim, Taehun and others},
  year={2022}
}
```

## License

MIT License
