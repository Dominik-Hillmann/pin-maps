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

    
    def __call__(self, img: Image.Image) -> Image.Image:
        return self.transform(img)


    def __repr__(self):
        return f'CompleteImageTransform ({type(self).__name__})'
