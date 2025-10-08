import argparse
from typing import Tuple
from PIL import Image, ImageOps
import numpy as np


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    s = hex_str.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {hex_str}")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def crop_top_whitespace(
    img: Image.Image,
    tol: int = 245,
    row_frac: float = 0.99,
    alpha_tol: int = 5,
) -> Image.Image:
    """
    Remove contiguous top rows that are 'white-like' (near-white or transparent).

    - tol:      RGB >= tol is considered near-white (0..255).
    - row_frac: a row is 'whitespace' if >= row_frac of its pixels are white-like.
    - alpha_tol: for RGBA, alpha <= alpha_tol is treated as whitespace (transparent).

    Returns a new PIL Image with only the top trimmed.
    """
    # Apply EXIF orientation first, then convert to RGBA for a uniform array shape.
    img = ImageOps.exif_transpose(img)
    rgba = img.convert("RGBA")
    arr = np.asarray(rgba)  # (H, W, 4), uint8

    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    white_rgb = (r >= tol) & (g >= tol) & (b >= tol)
    transparent = (a <= alpha_tol)
    white_like = white_rgb | transparent

    # Fraction of white-like pixels per row
    row_white_frac = white_like.mean(axis=1)

    # First row that is NOT whitespace:
    nonwhite_idxs = np.where(row_white_frac < row_frac)[0]
    if len(nonwhite_idxs) == 0:
        # All rows look like whitespace; keep original (avoid empty image).
        y0 = 0
    else:
        y0 = int(nonwhite_idxs[0])

    if y0 <= 0:
        return img  # nothing to crop
    return img.crop((0, y0, img.width, img.height))


def stack_vertical(
    top: Image.Image,
    bottom: Image.Image,
    mode: str = "pad",  # "pad" or "resize"
    bg_rgb: Tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    Stack two images vertically after making widths compatible.

    mode="pad":   Do NOT resize; center-pad both to the max width.
    mode="resize":Resize both to the same width (the larger of the two) preserving aspect.
    """
    if mode not in {"pad", "resize"}:
        raise ValueError("mode must be 'pad' or 'resize'")

    # Work internally in RGBA to preserve transparency if any.
    top_rgba = top.convert("RGBA")
    bot_rgba = bottom.convert("RGBA")

    if mode == "resize":
        target_w = max(top_rgba.width, bot_rgba.width)
        def _resize_keep_w(im):
            if im.width == 0:
                return im
            scale = target_w / im.width
            new_h = max(1, int(round(im.height * scale)))
            return im.resize((target_w, new_h), Image.Resampling.LANCZOS)
        top_rgba = _resize_keep_w(top_rgba)
        bot_rgba = _resize_keep_w(bot_rgba)

        out_w = target_w
        out_h = top_rgba.height + bot_rgba.height
        bg = Image.new("RGBA", (out_w, out_h), color=(*bg_rgb, 255))
        bg.paste(top_rgba, (0, 0), top_rgba)
        bg.paste(bot_rgba, (0, top_rgba.height), bot_rgba)
        return bg

    # mode == "pad"
    out_w = max(top_rgba.width, bot_rgba.width)
    out_h = top_rgba.height + bot_rgba.height
    bg = Image.new("RGBA", (out_w, out_h), color=(*bg_rgb, 255))

    # Center each row horizontally
    x_top = (out_w - top_rgba.width) // 2
    x_bot = (out_w - bot_rgba.width) // 2
    bg.paste(top_rgba, (x_top, 0), top_rgba)
    bg.paste(bot_rgba, (x_bot, top_rgba.height), bot_rgba)
    return bg


def main():
    p = argparse.ArgumentParser(description="Trim top whitespace and stack two images vertically.")
    p.add_argument("image_top", help="Path to the first image (goes on top).")
    p.add_argument("image_bottom", help="Path to the second image (goes below).")
    p.add_argument("-o", "--out", default="stacked.png", help="Output image path (default: stacked.png)")
    p.add_argument("--tol", type=int, default=245, help="Near-white RGB threshold (0..255). Default: 245")
    p.add_argument("--row-frac", type=float, default=0.99, help="Row considered whitespace if >= this fraction of pixels are white-like. Default: 0.99")
    p.add_argument("--alpha-tol", type=int, default=5, help="Alpha <= this is treated as whitespace. Default: 5")
    p.add_argument("--mode", choices=["pad", "resize"], default="pad", help="Width reconcile mode. Default: pad")
    p.add_argument("--bg", default="#ffffff", help="Background color for padding as hex. Default: #ffffff")
    args = p.parse_args()

    bg_rgb = hex_to_rgb(args.bg)

    img_top = Image.open(args.image_top)
    img_bot = Image.open(args.image_bottom)

    top_trim = crop_top_whitespace(img_top, tol=args.tol, row_frac=args.row_frac, alpha_tol=args.alpha_tol)
    top_trim.save(args.image_top)
    bot_trim = crop_top_whitespace(img_bot, tol=args.tol, row_frac=args.row_frac, alpha_tol=args.alpha_tol)
    bot_trim.save(args.image_bottom)

    # stacked = stack_vertical(top_trim, bot_trim, mode=args.mode, bg_rgb=bg_rgb)

    # Save with a sane format given extension
    # stacked.save(args.out)
    # print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()