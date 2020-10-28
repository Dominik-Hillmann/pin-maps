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
    __max_offset = max([abs(choice[2]) for choice in __left_end_choices]) + max([abs(choice[2]) for choice in __right_end_choices])
    __max_left_adjust_y = max([choice[2] for choice in __left_end_choices])
    
    # A character which stretches all the way down such that font is properly aligned.
    _cellar_char = 'j'
    # Num of px the font is smaller than the ribbon height.
    __font_gap = 15


    def __init__(
        self, 
        town_name: str, 
        font_path: str = None, 
        gap: int  = -15, # 0 would be largest possible ribbon. 
        ribbon_height: int = 100, 
        ribbon_choice: Union[None, int] = None # For debugging.
    ):
        super().__init__()
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
        # This difference in y position is needed for all ribbons to have the same distance
        # to the pin itself. Because size of ribbon image is determined by the largest
        # possible ribbon, not this individual ribbon --> adjustments to its position in the image.
        diff_left_adjust_y = self.__max_left_adjust_y - self.__left_adjust_y

        # Dimensions of the final image.
        complete_dims = (
            abs(self.__left_adjust_x) + ribbon_width + self.__right_adjust_x + right_width,
            self.__max_offset + ribbon_height
        )
        complete_img = Image.new('RGBA', complete_dims, color = (0, 0, 0, 0))
        # Paste the ribbon itself into final image.
        ribbon_pos = (self.__left_adjust_x, self.__left_adjust_y + diff_left_adjust_y)
        complete_img.paste(ribbon, ribbon_pos)
        # Paste the left ribbon end into the final image.
        left_pos = (0, 0 + diff_left_adjust_y)
        complete_img.paste(self.__left_end, left_pos, self.__left_end)
        # Paste the right ribbon end into the final image.
        right_pos = (
            self.__left_adjust_x + ribbon_width + self.__right_adjust_x, 
            self.__left_adjust_y + diff_left_adjust_y
        )
        complete_img.paste(self.__right_end, right_pos, self.__right_end)

        return complete_img
    
    
    # Override from ImageTransform
    def transform(self, heraldry: Image.Image) -> Image.Image:
        segment_width, segment_height = self.__segment_left.size # Both have same dimensions.
        
        font = self._get_sized_font(segment_height, self.__font_gap)
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
        prop_ribbon_of_label = segment_height / ribbon_img.height
        ribbon_heraldry = self._add_label_to_heraldry(ribbon_img, heraldry, self.__ribbon_height, self.__gap)
        
        return ribbon_heraldry
    
