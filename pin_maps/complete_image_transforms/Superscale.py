# Python libraries
import os
# Internal imports
from complete_image_transforms.CompleteImageTransform import CompleteImageTransform
# External imports
from cv2 import dnn_superres
import numpy as np
from PIL import Image

class Superscale(CompleteImageTransform):
    """Upscales the image using superresolution neural networks."""

    available_models = {'espcn', 'fsrcnn', 'lapsrn'}
    available_scale_factors = {4}

    def __init__(self, scale_factor: int = 4, model_name: str = 'lapsrn'):
        super().__init__()

        if scale_factor not in self.available_scale_factors:
            err_message = (f'Scale factor {scale_factor} unavailable. Available: ' +
            ', '.join(fac for fac in available_scale_factors) + '.')
            raise ValueError(err_message)
        self.scale_factor = scale_factor

        if model_name not in self.available_models:
            err_message = (f'Model {model_name} unavailable. Available: ' +
            ', '.join(self.available_models) + '.')
            raise ValueError(err_message)
        self.model_name = model_name


    def superscale(self, img: Image.Image) -> Image.Image:
        """Performs upsampling using superresolution neural networks.
        At the moment, OpenCV offers four models, three of which you can choose here:
        LAPSRN, ESPCN, FSRCNN. All of which can upsample by the factor of 4.
        Other versions can be downloaded too, the EDSR model is too large and too slow.

        Quellen:
        https://towardsdatascience.com/deep-learning-based-super-resolution-with-opencv-4fd736678066
        https://docs.opencv.org/master/d5/d29/tutorial_dnn_superres_upscale_image_single.html


        Args:
            img (Image.Image): Image to be upscaled.

        Returns:
            Image.Image: The upsampled image.
        """
        superscaler = dnn_superres.DnnSuperResImpl_create()
        model_path = os.path.join('data', 'models', f'{self.model_name.upper()}_x{self.scale_factor}.pb')
        superscaler.readModel(model_path)
        superscaler.setModel(self.model_name, self.scale_factor)

        img = img.convert('RGB')
        img = np.array(img)
        img = superscaler.upsample(img)
        img = Image.fromarray(img.astype('uint8'), 'RGB')

        return img
    

    def transform(self, img: Image.Image) -> Image.Image:
        return self.superscale(img)