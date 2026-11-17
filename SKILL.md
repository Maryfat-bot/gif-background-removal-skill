---
name: gif-background-removal
description: Remove background from animated GIF files and generate transparent GIFs. Use when the user asks to remove background from a GIF, make a GIF transparent, or process animated image transparency.
---

# GIF Background Removal

A skill for removing the background from animated GIF images and outputting a transparent GIF.

## When to Use
* The user wants to remove the background of an animated GIF.
* The user wants to make a GIF transparent.
* The user provides an animated GIF and asks for background removal or chroma keying.

## Workflow

1. **Analyze the Request:**
   - Identify the source GIF provided by the user.
   - Determine if a specific background color needs to be keyed out (e.g., solid white, solid black, or chroma green/blue) or if automated background removal is required.

2. **Generate Processing Code:**
   Write and execute a Python script using standard libraries (`Pillow`, `imageio`, or `rembg` if available) to:
   - Extract all frames from the input GIF.
   - Process each frame to remove the background (either via color thresholding, alpha channel masking, or AI matting).
   - Re-assemble and save the frames back into an optimized animated GIF with transparency (`dispose=2` or proper alpha handling to prevent frame ghosting/artifacts).

3. **Deliver the Output:**
   - Provide the processed GIF file for the user to download.
   - Briefly explain the method used (e.g., color-based removal or frame-by-frame alpha masking).

## Python Implementation Example

```python
from PIL import Image

def remove_gif_background(input_path, output_path, bg_color=(255, 255, 255), tolerance=30):
    img = Image.open(input_path)
    frames = []
    
    try:
        while True:
            # Convert frame to RGBA
            frame = img.copy().convert("RGBA")
            datas = frame.getdata()
            
            new_data = []
            for item in datas:
                # Check if the pixel is close to the target background color
                if (abs(item[0] - bg_color[0]) < tolerance and
                    abs(item[1] - bg_color[1]) < tolerance and
                    abs(item[2] - bg_color[2]) < tolerance):
                    # Make transparent
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            frame.putdata(new_data)
            frames.append(frame)
            
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=img.info.get('duration', 100),
            loop=0,
            transparency=0
        )