# Textify

Converts the image into ASCII art / text using the given font file (.ttf or .otf). Obviously, this looks much better with
monospaced fonts.

## Inputs

| Parameter   | Type   | Description                                         |
|-------------|--------|-----------------------------------------------------|
| `image`     | IMAGE  | The input image to process                          |
| `font`      | STRING | Path to a valid font file or an installed font name |
| `font_size` | INT    | The font size to use                                |
| `charset`   | STRING | The character set to use.                           |
| `mode`      | select | Choose between modes                                |
| `dither`    | BOOL   | Whether to use dithering when shape matching        |

## Outputs

| Output  | Type  | Description                |
|---------|-------|----------------------------|
| `IMAGE` | IMAGE | The processed output image |
