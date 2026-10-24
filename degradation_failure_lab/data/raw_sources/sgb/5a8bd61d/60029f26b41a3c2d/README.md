# AnimeGANv3

Paper Title: A Novel Double-Tail Generative Adversarial Network for Fast Photo Animation.
## Let's use AnimeGANv3 to produce our own animation.

## Usage

* Official online demo is released in Hugging Face Spaces.
* Download this repository and use AnimeGANv3's UI tool and pre-trained *.onnx to turn your photos into anime.

* Installation
  1. Clone repo
      ```bash
      git clone https://github.com/TachibanaYoshino/AnimeGANv3.git
      cd AnimeGANv3
      ```
  1. Install dependent packages
      ```bash
      pip install -r requirements.txt
      ```
  1. Inference with *.onnx
      ```bash
      python deploy/test_by_onnx.py -i inputs/imgs/ -o output/results -m deploy/AnimeGANv3_Hayao_36.onnx
      ```
  1. video to anime with *.onnx
      ```bash
      python tools/video2anime.py -i inputs/vid/1.mp4 -o output/results -m deploy/AnimeGANv3_Hayao_36.onnx
      ```

## Landscape Demos
### Photo to Hayao Style
### Photo to Shinkai Style

## Portrait Style Demos

Available portrait styles include:
- Face to USA cartoon style
- Face to Disney cartoon style
- Face to Ghibli-c1 style
- Face to Trump style
- Face to Arcane style
- Portrait to comic style
- Face to Kpop style
- Portrait to Oil-painting style
- Portrait to Cute style
- Portrait to Pixar style
- Portrait to Sketch-0 style
- Portrait to 8bit style
- Face to portrait sketch

## Train

#### 1. Download dataset and pretrained vgg19
1. vgg19
2. Hayao dataset
3. Shinkai dataset
4. photo dataset

#### 2. Do edge_smooth
```bash
    cd tools && python edge_smooth.py --dataset Hayao --img_size 256
```

#### 3. Do superPixel
```bash
    cd tools && python visual_superPixel_seg_image.py
```

#### 4. Train
```bash
    python train.py --style_dataset Hayao --init_G_epoch 5 --epoch 100
```

## License
This repo is made freely available to academic and non-academic entities for non-commercial purposes such as academic research, teaching, scientific publications.

## Author
Asher Chan
