#!/usr/bin/env python3
"""Remove backgrounds from GIF frames and save a transparent GIF."""

from __future__ import annotations

import argparse
import io
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import new_session, remove


def extract_frames(input_path: Path):
    source = Image.open(input_path)
    size = source.size
    frame_count = getattr(source, "n_frames", 1)
    loop = source.info.get("loop")
    frames = []
    durations = []

    for index in range(frame_count):
        source.seek(index)
        durations.append(source.info.get("duration", 100))
        frame = source.convert("RGBA").copy()
        if frame.size != size:
            raise ValueError(f"Unexpected canvas size in frame {index}")
        frames.append(frame)

    return frames, durations, loop, size


def segment_frames(frames, model_name: str, alpha_matting: bool):
    session = new_session(model_name, providers=["CPUExecutionProvider"])
    cutouts = []

    for index, frame in enumerate(frames):
        buffer = io.BytesIO()
        frame.save(buffer, format="PNG")
        result = remove(
            buffer.getvalue(),
            session=session,
            alpha_matting=alpha_matting,
        )
        cutout = Image.open(io.BytesIO(result)).convert("RGBA")
        if cutout.size != frame.size:
            raise ValueError(f"Segmentation changed frame {index}'s dimensions")
        cutouts.append(cutout)

    return cutouts


def shared_palette(frames):
    samples = []
    rng = np.random.default_rng(17)
    for frame in frames:
        rgba = np.asarray(frame)
        pixels = rgba[:, :, :3][rgba[:, :, 3] > 32]
        if len(pixels) > 15_000:
            pixels = pixels[rng.choice(len(pixels), 15_000, replace=False)]
        if len(pixels):
            samples.append(pixels)

    if not samples:
        raise RuntimeError("No visible subject pixels were found")

    pixels = np.concatenate(samples, axis=0)
    sample_image = Image.fromarray(pixels.reshape(1, -1, 3).astype(np.uint8))
    quantized = sample_image.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()[:768]
    palette += [0] * (768 - len(palette))
    palette[765:768] = [255, 0, 255]  # Index 255 is reserved for transparency.

    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette)
    return palette, palette_image


def encode_frames(frames, size, palette, palette_image):
    encoded = []
    for frame in frames:
        rgba = np.asarray(frame)
        indexed = frame.convert("RGB").quantize(
            palette=palette_image,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        indices = np.asarray(indexed).copy()
        indices[rgba[:, :, 3] < 128] = 255
        gif_frame = Image.frombytes("P", size, indices.astype(np.uint8).tobytes())
        gif_frame.putpalette(palette)
        encoded.append(gif_frame)
    return encoded


def save_checkerboard_preview(output_path: Path):
    result = Image.open(output_path)
    size = result.size
    frame_count = getattr(result, "n_frames", 1)
    columns = min(3, frame_count)
    rows = (frame_count + columns - 1) // columns
    preview = Image.new("RGB", (size[0] * columns, size[1] * rows), "white")

    for index in range(frame_count):
        result.seek(index)
        rgba = np.asarray(result.convert("RGBA"))
        height, width = rgba.shape[:2]
        yy, xx = np.indices((height, width))
        checker = ((xx // 12 + yy // 12) % 2)[:, :, None]
        background = np.where(checker == 0, 210, 245).astype(np.uint8)
        alpha = rgba[:, :, 3:4].astype(np.float32) / 255
        composite = (rgba[:, :, :3] * alpha + background * (1 - alpha)).astype(np.uint8)
        x = (index % columns) * size[0]
        y = (index // columns) * size[1]
        preview.paste(Image.fromarray(composite), (x, y))

    preview_path = output_path.with_name(output_path.stem + "_preview.png")
    preview.save(preview_path)
    return preview_path


def remove_gif_background(input_path: Path, output_path: Path, model_name: str, alpha_matting: bool):
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if input_path == output_path:
        raise ValueError("Choose a new output path; the input file must remain untouched")
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames, durations, loop, size = extract_frames(input_path)
    cutouts = segment_frames(frames, model_name, alpha_matting)
    palette, palette_image = shared_palette(cutouts)
    encoded = encode_frames(cutouts, size, palette, palette_image)

    save_options = {
        "save_all": True,
        "append_images": encoded[1:],
        "duration": durations,
        "transparency": 255,
        "disposal": 2,
        "optimize": False,
    }
    if loop is not None:
        save_options["loop"] = loop
    encoded[0].save(output_path, **save_options)

    result = Image.open(output_path)
    if result.size != size or getattr(result, "n_frames", 1) < 1:
        raise RuntimeError("The output GIF failed basic validation")
    preview_path = save_checkerboard_preview(output_path)
    return getattr(result, "n_frames", 1), preview_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source animated GIF")
    parser.add_argument("output", type=Path, help="destination transparent GIF")
    parser.add_argument("--model", default="u2net", help="rembg model name (default: u2net)")
    parser.add_argument(
        "--alpha-matting",
        action="store_true",
        help="refine soft edges; inspect the result because it can remove fine details",
    )
    args = parser.parse_args()

    frame_count, preview = remove_gif_background(
        args.input,
        args.output,
        model_name=args.model,
        alpha_matting=args.alpha_matting,
    )
    print(f"Saved {args.output} ({frame_count} frame(s))")
    print(f"Checkerboard preview: {preview}")


if __name__ == "__main__":
    main()
