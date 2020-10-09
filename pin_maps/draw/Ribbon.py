# Python libraries
import os
# Internal modules
from draw.ImageTransform import ImageTransform
# External modules
from PIL import Image, ImageFont, ImageDraw


class Ribbon(ImageTransform):
    """Creates a ribbon with the city's name at the bottom of the image.
    
    Args:
    -----
        town_name (str): The name written on the ribbon.
        font_path (str): The path to the truetype font. Defaults to standard_font_path.
        gap (int): Gap between heraldry and ribbon in pixels. Defaults to 7.
        ribbon_height (int): Height of the ribbon in pixels. Defaults to 100.
    """
    
    standard_font_path = os.path.join('data', 'fonts', 'grandhotel.ttf')
    ribbon_path = os.path.join('data', 'img', 'ribbons')
    segment_left = Image.open(os.path.join(ribbon_path, 'left-segment.png'))
    segment_right = Image.open(os.path.join(ribbon_path, 'right-segment.png'))
    left_ending = Image.open(os.path.join(ribbon_path, 'left-end-1.png'))
    right_ending = Image.open(os.path.join(ribbon_path, 'right-end-1.png'))
    # A character which stretches all the way down such that font is properly aligned.
    __cellar_char = 'j'


    def __init__(self, town_name: str, font_path: str = None, gap: int = 7, ribbon_height: int = 100, ribbon_choice: int = None):
        self.town_name = town_name[0].capitalize() + town_name[1:]
        self.gap = gap
        self.ribbon_height = ribbon_height

        if font_path is not None:
            self.font_path = font_path
        else:
            self.font_path = self.standard_font_path
        
    
    def __get_sized_font(self, segment_height: int, eta: int) -> ImageFont.ImageFont:
        """Get a font where the height fits into the ribbon segments.

        Args:
        -----
            segment_height (int): Segment height in pixels.
            eta (int): How much there should be between ribbon and font in pixels.

        Returns:
        --------
            ImageFont.ImageFont: The fitting font.
        """
        goal_height = segment_height - eta
        text = self.town_name + self.__cellar_char
        
        font_size = 500
        current_font = ImageFont.truetype(self.font_path, font_size)
        _, current_height = current_font.getsize(text)
        # current_cellar_width, _ = current_font.getsize(self.__cellar_char)
        while current_height >= goal_height:
            font_size -= 1
            current_font = ImageFont.truetype(self.font_path, font_size)
            _, current_height = current_font.getsize(text)

        return current_font

    
    def __attach_ribbon_ends(self, text_ribbon: Image.Image) -> Image.Image:
        """Attaches to scroll rolling at the left and right end. Chooses randomly
        between alternatives.
        
        Args:
        -----
            text_ribbon (Image.Image): The middle part of the ribbon.

        Returns:
        --------
            Image.Image: The ribbon with both ends attached to it.
        """
        right_width, right_height = self.right_ending.size
        left_width, left_height = self.left_ending.size
        text_ribbon_width, text_ribbon_height = text_ribbon.size

        complete_dims = (
            right_width + left_width + text_ribbon_width, 
            max(right_height, left_height, text_ribbon_height)
        )
        complete_img = Image.new('RGBA', complete_dims, color = (0, ) * 4)

        # ADJUSTMENTS NEED TO BE ATTACHED TO ENDINGS
        left_ending_adjustment = 16
        right_ending_adjustment = -7
        complete_img.paste(text_ribbon, (left_width + 1, 20))
        complete_img.paste(self.left_ending, (0 + left_ending_adjustment, 0), self.left_ending)
        complete_img.paste(self.right_ending, (left_width + text_ribbon_width + 1 + right_ending_adjustment, 0), self.right_ending)
        complete_img = complete_img.crop((left_ending_adjustment, 0, complete_dims[0] + right_ending_adjustment, complete_dims[1]))

        return complete_img
    
    
    def __add_ribbon_to_heraldry(self, ribbon: Image.Image, heraldry: Image.Image) -> Image.Image:
        """Puts the ribbon into the same image as the heraldry.

        Args:
        -----
            ribbon (Image.Image): The ribbon.
            heraldry (Image.Image): The heraldry.

        Returns:
        --------
            (Image.Image): The combined image.
        """
        # Proportionally resize ribbon to certain height.
        current_ribbon_w, current_ribbon_h = ribbon.size
        max_ribbon_w, max_ribbon_h = current_ribbon_w, self.ribbon_height
        resize_ratio = min(max_ribbon_w / current_ribbon_w, max_ribbon_h / current_ribbon_h)
        new_ribbon_size = round(resize_ratio * current_ribbon_w), round(resize_ratio * current_ribbon_h)
        ribbon.thumbnail(new_ribbon_size)

        # Create image with maximum width and height of ribbon and heraldry and a gap.
        complete_img_h = ribbon.height + self.gap + heraldry.height
        complete_img_w = max(ribbon.width, heraldry.width)
        complete_img = Image.new('RGBA', (complete_img_w, complete_img_h), (0, 0, 0, 0))
        
        # Paste both images into correct postion.
        if ribbon.width >= heraldry.width:
            ribbon_paste_w = 0
            heraldry_paste_w = round((ribbon.width - heraldry.width) / 2)
        else:
            ribbon_paste_w = round((heraldry.width - ribbon.width) / 2)
            heraldry_paste_w = 0

        ribbon_paste_pos = (ribbon_paste_w, 0)
        heraldry_paste_pos = (heraldry_paste_w, ribbon.height + self.gap)

        complete_img.paste(ribbon, ribbon_paste_pos)
        complete_img.paste(heraldry, heraldry_paste_pos)

        return complete_img


    # Override
    def transform(self, heraldry: Image.Image) -> Image.Image:
        segment_width, segment_height = self.segment_left.size # Both have same dimensions.
        
        eta = 10 # in px
        font = self.__get_sized_font(segment_height, eta)
        text_width, _ = font.getsize(self.town_name)
        _, text_height = font.getsize(self.town_name + self.__cellar_char)
        cellar_width, _ = font.getsize(self.__cellar_char)
        
        # Create segments backgrounds.
        num_segs = 1
        while num_segs * segment_width <= text_width:
            num_segs += 1

        ribbon_img = Image.new('RGBA', (num_segs * segment_width, segment_height), color = (0, ) * 4)
        for segment_idx in range(num_segs):
            if segment_idx % 2 == 0:
                ribbon_img.paste(self.segment_left, (segment_idx * segment_width, 0))
            else:
                ribbon_img.paste(self.segment_right, (segment_idx * segment_width, 0))
        
        # Write onto the segments background.
        ribbon_drawer = ImageDraw.Draw(ribbon_img)
        text_pos = (
            # Width has to be adjusted for cellar char.
            round((segment_width * num_segs - (text_width - cellar_width / 2) ) / 2), 
            round((segment_height - text_height) / 2)
        )
        ribbon_drawer.text(text_pos, self.town_name, 'black', font)
        
        # Attach the rolled ends to the ribbon.
        ribbon_img = self.__attach_ribbon_ends(ribbon_img)
        ribbon_heraldry = self.__add_ribbon_to_heraldry(ribbon_img, heraldry)
        
        return ribbon_heraldry
