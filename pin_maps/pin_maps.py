#!/usr/bin/env python
"""This program designs posters with pins on a map and undertitles."""

# Internal modules
from input_parser.ParamsParser import ParamsParser
from draw.AddShadow import AddShadow
from draw.BackgroundDeletion import BackgroundDeletion
from draw.Ribbon import Ribbon
from draw.OffsetLettering import OffsetLettering
from draw.Map import Map
from draw.Pin import Pin
# Python libraries
import os
from copy import deepcopy
from time import time
import logging
# External modules
from PIL import Image, ImageDraw, ImageFont
# Typing
from typing import List, Tuple, Union
# Dev
from pprint import pprint


def main() -> None:
    params = ParamsParser()
    create_output_dir()
    
    height_text_space = 750
    text = u'Inge & Das ist ein Test'
    added_frame_px = 150
    # germany = Map('de-neg.shp', 'space.png', [5.7, 15.3, 47.2, 56.2])
    # germany = Map('de-neg.shp', 'old-cut.png', [5.7, 15.3, 47.2, 56.2])
    img_transforms = [BackgroundDeletion(), AddShadow()]
    germany = Map('de-neg.shp', 'old-topo.png', [5.7, 15.3, 47.2, 56.2])
    
    for location in params.locations:
        specific_transforms = img_transforms + [Ribbon(location.name)] if params.ribbons else img_transforms
        print('TRANSOFRMS', specific_transforms)
        try:
            pin = Pin(location, params.marker_symbol, specific_transforms)
        except (ConnectionRefusedError, LookupError) as e:
            print(f'Had to skip pin at position {str(location)} due to {str(e)}.')
            continue

        germany.add_pin(pin)

    raw_img_name = f'raw-{round(time())}.png'
    germany.save(raw_img_name)

    cropping = (300, 650, 1760, 2580) # (left, top, right, bottom)
    img_new, (width_cropped, height_cropped) = crop_add_text_space(raw_img_name, cropping, height_text_space)
    draw, font_height = write_header(img_new, params.head_font_path, text, height_cropped, added_frame_px)
   
    t = 'München und Nürnberg sind in Bayern. Hallo, Wolfsburg ist ein Dresden. Ping ping pong ping ping pong Halle.'
    if params.text_coats:
        write_main_text_with_heraldry(
            t, 
            img_new, 
            ImageFont.truetype(params.main_font_path, 70),
            70,
            30,
            [location.name.lower() for location in params.locations],
            height_cropped,
            added_frame_px,
            font_height # Meaning the height of the main title, stupid variable naming!
        )
    else:
        write_main_text(
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

town_name_format = lambda word: word.lower().strip('.?,!:;-%()"\'$€/')

def write_main_text_with_heraldry(
    text: str,
    img: Image.Image,
    font: ImageFont.ImageFont,
    font_size: int,
    line_spacing: int,
    town_names: List[str],
    height_cropped: int,
    added_frame_px: int,
    height_heading: int,
    coat_text_gap: int = 15
):
    _, font_height = font.getsize('Tg')
    start_y = height_cropped + added_frame_px + height_heading + line_spacing
    for start_x, line_pattern in pattern_2nd_text_with_coats(text, img, font, font_size, line_spacing, town_names):
        line = compile_to_line(line_pattern)
        drawing = ImageDraw.Draw(img)
        
        for i, line_element in enumerate(line):
            if type(line_element) is str:
                drawing.text((start_x, start_y), line_element, font = font, fill = 'black')
                element_width, _ = font.getsize(line_element)
                start_x += element_width
            else:
                start_x += coat_text_gap if not i == 0 else 0

                element_width, element_height = proportional_size(font_height, line_element)
                line_element.thumbnail((element_width, element_height))
                img.paste(line_element, (start_x, start_y), line_element)
                
                start_x += element_width + coat_text_gap

        start_y += font_height + line_spacing


def get_coat_from_cache(town_name):
    return Image.open(os.path.join('data', 'img', 'pin-cache', f'{town_name}-pin.png'))


def proportional_size(set_height, img) -> Tuple[int, int]:
    current_w, current_h = img.size
    max_w, max_h = current_w, set_height,
    resize_ratio = min(max_w / current_w, max_h/ current_h)
    return (round(resize_ratio * current_w), round(resize_ratio * current_h))


def create_output_dir() -> None:
    """Creates a new output directory, if there is none."""

    working_dir_content = os.listdir(os.getcwd())
    if 'output' not in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def crop_add_text_space(
    raw_img_name: str,
    cropping: Tuple[float, float, float, float],
    added_text_height: int
) -> (Image.Image, Tuple[int, int]):
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
    adjustment: int = 20
) -> Tuple[ImageDraw.Draw, int]:
    """Writes the header below the image itself.

    Args
    ----
        img (Image): 
        font_path (str): 
        text (str): 
        height_cropped (int): 
        frame_width (int):
        adjustment (int): Defaults to 20.

    Returns
    -------
        [type]: [description]
    """
    img_width, _ = img.size
    font_size = 500 # Arbitrary but high start value
    font = ImageFont.truetype(font_path, font_size)
    font_width, font_height = font.getsize(text) 

    while font_width > img_width:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_width, font_height = font.getsize(text)
    
    draw = ImageDraw.Draw(img)
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


def town_formatting(town_name):
    return town_name.lower().strip('.?,!:;-%()"\'$€/')


def pattern_2nd_text_with_coats(
    text: str,
    img: Image.Image,
    font: ImageFont.ImageFont,
    font_size: int,
    line_spacing: int,
    town_names: List[str],
    coats_width: int = 150
) -> List[Tuple[bool, List[str]]]:
    pattern = []
    for start_x, line in pattern_2nd_text(text, img.width - coats_width, font, font_size, line_spacing):
        words = line.split(' ')
        line_pattern = [(False, [])]

        for word in words:
            n_splits = len(line_pattern)
            if town_formatting(word) in town_names:
                line_pattern.append((True, [word]))
            else:
                line_pattern[n_splits - 1][1].append(word)
        
        if line_pattern[0] == (False, []):
            line_pattern = line_pattern[1:]
        pattern.append((start_x, line_pattern))

    return pattern


def compile_to_line(line_pattern: List[Tuple[bool, List[str]]]) -> List[Union[Image.Image, str]]:
    written_line = []
    for coat_wanted, words in line_pattern:
        if coat_wanted:
            written_line.append(get_coat_from_cache(town_formatting(words[0])))
        written_line.append(' '.join(words))

    return written_line


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


def frame_img(img: Image.Image, added_frame_px: int) -> Image.Image:
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

'''
def add_header_strokes(
    img: Image.Image, 
    header_pos: Tuple[int, int], 
    header_size: Tuple[int, int],
    gap: int = 100
) -> Image.Image:
    """
    """
    img_width, _ = img.size
    header_x, header_y = header_pos
    header_width, header_height = header_size
    
    drawing = ImageDraw.Draw(img)
    
    lines_y = header_y + round(height_height / 2)
    left_line_start = (header_x - gap, lines_y)
    left_line_end = (gap, lines_y)
    right_line_start = (header_x + header_width + gap, lines_y)
    right_line_end = (img_width - gap, lines_y)

    drawing.line((*left_line_start, *left_line_end), fill = 128, width = 10)
    drawing.line((*right_line_start, *right_line_start), fill = 128, width = 10)
    
    return img
'''

if __name__ == '__main__':
    logging.warn('Ich starte.')
    main()
    logging.critical('Ich beende.')
    
