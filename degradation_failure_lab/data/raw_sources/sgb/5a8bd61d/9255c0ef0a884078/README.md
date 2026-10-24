# Bringing Old Photos Back to Life

**Official PyTorch implementation** of *Bringing Old Photos Back to Life* (CVPR 2020 Oral).

> Old photo restoration via deep latent space translation.

Microsoft Research Asia | City University of Hong Kong | UESTC

## Highlights

- Restores old photos suffering from degradation (blur, noise, color fading) and structured damage (scratches, film grain)
- Two-stage pipeline: global restoration + face enhancement
- Scratch detection and removal as optional preprocessing
- High-resolution support via patch-based processing
- GUI interface for interactive use

## Installation

```bash
git clone https://github.com/nicholasgasior/Synchronized-BatchNorm-PyTorch
cp -r Synchronized-BatchNorm-PyTorch/sync_batchnorm .

# Download pretrained models
cd Face_Enhancement/models/networks/
git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
cp -r Synchronized-BatchNorm-PyTorch/sync_batchnorm .

# Get face landmark model
cd Face_Detection/
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
```

## Usage

### Full pipeline (with scratch removal)
```bash
python run.py --input_folder [test_image_folder_path] \
              --output_folder [output_path] \
              --GPU 0 \
              --with_scratch
```

### Without scratch removal
```bash
python run.py --input_folder [test_image_folder_path] \
              --output_folder [output_path] \
              --GPU 0
```

### Scratch detection only
```bash
cd Global/
python detection.py --test_path [test_image_folder_path] \
                    --output_dir [output_path] \
                    --input_size full_size \
                    --GPU 0
```

### High-resolution mode
```bash
python run.py --input_folder [test_image_folder_path] \
              --output_folder [output_path] \
              --GPU 0 \
              --with_scratch \
              --HR
```

## Training

The training pipeline involves:
1. VAE training for domain translation
2. Mapping network training between latent spaces
3. Scratch detection network training

## Models

- **Global restoration**: Handles overall image quality improvement
- **Face enhancement**: Improves facial regions with progressive generation
- **Scratch detection**: Identifies damaged regions for targeted restoration

## Citation

```
@inproceedings{wan2020bringing,
  title={Bringing Old Photos Back to Life},
  author={Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang},
  booktitle={IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2020}
}
```

## License

MIT License
