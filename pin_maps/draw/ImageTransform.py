# Python libraries
from abc import ABC, abstractmethod
# External modules
from PIL import Image
from PIL import ImageFont


class ImageTransform(ABC):
    """Abstract base class for image/pin transformations. The `transform(self, 
    heraldry: Image.Image) -> Image.Image` method needs to be implemented."""

    _cellar_char = 'j'

    def __init__(self):
        super().__init__()
        self.town_name = None
        self._font_path = None


    def _get_sized_font(self, segment_height: int, eta: int) -> ImageFont.ImageFont:
        """Get a font where the height fits into the `segment_height` with a 
        space of `eta / 2` remaining above and below.

        Args:
        -----
            segment_height (int): Segment height in pixels.
            eta (int): How much there should be between ribbon and font in pixels.

        Returns:
        --------
            ImageFont.ImageFont: The fitting font.
        """
        goal_height = segment_height - eta
        text = self.town_name + self._cellar_char
        
        font_size = 500
        current_font = ImageFont.truetype(self._font_path, font_size)
        _, current_height = current_font.getsize(text)
        while current_height >= goal_height:
            font_size -= 1
            current_font = ImageFont.truetype(self._font_path, font_size)
            _, current_height = current_font.getsize(text)

        return current_font
    

    @staticmethod
    def _add_label_to_heraldry(
        label: Image.Image, 
        heraldry: Image.Image,
        label_height: int,
        gap: int
    ) -> Image.Image:
        """Puts the `label` into the same image as the `heraldry`.

        Args:
        -----
            label (Image.Image): The label image.
            heraldry (Image.Image): The heraldry.
            label_height (int): The height of the label in pixels.
            gap (int): The distance between the label and the heraldry in pixels.

        Returns:
        --------
            (Image.Image): The combined image.
        """
        # Proportionally resize label to certain height.
        current_label_w, current_label_h = label.size
        max_label_w, max_label_h = current_label_w, label_height
        resize_ratio = min(max_label_w / current_label_w, max_label_h / current_label_h)
        new_label_size = (round(resize_ratio * current_label_w), round(resize_ratio * current_label_h))
        label.thumbnail(new_label_size)

        # Create image with maximum width and height of label and heraldry and a gap.
        complete_img_h = label.height + gap + heraldry.height
        complete_img_w = max(label.width, heraldry.width)
        complete_img = Image.new('RGBA', (complete_img_w, complete_img_h), (0, 0, 0, 0))
        
        # Paste both images into correct postion.
        if label.width >= heraldry.width:
            label_paste_w = 0
            heraldry_paste_w = round((label.width - heraldry.width) / 2)
        else:
            label_paste_w = round((heraldry.width - label.width) / 2)
            heraldry_paste_w = 0

        label_paste_pos = (label_paste_w, 0)
        heraldry_paste_pos = (heraldry_paste_w, label.height + gap)

        complete_img.paste(label, label_paste_pos)
        complete_img.paste(heraldry, heraldry_paste_pos)

        return complete_img


    @abstractmethod
    def transform(self, heraldry: Image.Image) -> Image.Image:
        """Performs the image change."""
        pass

    
    def __call__(self, heraldry: Image.Image) -> Image.Image:
        return self.transform(heraldry)


    def __repr__(self):
        return f'ImageTransform ({type(self).__name__})'
