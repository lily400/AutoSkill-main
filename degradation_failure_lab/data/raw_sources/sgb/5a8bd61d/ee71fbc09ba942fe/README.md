# VideoPose3D

3D human pose estimation in video with temporal convolutions and semi-supervised training.

> Efficient 3D pose estimation from 2D keypoint sequences using temporal dilated convolutions.

## Features

- Lift 2D keypoints to 3D poses using temporal convolutions
- Support for causal (real-time) and non-causal modes
- Semi-supervised training with unlabeled video
- Visualization tools for 3D pose rendering
- Pretrained models for Human3.6M dataset

## Installation

```bash
git clone https://github.com/facebookresearch/VideoPose3D.git
cd VideoPose3D
pip install -r requirements.txt
```

## Quick Start

### Inference with pretrained model

```bash
python run.py -k cpn_ft_h36m_dbb -arc 3,3,3,3,3
```

### With causal convolutions

```bash
python run.py -k cpn_ft_h36m_dbb -arc 3,3,3,3,3 --causal
```

## Architecture

The model uses dilated temporal convolutions over 2D keypoint sequences. The default architecture uses filter widths of `[3,3,3,3,3]` with 1024 channels.

### Keypoint Sources

- `cpn_ft_h36m_dbb`: CPN fine-tuned on Human3.6M
- `detectron_ft_h36m`: Detectron2 keypoints

### Evaluation

```bash
python run.py -k cpn_ft_h36m_dbb -arc 3,3,3,3,3 --evaluate pretrained_h36m_cpn.bin
```

## Citation

```
@inproceedings{pavllo2019videopose3d,
  title={3D human pose estimation in video with temporal convolutions and semi-supervised training},
  author={Pavllo, Dario and Feichtenhofer, Christoph and Grangier, David and Auli, Michael},
  booktitle={CVPR},
  year={2019}
}
```

## License

Attribution-NonCommercial 4.0 International
