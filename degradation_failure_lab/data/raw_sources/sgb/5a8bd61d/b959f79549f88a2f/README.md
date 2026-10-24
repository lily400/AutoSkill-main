# DeOldify

The mission of this project is to colorize and restore old images and film footage.

## About DeOldify

We're particularly focused on photorealistic results. Key improvements:
- Elimination of glitches and artifacts
- Better skin rendering
- More photorealistic output
- Less "blue bias"
- Good video support
- NoGAN training technique

## Why Three Models?

- **Artistic** - Highest quality and vibrance but may require fiddling with render_factor. Uses resnet34 backbone. Trained with 32% ImageNet data (12.5 hours GAN training).
- **Stable** - Best for landscapes and portraits, fewer artifacts. Uses resnet101 backbone. Trained with 7% ImageNet data (3 hours GAN training).
- **Video** - Optimized for smooth, flicker-free video. Same architecture as stable. Trained on 2.2% ImageNet data (1 hour GAN training).

## What is NoGAN?

NoGAN is a new type of GAN training that combines benefits of GAN training while minimizing direct GAN time. Steps:
1. Train generator conventionally with feature loss
2. Train critic as binary classifier on generated vs real images
3. Train together in GAN setting

## Technical Details

Combines Self-Attention GAN, Two Time-Scale Update Rule, NoGAN, and Perceptual Loss based on VGG16.

## Getting Started

Colab notebooks are the easiest approach. For local setup: requires a beefy GPU (11GB+ for training, 4GB+ for inference), Linux (Ubuntu), and Anaconda install:
```bash
conda env create -f environment.yml
```

## Pretrained Weights

Generator weights go in the `/models/` folder:
- Artistic model weights
- Stable model weights
- Video model weights

## License

All code is under the MIT license. Model weights are also released under MIT.
