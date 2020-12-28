# Python libraries
from abc import ABC, abstractmethod
# External modules
from PIL import Image


class CompleteImageTransform(ABC):
    """Abstract base class for image transformations. The `transform(self, 
    img: Image.Image) -> Image.Image` method needs to be implemented."""

    def __init__(self):
        super().__init__()


    @abstractmethod
    def transform(self, img: Image.Image) -> Image.Image:
        """Performs the image transformation."""
        pass
    
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

    
    def __call__(self, img: Image.Image) -> Image.Image:
        return self.transform(img)


    def __repr__(self):
        return f'CompleteImageTransform ({type(self).__name__})'
