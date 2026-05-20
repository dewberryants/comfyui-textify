"""Top-level package for asciify."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """Dominik Behrens"""
__email__ = "dewberryants@gmail.com"
__version__ = "0.0.1"

from .src.textify.node import NODE_CLASS_MAPPINGS

WEB_DIRECTORY = "./web"
