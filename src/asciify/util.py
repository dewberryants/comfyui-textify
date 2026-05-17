import numpy as np

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple

SOBEL_X = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
], dtype=np.float32)

SOBEL_Y = np.array([
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
], dtype=np.float32)


def rgb_to_gray(img: np.ndarray) -> np.ndarray:
    return (
        0.299 * img[..., 0] +
        0.587 * img[..., 1] +
        0.114 * img[..., 2]
    ).astype(np.float32)


def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    kh, kw = kernel.shape
    pad_h = kh // 2
    pad_w = kw // 2

    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
    out = np.zeros_like(image)

    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            region = padded[y:y+kh, x:x+kw]
            out[y, x] = np.sum(region * kernel)

    return out


def sobel_features(gray: np.ndarray) -> np.ndarray:
    gx = convolve2d(gray, SOBEL_X)
    gy = convolve2d(gray, SOBEL_Y)

    magnitude = np.sqrt(gx * gx + gy * gy)

    if magnitude.max() > 0:
        magnitude /= magnitude.max()

    return magnitude.astype(np.float32)


def measure_character_size(font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    bbox = font.getbbox("█")
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return w, h


def render_character_mask(
    char: str,
    font: ImageFont.FreeTypeFont,
    cell_w: int,
    cell_h: int
) -> np.ndarray:
    img = Image.new("L", (cell_w, cell_h), 0)
    draw = ImageDraw.Draw(img)

    bbox = font.getbbox(char)

    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]

    x = (cell_w - gw) // 2 - bbox[0]
    y = (cell_h - gh) // 2 - bbox[1]

    draw.text((x, y), char, fill=255, font=font)

    arr = np.array(img)
    return (arr > 127).astype(np.float32)


def precompute_glyph_data(
    font: ImageFont.FreeTypeFont,
    cell_w: int,
    cell_h: int,
    charset: str
) -> Dict[str, Dict]:
    glyphs = {}

    for ch in charset:
        mask = render_character_mask(ch, font, cell_w, cell_h)

        glyph_img = (mask * 255).astype(np.uint8)

        sobel = sobel_features(glyph_img.astype(np.float32))

        glyphs[ch] = {
            "mask": mask,
            "sobel": sobel
        }

    return glyphs


def match_character(
    tile_gray: np.ndarray,
    glyphs: Dict[str, Dict]
):
    tile_sobel = sobel_features(tile_gray)

    best_char = None
    best_score = float("inf")

    for ch, data in glyphs.items():
        glyph_sobel = data["sobel"]

        diff = tile_sobel - glyph_sobel
        score = np.mean(diff * diff)

        if score < best_score:
            best_score = score
            best_char = ch

    return best_char


def compute_fg_bg_colors(
    tile_rgb: np.ndarray,
    glyph_mask: np.ndarray,
    background: bool
):
    fg_mask = glyph_mask > 0.5
    bg_mask = ~fg_mask

    if np.any(fg_mask):
        fg = tile_rgb[fg_mask].mean(axis=0)
    else:
        fg = np.array([255, 255, 255])

    if background and np.any(bg_mask):
        bg = tile_rgb[bg_mask].mean(axis=0)
    else:
        bg = np.array([0, 0, 0])

    return tuple(np.uint8(fg)), tuple(np.uint8(bg))


def image_to_ascii(
    image: Image.Image,
    font_path: str,
    font_size: int,
    charset: str,
    background: bool
) -> Image.Image:

    font = ImageFont.truetype(font_path, font_size)
    cell_w, cell_h = measure_character_size(font)

    img_rgb = image.convert("RGB")
    img_np = np.array(img_rgb)

    H, W = img_np.shape[:2]

    cols = W // cell_w
    rows = H // cell_h

    out_w = cols * cell_w
    out_h = rows * cell_h

    glyphs = precompute_glyph_data(font, cell_w, cell_h, charset)

    out = Image.new("RGB", (out_w, out_h), (0, 0, 0))
    draw = ImageDraw.Draw(out)

    for row in range(rows):
        for col in range(cols):

            x0 = col * cell_w
            y0 = row * cell_h

            tile = img_np[
                y0:y0 + cell_h,
                x0:x0 + cell_w
            ]

            tile_gray = rgb_to_gray(tile)

            ch = match_character(tile_gray, glyphs)

            glyph_mask = glyphs[ch]["mask"]

            fg, bg = compute_fg_bg_colors(tile, glyph_mask, background)

            draw.rectangle(
                [x0, y0, x0 + cell_w, y0 + cell_h],
                fill=bg
            )

            # Draw glyph
            draw.text(
                (x0, y0),
                ch,
                font=font,
                fill=fg
            )
    return out
