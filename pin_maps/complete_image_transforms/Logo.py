# Internal imports
from complete_image_transforms.CompleteImageTransform import CompleteImageTransform
# External modules
from PIL import Image
# Python libraries
import os
# Typing
from typing import Tuple

class Logo(CompleteImageTransform):
    """Inserts the Logo into the image."""

    __logo_path = os.path.join('data', 'img', 'brainrain-logo-lang.jpg')
    __target_height = 50

    def __init__(self):
        super().__init__()


    @staticmethod
    def __proportional_size(set_height: int, img: Image.Image) -> Tuple[int, int]:
        """Calculates the the width of an image given its resized height.

        Args:
            set_height (int): The new height to which width should be adapted.
            img (Image.Image): The image that gets resized.

        Returns:
            Tuple[int, int]: The proportional width.
        """
        current_w, current_h = img.size
        max_w, max_h = current_w, set_height,
        resize_ratio = min(max_w / current_w, max_h / current_h)
        return (round(resize_ratio * current_w), round(resize_ratio * current_h))


    def transform(self, img: Image.Image) -> Image.Image:
        logo = Image.open(self.__logo_path)
        logo = logo.resize(self.__proportional_size(self.__target_height, logo))
        logo_width, logo_height = logo.size
        
        half_img_width = round(img.width / 2)
        half_logo_width = round(logo_width / 2)
        paste_pos = (
            half_img_width - half_logo_width, 
            img.height - logo_height - 50
        )
        img.paste(logo, paste_pos)

        return img
