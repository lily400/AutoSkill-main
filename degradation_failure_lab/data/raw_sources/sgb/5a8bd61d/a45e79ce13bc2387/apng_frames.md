# Pillow APNG notes

Use `Image.save(..., save_all=True, append_images=[...], format="PNG")` to create an animated PNG.
For this task, the important options are `disposal` and `blend`, because they change how later frames are composed.
After saving, reopen the APNG and iterate over frames with `ImageSequence.Iterator`.
Convert each frame to `RGBA` before reading pixel values.
