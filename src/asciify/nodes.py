import torch
import random

import numpy as np

from PIL import Image, ImageDraw, ImageFont


def get_largest_pixel_size(font, charset):
    x, y = 1, 1
    for char in charset:
        a, b, c, d = font.getbbox(char)
        x = max(x, round(c - a))
        y = max(y, round(d - b))
    return x, y

def prepare_bitmaps(font, charset, pixel_size):
    bitmaps = []
    for char in charset:
        a, b, c, d = font.getbbox(char)
        tmp = Image.new("1", pixel_size, 0)
        draw = ImageDraw.Draw(tmp)
        draw.text((-a, -b), char, 1, font)
        bitmaps.append([x for x in tmp.getdata()])
    return np.array(bitmaps, dtype='bool')

def extract_color(im, bm):
    tmp = np.array(im)
    mask = bm.reshape(tmp.shape[:2])
    if not mask.any():
        return tuple(tmp.mean(axis=(0, 1)).astype("int"))
    ret = tuple(tmp[mask].mean(axis=0).astype("int"))
    return ret

def textify(image: Image, font: str, font_size: int, charset: str, mode=1, dither=True):
    Font = ImageFont.truetype(font, font_size)
    iw, ih = image.size
    pw, ph = get_largest_pixel_size(Font, charset)
    bitmaps = prepare_bitmaps(Font, charset, (pw, ph))

    image_bw = image.convert("1", dither=3 if dither else 0)

    output = Image.new("RGBA", image.size)
    output_draw = ImageDraw.Draw(output)

    counter = 0

    for row in range(ih // ph):
        if row * ph > image.height:
            break
        for col in range(iw // pw):
            if col * pw > image.width:
                continue

            pos = a, b, c, d = (col * pw, row * ph, col * pw + pw, row * ph + ph)
            current = image.crop(pos)
            current_bw = image_bw.crop(pos)

            if mode == 1: # Shape matching
                bm = np.array(current_bw.getdata(), dtype='bool')
                sim = np.sum(bitmaps == bm, axis=1)
                fg_rgb = extract_color(current, bitmaps[np.argmax(sim)])
                char = charset[np.argmax(sim)]
            elif mode == 2: # Characters in order
                fg_rgb = extract_color(current, bitmaps[counter])
                char = charset[counter]
                counter += 1
                if counter == len(charset):
                    counter = 0
            else: # Random Character
                idx = random.randint(0, len(charset) - 1)
                fg_rgb = extract_color(current, bitmaps[idx])
                char = charset[idx]
            output_draw.text((a, b), char, tuple(fg_rgb), Font)
    return output


class Textify:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", { "tooltip": "This is an image"}),
                "font": ("STRING", {
                    "tooltip": "Path to a valid .ttf or .otf file.",
                    "default": "consola.ttf"
                }),
                "font_size": ("INT", {
                    "default": 6,
                    "min": 4,
                    "max": 256,
                    "step": 1
                }),
                "charset": ("STRING", {
                    "tooltip": "The characters to use. By default, this is all standard ASCII characters. Be aware that"
                               " when shape matching, the empty space and very small characters will usually lessen"
                               " color depth in dark areas of the image.",
                    "default": "!\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]"
                               "^_`abcdefghijklmnopqrstuvwxyz{|}~",
                    "multiline": True
                }),
                "mode": (["Match Shape", "Ordered", "Random"], {
                    "tooltip": "Match Shape uses a simple bitmap matching algorithm to determine which character to"
                               "use from the charset. Ordered uses the charset in order,"
                               "while random chooses random characters from the set.",
                }),
                "dither": ("BOOLEAN", {
                    "tooltip": "Whether to use dithering to get more detailed shapes to match (does nothing for"
                               " ordered and random modes).",
                    "default": True
                })
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("Image",)

    FUNCTION = "convert"

    CATEGORY = "Asciify"

    def convert(self, image: torch.Tensor, font: str, font_size: int, charset: str, mode: int, dither: bool):
        image_np = image.cpu().numpy()
        work = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))
        mode_dict = {"Match Shape": 1, "Ordered": 2, "Random": 3}

        converted = textify(work, font, font_size, charset, mode_dict[mode], dither)
        converted = torch.tensor(np.array(converted).astype(np.float32) / 255.0)

        return torch.unsqueeze(converted, 0), ""

NODE_CLASS_MAPPINGS = {
    "Textify": Textify
}
