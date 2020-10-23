# Python libraries
import os
import random
# Internal modules
from transforms.ImageTransform import ImageTransform
# External modules
from PIL import Image, ImageFont, ImageDraw
# Typing
from typing import Union

class Ribbon(ImageTransform):
    """Creates a ribbon with the city's name written on it.
    
    Args:
    -----
        town_name (str): The name written on the ribbon.
        font_path (str): The path to the truetype font. Defaults to standard_font_path.
        gap (int): Gap between heraldry and ribbon in pixels. Defaults to 7.
        ribbon_height (int): Height of the ribbon in pixels. Defaults to 100.
    """
    __standard_font_path = os.path.join('data', 'fonts', 'fraktur-modern.ttf')
    __ribbon_path = os.path.join('data', 'img', 'ribbons')

    __segment_left = Image.open(os.path.join(__ribbon_path, 'left-segment.png'))
    __segment_right = Image.open(os.path.join(__ribbon_path, 'right-segment.png'))
    # (ribbon ending, adjustment along x dimension, adjustment along y dimension)
    __left_end_choices = [
        (Image.open(os.path.join(__ribbon_path, 'left-end-1.png')), 45, 31),
        (Image.open(os.path.join(__ribbon_path, 'left-end-2.png')), 65, 46),
        (Image.open(os.path.join(__ribbon_path, 'left-end-3.png')), 67, 67)
    ] 
    __right_end_choices = [
        (Image.open(os.path.join(__ribbon_path, 'right-end-1.png')), -22, 33),
        (Image.open(os.path.join(__ribbon_path, 'right-end-2.png')), -30, 43),
        (Image.open(os.path.join(__ribbon_path, 'right-end-3.png')), -40, 70)
    ]

    # A character which stretches all the way down such that font is properly aligned.
    _cellar_char = 'j'


    def __init__(
        self, 
        town_name: str, 
        font_path: str = None, 
        gap: int = 7, 
        ribbon_height: int = 100, 
        ribbon_choice: Union[None, int] = None # For debugging.
    ):
        self.town_name = town_name[0].capitalize() + town_name[1:]
        self.__gap = gap
        self.__ribbon_height = ribbon_height

        if ribbon_choice is not None:
            self.__left_end, self.__left_adjust_x, self.__left_adjust_y = self.__left_end_choices[ribbon_choice - 1]
            self.__right_end, self.__right_adjust_x, self.__right_adjust_y = self.__right_end_choices[ribbon_choice - 1]
        else:
            self.__left_end, self.__left_adjust_x, self.__left_adjust_y = random.choice(self.__left_end_choices)
            self.__right_end, self.__right_adjust_x, self.__right_adjust_y = random.choice(self.__right_end_choices)

        if font_path is not None:
            self._font_path = font_path
        else:
            self._font_path = self.__standard_font_path
        
    
    def __attach_ribbon_ends(self, ribbon: Image.Image) -> Image.Image:
        """Attaches to scroll rolling at the left and right end. Chooses randomly
        between alternatives.
        
        Args:
        -----
            text_ribbon (Image.Image): The middle part of the ribbon.

        Returns:
        --------
            Image.Image: The ribbon with both ends attached to it.
        """
        right_width, _ = self.__right_end.size
        ribbon_width, ribbon_height = ribbon.size
        
        # Dimensions of the final image.
        complete_dims = (
            abs(self.__left_adjust_x) + ribbon_width + self.__right_adjust_x + right_width,
            abs(self.__left_adjust_y) + ribbon_height + abs(self.__right_adjust_y)
        )
        complete_img = Image.new('RGBA', complete_dims, color = (0, ) * 4)
        # Paste the ribbon itself into final image.
        ribbon_pos = (self.__left_adjust_x, self.__left_adjust_y)
        complete_img.paste(ribbon, ribbon_pos)
        # Paste the left ribbon end into the final image.
        complete_img.paste(self.__left_end, (0, 0), self.__left_end)
        # Paste the right ribbon end into the final image.
        right_pos = (
            self.__left_adjust_x + ribbon_width + self.__right_adjust_x, 
            abs(self.__left_adjust_y)
        )
        complete_img.paste(self.__right_end, right_pos, self.__right_end)

        return complete_img
    
    
    # Override from ImageTransform
    def transform(self, heraldry: Image.Image) -> Image.Image:
        segment_width, segment_height = self.__segment_left.size # Both have same dimensions.
        
        eta = 15 # in px
        font = self._get_sized_font(segment_height, eta)
        text_width, _ = font.getsize(self.town_name)
        _, text_height = font.getsize(self.town_name + self._cellar_char)
        cellar_width, _ = font.getsize(self._cellar_char)
        
        # Create segments backgrounds.
        num_segs = 1
        while num_segs * segment_width <= text_width:
            num_segs += 1
        num_segs += 4 # To provide enough space for the ribbon ends.

        ribbon_img = Image.new('RGBA', (num_segs * segment_width, segment_height), color = (0, ) * 4)
        for segment_idx in range(num_segs):
            if segment_idx % 2 == 0:
                ribbon_img.paste(self.__segment_left, (segment_idx * segment_width, 0))
            else:
                ribbon_img.paste(self.__segment_right, (segment_idx * segment_width, 0))
        
        # Write onto the segments background.
        ribbon_drawer = ImageDraw.Draw(ribbon_img)
        text_pos = (
            # Width has to be adjusted for cellar char.
            round((segment_width * num_segs - (text_width - cellar_width / 2)) / 2) - round(cellar_width / 2), 
            round((segment_height - text_height) / 2)
        )
        ribbon_drawer.text(text_pos, self.town_name, 'black', font)
        
        ribbon_img = self.__attach_ribbon_ends(ribbon_img)
        # We want the middle part of all ribbons to be the same height, not the complete ribbon including the ends.        
        prop_ribbon_of_label = segment_height / ribbon_img.height
        print(prop_ribbon_of_label)
        wanted_height = self.__ribbon_height #round(self.__ribbon_height / prop_ribbon_of_label) 
        ribbon_heraldry = self._add_label_to_heraldry(ribbon_img, heraldry, wanted_height, self.__gap)
        
        return ribbon_heraldry
    
