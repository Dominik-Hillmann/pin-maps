# Internal modules
from draw.ImageTransform import ImageTransform
# External imports
from PIL import Image, ImageDraw
# Typing
from typing import Tuple

class BackgroundDeletion(ImageTransform):
    
    def __init__(self, px_dist: int = 50, replace_val: Tuple[int, int, int, int] = (255, 255, 255, 0)):
        self.px_dist = px_dist
        self.replace_val = replace_val


    def transform(heraldry: Image.Image) -> Image.Image:
        """Removes background of the heraldry if it is not transparent.

        Args:
            heraldry (Image.Image): The image from which background should be removed.
            px_dist (int, optional): Max. pixel distance in the flood fill algorithm. Defaults to 50.

        Returns:
            Image.Image: The image with transparent background.
        """
        
        heraldry = heraldry.convert('RGBA')
        # new_val = (255, 255, 255, 0) # Last zero important: transparency.
        seed_right = (val - 1 for val in heraldry.size)
        ImageDraw.floodfill(heraldry, xy = seed_right, value = self.replace_val, thresh = self.px_dist)

        _, height = heraldry.size
        seed_left = (0, height - 1)
        ImageDraw.floodfill(heraldry, xy = seed_left, value = self.replace_val, thresh = self.px_dist)

        return heraldry