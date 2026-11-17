---
name: gif-background-removal
description: Advanced background removal from animated GIF files using AI matting and high-precision frame processing to generate clean transparent GIFs without residue. Use when the user asks to cleanly remove background from a GIF or make a GIF transparent with high quality.
---

# Advanced GIF Background Removal

A professional skill for removing complex or textured backgrounds from animated GIF images using AI-powered matting (such as `rembg`) to output clean, crisp transparent GIFs without halos or residue.

## When to Use
* The user wants to cleanly remove complex, textured, or gradient backgrounds from an animated GIF.
* Simple color tolerance leaves residue or halos and higher-precision AI matting is needed.
* The user asks for high-quality transparent GIFs.

## Workflow

1. **Analyze the Request:**
   - Identify the input animated GIF.
   - Determine that AI-powered foreground segmentation (`rembg` or advanced alpha matting) is required to handle complex textures and lighting.

2. **Generate and Execute Processing Code:**
   Write and execute a Python script utilizing `Pillow` and `rembg` (or advanced edge refinement) to:
   - Extract all frames from the input GIF.
   - Process each frame individually through the AI background removal model to extract precise alpha masks.
   - Clean up semi-transparent edge artifacts to prevent "ghosting" or residual halos.
   - Re-assemble and save the processed frames back into an optimized animated GIF with clean transparency (`dispose=2` or proper alpha handling).

3. **Deliver the Output:**
   - Provide the high-quality transparent GIF file for the user to download.

## Python Implementation Example (AI-powered with `rembg`)

```python
from PIL import Image
import io
from rembg import remove

def remove_gif_background_ai(input_path, output_path):
    img = Image.open(input_path)
    frames = []
    durations = []
    
    try:
        while True:
            durations.append(img.info.get('duration', 100))
            # Convert current frame to RGBA
            frame = img.copy().convert("RGBA")
            
            # Convert frame to bytes for rembg processing
            img_byte_arr = io.BytesIO()
            frame.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Apply AI background removal
            output_data = remove(img_byte_arr)
            processed_frame = Image.open(io.BytesIO(output_data)).convert("RGBA")
            
            frames.append(processed_frame)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=durations,
            loop=0,
            disposal=2
        )
