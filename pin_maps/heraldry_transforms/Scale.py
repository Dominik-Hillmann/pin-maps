
# Internal modules
from heraldry_transforms.ImageTransform import ImageTransform
# External modules
from PIL import Image
import cv2
import numpy as np
# Typing 
from typing import Tuple


class Scale(ImageTransform):
    """Scales all images to a uniform width so that further transforms have the same dimensions.

    Args:
    -----
        width (int): Target width of the scaling.
    """

    def __init__(self, width: int):
        super().__init__()
        self.__target_width = width


    def __scale_dims(self, width: int, height: int) -> Tuple[int, int]:
        """Proportionally scales height to target width.

        Args:
        -----
            width (int): Image width.
            height (int): Image height.

        Returns:
        --------
            Tuple[int, int]: Scaled image shape.
        """
        max_width, max_height = self.__target_width, height
        resize_ratio = max_width / width
        new_size = (self.__target_width, round(resize_ratio * max_height))

        return new_size


    # Override from ImageTransform
    def transform(self, heraldry: Image.Image) -> Image.Image:
        old_size = heraldry.size
        new_size = self.__scale_dims(*old_size)
        
        img_arr = np.array(heraldry)
        scaled_img_arr = cv2.resize(img_arr, new_size)
        scaled_heraldry = Image.fromarray(scaled_img_arr)

        return scaled_heraldry
