# Internal modules
from transforms.ImageTransform import ImageTransform
# External modules
from PIL import Image

class Cutout(ImageTransform):
    """Removes empty space at the edge of the image."""

    def __init__(self):
        super().__init__()


    # Override from ImageTransform
    def transform(self, heraldry: Image.Image) -> Image.Image:
        boundary_box = heraldry.getbbox()
        if boundary_box:
            return heraldry.crop(boundary_box)
        else: 
            return heraldry
