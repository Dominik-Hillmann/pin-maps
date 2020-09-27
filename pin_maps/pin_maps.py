#!/usr/bin/env python
"""Create maps with pins and make them beautiful."""

# Internal modules
from input_parser.ParamsParser import ParamsParser
# from info_retrieval.Coordinates import Coordinates
from draw.Map import Map
from draw.Pin import Pin
# Python libraries
import os
from copy import deepcopy
from time import time
# External modules
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
# Typing
from typing import List, Tuple
# Dev
from pprint import pprint


def main() -> None:
    params = ParamsParser()
    create_output_dir()

    height_text_space = 750
    text = u'Inge & Maik-Günter'
    added_frame_px = 150
    # germany = Map('de-neg.shp', 'space.png', [5.7, 15.3, 47.2, 56.2])
    germany = Map('de-neg.shp', 'old-cut.png', [5.7, 15.3, 47.2, 56.2])
    
    for location in params.locations:
        try:
            pin = Pin(location, params.marker_symbol)
        except (ConnectionRefusedError, LookupError) as e:
            print(f'Had to skip pin at position {str(location)} due to {str(e)}.')
            continue

        germany.add_pin(pin)

    raw_img_name = f'raw-{round(time())}.png'
    germany.save(raw_img_name)

    cropping = (300, 650, 1760, 2580) # (left, top, right, bottom)
    img_new, (width_cropped, height_cropped) = crop_add_text_space(raw_img_name, cropping, height_text_space)
    draw, font_height = write_header(img_new, params.head_font_path, text, height_cropped, added_frame_px)
    
    t = 'Fulda, 11. September 2001. Ich werde dich für immer lieben. Für immer und immer und immer und immer und immer.'
    img_new = write_main_text(
        img_new,
        t,
        params.main_font_path, 
        70,
        height_cropped,
        added_frame_px,
        font_height
    )

    framed_img = frame_img(img_new, added_frame_px)
    framed_img.save(os.path.join(os.getcwd(), 'output', 'written.png'))


def create_output_dir() -> None:
    """Creates a new output directory, if there is none."""

    working_dir_content = os.listdir(os.getcwd())
    if 'output' not in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def crop_add_text_space(
    raw_img_name: str,
    cropping: Tuple[float, float, float, float],
    added_text_height: int
) -> (Image, Tuple[int, int]):
    """Crops the cartopy output and adds space to write text into below.

    Args:
        raw_img_name (str): The name if the image file with the map in the output directory.
        cropping (Tuple[float, float, float, float]): Pixels from which map will be cropped (left, top, right, bottom).
        added_text_height (int): The height of the area below into which text will be written.

    Returns:
        (Image, Tuple[int, int]): The changed image and the size of the cropped map.
    """

    img = Image.open(os.path.join('output', raw_img_name))
    img = img.crop(cropping)
    width_cropped, height_cropped = img.size
    
    dims_with_text = (width_cropped, height_cropped + added_text_height)
    img_text = Image.new(img.mode, dims_with_text, color = (255, ) * 3)
    img_text.paste(img, (0, 0))

    return img_text, (width_cropped, height_cropped)


def write_header(
    img: Image, 
    font_path: str, 
    text: str, 
    height_cropped: int, 
    frame_width: int, 
    # added_frame_px: int,
    adjustment: int = 20
) -> (ImageDraw.Draw, int):

    img_width, img_height = img.size
    font_size = 500 # Arbitrary but high start value
    font = ImageFont.truetype(font_path, font_size)
    font_width, font_height = font.getsize(text) 

    # print(f'Width: {font_width}, Size: {font_size}')
    while font_width > img_width:
        # print(f'Width: {font_width}, Size: {font_size}')
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_width, font_height = font.getsize(text)
    
    draw = ImageDraw.Draw(img)
    # draw.text((0, height_cropped + added_frame_px - adjustment), text, 'black', font)
    draw.text((0, height_cropped + frame_width - adjustment), text, 'black', font)

    return draw, font_height


def pattern_2nd_text(
    text: str, 
    img_width: int, 
    font: ImageFont, 
    font_size: int = 80, 
    line_dist: int = 10
) -> List[Tuple[int, str]]:
    """Creates the text lines and their horizontal start position.

    Args:
        text (str): The text to be partiotined.
        img_width (int): Image width.
        font (ImageFont): The font with which the second text will be written.
        font_size (int, optional): The size of this font. Defaults to 80.
        line_dist (int, optional): The vertical distance in pixels between lines. Defaults to 10.

    Returns:
        List[Tuple[int, str]]: The list of the horizontal start positions and the lines.
    """

    lines = []
    starts = []
    text = text.split(' ')

    while len(text) > 0:
        this_line = deepcopy(text)
        line_width, line_height = font.getsize(' '.join(this_line))
        
        while line_width > img_width:
            this_line.pop()
            line_width, line_height = font.getsize(' '.join(this_line))

        lines.append(' '.join(this_line))
        starts.append(round((img_width - line_width) / 2))
        
        for _ in this_line:
            text.pop(0)

    return list(zip(starts, lines))


def write_main_text(
    img: Image,
    text: str, 
    font_path: str, 
    font_size: int,
    height_cropped: int,
    added_frame_px: int,
    font_height: int,
    line_spacing: int = 30
) -> Image:
    """Writes the main text into the free area.

    Args:
        img (Image): The image on which will be written.
        text (str): The text that will be written
        font_path (str): Path to the font used.
        font_size (int): The font size.
        height_cropped (int): Height of the cropped out map.
        added_frame_px (int): The width of the future frame.
        font_height (int): The height of the font of the heading.
        line_spacing (int, optional): Number of pixels in spacing between lines. Defaults to 30.

    Returns:
        Image: The image with text.
    """

    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)

    hori_start = height_cropped + added_frame_px + font_height + line_spacing # Height of first heading
    font = ImageFont.truetype(font_path, font_size)
    font_width, font_height = font.getsize(text)
    
    pattern = pattern_2nd_text(text, img_width, font)
    for vert_start, line in pattern:
        draw_pos = (vert_start, hori_start)
        draw.text(draw_pos, line, (0, ) * 3, font)
        hori_start += font_height + line_spacing
    
    return img


def frame_img(img: Image, added_frame_px: int) -> Image:
    """Puts a uniform frame around the image.

    Args:
        img (Image): The image around which the frame will be put.
        added_frame_px (int): Width of the frame.

    Returns:
        Image: [description]
    """

    width, height = img.size
    frame_dims = (width + added_frame_px * 2, height + added_frame_px * 2)
    framed_img = Image.new(img.mode, frame_dims, (255, ) * 3)
    framed_img.paste(img, (added_frame_px, ) * 2)

    return framed_img


if __name__ == '__main__':
    main()
    