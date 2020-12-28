# Internal modules
from heraldry_transforms.ImageTransform import ImageTransform
# External modules
from PIL import Image, ImageDraw, ImageFont
# Python libraries
import os

class OffsetLettering(ImageTransform):
    """Generates a label above with the same label slightly offset.

    Args:
    -----
        town_name (str): The label on the map.
        foreground_col (str, optional): Main color. Defaults to None.
        background_col (str, optional): The color of the offsets. Defaults to None.
        height (int, optional): Height of the label. Defaults to None.
        gap (int, optional): Gap in pixels between heraldry and label. Defaults to None.
        font_path (str, optional): Path to the font used. Defaults to None.
    """    
    __standard_font_path = os.path.join('data', 'fonts', 'fraktur-modern.ttf')

    def __init__(
        self,
        town_name: str,
        foreground_col: str = None,
        background_col: str = None,
        height: int = None,
        gap: int = None,
        font_path: str = None
    ):
        super().__init__()
        self.town_name = town_name[0].capitalize() + town_name[1:]
        self.__foreground_col = 'white' if foreground_col is None else foreground_col
        self.__background_col = 'red' if background_col is None else background_col
        self.__wanted_height = 80 if height is None else height
        self.__gap = 10 if gap is None else gap
        self._font_path = self.__standard_font_path if font_path is None else font_path
        self.__font = self._get_sized_font(100, 0)


    # Override from ImageTransform
    def transform(self, heraldry: Image.Image) -> Image.Image:
        lettering_dims = self.__font.getsize(self.town_name)
        spacing = 1
        num_steps = 10

        lettering_dims = tuple(val + spacing * num_steps for val in lettering_dims)
        lettering = Image.new('RGBA', lettering_dims, (0, ) * 4)
        lettering_drawing = ImageDraw.Draw(lettering)
        
        for i in range(num_steps, 0, -1):
            lettering_drawing.text((spacing * i, ) * 2, self.town_name, self.__background_col, self.__font)
        lettering_drawing.text((0, 0), self.town_name, self.__foreground_col, self.__font)

        complete_img = self._add_label_to_heraldry(lettering, heraldry, self.__wanted_height, self.__gap)
        
        return complete_img
