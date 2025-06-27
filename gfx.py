import io
from functools import lru_cache
from typing import Tuple
import sys
import pygame
from cairosvg import svg2png
from PIL import Image


def _rasterize(svg_bytes: bytes, size: tuple[int, int]) -> pygame.Surface:
    """
    Rasterize SVG bytes to a Pygame surface of the given pixel size.
    Falls back to Pillow for PNG decoding since SDL_Image isn’t built with PNG support.
    """
    width, height = size
    # 1. Render SVG→PNG bytes
    png_bytes = svg2png(bytestring=svg_bytes,
                        output_width=width,
                        output_height=height)
    # 2. Decode PNG via Pillow into an RGBA image
    pil_img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    w, h = pil_img.size
    raw_data = pil_img.tobytes()  # contiguous RGBA bytes
    # 3. Create a Pygame surface from those raw pixels
    surface = pygame.image.fromstring(raw_data, (w, h), "RGBA")
    return surface.convert_alpha()

@lru_cache(maxsize=64)
def load_svg(path: str, pixel_size: int) -> pygame.Surface:
    """Load an SVG file and rasterize it to a square surface (pixel_size×pixel_size).

    Results are cached (path, pixel_size) to avoid repeated rasterisation.
    """
    with open(path, "rb") as f:
        svg_data = f.read()
    return _rasterize(svg_data, (pixel_size, pixel_size))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((140, 140))
    img = load_svg('icons/attack.svg', 120);
    screen.blit(img, (10, 10));
    pygame.display.flip()
    pygame.time.wait(1500);
    pygame.quit();
    sys.exit()