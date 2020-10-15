# Python libraries
from abc import ABC, abstractmethod
# External modules
from PIL import Image


class ImageTransform(ABC):
    """Abstract base class for image/pin transformations. The 
    ```transform(self, heraldry: Image.Image) -> Image.Image``` method needs to be implemented."""

    def __init__(self):
        super().__init__()

    
    @abstractmethod
    def transform(self, heraldry: Image.Image) -> Image.Image:
        """Performs the image change."""
        pass

    
    def __call__(self, heraldry: Image.Image) -> Image.Image:
        return self.transform(heraldry)


    def __repr__(self):
        return f'ImageTransform ({type(self).__name__})'
