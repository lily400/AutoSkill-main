# Diffusers

Diffusers is the go-to library for state-of-the-art pretrained diffusion models for generating images, audio, and 3D structures.

## Installation

```bash
pip install diffusers[torch]
```

## Quickstart

```python
from diffusers import DiffusionPipeline
import torch

pipeline = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipeline.to("cuda")
pipeline("An image of a squirrel in Picasso style").images[0]
```

## Custom Diffusion System

```python
from diffusers import DDPMScheduler, UNet2DModel
import torch

scheduler = DDPMScheduler.from_pretrained("google/ddpm-cat-256")
model = UNet2DModel.from_pretrained("google/ddpm-cat-256").to("cuda")
scheduler.set_timesteps(50)

noise = torch.randn((1, 3, 256, 256), device="cuda")
input = noise
for t in scheduler.timesteps:
    with torch.no_grad():
        noisy_residual = model(input, t).sample
        prev = scheduler.step(noisy_residual, t, input).prev_sample
        input = prev
```

## Supported Tasks

- Text-to-Image: Stable Diffusion, SDXL, Kandinsky
- Image-to-Image: ControlNet, InstructPix2Pix
- Inpainting, Super Resolution, Video Generation

## License

Apache 2.0
