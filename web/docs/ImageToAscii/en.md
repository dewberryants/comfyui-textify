# Image To Ascii

Converts the image into ASCII art using the given font file (.ttf or .otf). Obviously, this looks much better with
monospaced fonts.

Depending on the size of the image and character set, this can take quite some time, as it uses Sobel for
glyph matching, which is accurate but slow.

## Inputs

| Parameter        | Type   | Description                |
|------------------|--------|----------------------------|
| `image`          | IMAGE  | The input image to process |
| `int_field`      | INT    | An integer parameter       |
| `float_field`    | FLOAT  | A float parameter          |
| `string_field`   | STRING | A text input               |
| `print_to_screen`| select | Enable/disable console output |

## Outputs

| Output  | Type  | Description                |
|---------|-------|----------------------------|
| `IMAGE` | IMAGE | The processed output image |
