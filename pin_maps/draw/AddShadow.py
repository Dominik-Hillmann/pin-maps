# Internal modules
from draw.ImageTransform import ImageTransform
# External modules
from PIL import Image, ImageDraw
# Typing
from typing import Tuple

class AddShadow(ImageTransform):
    """Adds a shadow below the heraldry.

    Args:
        height_change (float, optional): Percentage change to make space for the shadow. Defaults to 1.1.
        ell_start (float, optional): Upper start of shadow as percentage of the height of the input image. Defaults to 0.9.
        fill_col (Tuple[int, int, int, int], optional): Color of the shadow. Defaults to (0, 0, 0, 100).
    """

    def __init__(
        self, 
        height_change: float = 1.1, 
        ell_start: float = 0.9, 
        fill_col: Tuple[int, int, int, int] = (0, 0, 0, 100)
    ):
        self.height_change = height_change
        self.ell_start = ell_start
        self.fill_col = fill_col

    
    def transform(heraldry: Image.Image) -> Image.Image:
        """Adds a shadow below the heraldry.

        Args:
            heraldry (Image.Image): The image to which you want to add the shadow.

        Returns:
            Image.Image: The image containing a shadow.
        """

        heraldry = heraldry.convert('RGBA')
        orig_width, orig_height = heraldry.size

        new_height = int(self.height_change * orig_height)
        ell_img = Image.new('RGBA', (orig_width, new_height))
        draw = ImageDraw.Draw(ell_img)

        top_left = (0, int(self.ell_start * orig_height))
        bot_right = (orig_width - 1, new_height - 1)
        draw.ellipse((*top_left, *bot_right), fill = self.fill_col)
        ell_img.paste(heraldry, (0, 0), heraldry)

        return ell_img