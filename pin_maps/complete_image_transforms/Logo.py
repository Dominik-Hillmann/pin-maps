# Internal imports
from complete_image_transforms.CompleteImageTransform import CompleteImageTransform
# External modules
from PIL import Image
# Python libraries
import os 

class Logo(CompleteImageTransform):

    __logo_path = Image.open(os.path.join('data', 'img', 'brainrain-logo-lang.jpg'))
    __target_height = 50

    def __init__(self):
        super().__init__()

    
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