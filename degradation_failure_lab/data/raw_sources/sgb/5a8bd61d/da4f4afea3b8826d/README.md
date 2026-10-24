# pytorch-neural-style-transfer

This repository contains a concise PyTorch implementation of optimization-based neural style transfer.

## Relevant capability for this task

- optimizer choices: `lbfgs` and `adam`
- initialization choices: `random`, `content`, `style`
- default `data/content-images`, `data/style-images`, and `data/output-images` layout
- output image naming conventions and starting-weight recommendations encoded in code comments

## Notes

- The full repository performs heavy optimization with VGG models.
- For deterministic code_repo tasks, configuration planning is more stable than running full style transfer.
