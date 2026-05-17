import torch
import numpy as np

from PIL import Image

from .util import image_to_ascii

class ImageToAscii:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", { "tooltip": "This is an image"}),
                "font": ("STRING", {
                    "tooltip": "Path to a valid .ttf or .otf file",
                    "default": "consola.ttf"
                }),
                "font_size": ("INT", {
                    "default": 6,
                    "min": 4,
                    "max": 256,
                    "step": 1
                }),
                "charset": ("STRING", {
                    "tooltip": "The characters to use. By default, this is all standard ASCII characters.",
                    "default": " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]"
                               "^_`abcdefghijklmnopqrstuvwxyz{|}~",
                    "multiline": True
                }),
                "background": ("BOOLEAN", {
                    "tooltip": "Whether to calculate a background color or not",
                    "default": False
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("Image", "Text")

    FUNCTION = "convert"

    CATEGORY = "Asciify"

    def convert(self, image: torch.Tensor, font: str, font_size: int, charset: str, background: bool):
        image_np = image.cpu().numpy()
        work = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))

        converted = image_to_ascii(work, font, font_size, charset, background)
        converted = torch.tensor(np.array(converted).astype(np.float32) / 255.0)

        return torch.unsqueeze(converted, 0), ""


class PreviewAscii:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "String": ("Text", { "tooltip": "Pass ASCII Text in here"}),
                "Font": ("STRING", {
                    "tooltip": "Path to a valid .ttf or .otf file",
                    "default": "consola.ttf"
                }),
                "Font Size": ("INT", {
                    "default": 6,
                    "min": 4,
                    "max": 256,
                    "step": 1})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("Image",)
    DESCRIPTION = ""
    FUNCTION = "convert"

    CATEGORY = "Asciify"

    def _convert(self, text: str, font: str, font_size: int):
        image: torch.Tensor = torch.zeros((1, 1, 1, 3))
        return (image,)


NODE_CLASS_MAPPINGS = {
    "ImageToAscii": ImageToAscii,
    "Preview Ascii": PreviewAscii
}
