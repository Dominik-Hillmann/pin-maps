#!/usr/bin/env python
"""This program designs posters of maps with pins and undertitles."""

# Internal modules
from input_parser.ParamsParser import ParamsParser
from transforms.AddShadow import AddShadow
from transforms.BackgroundDeletion import BackgroundDeletion
from transforms.Ribbon import Ribbon
from transforms.OffsetLettering import OffsetLettering
from transforms.Scale import Scale
from transforms.Cutout import Cutout
from draw.Map import Map
from draw.Pin import Pin
# Python libraries
import os
from copy import deepcopy
from time import time
import logging
import random
# External modules
from PIL import Image, ImageDraw, ImageFont
# Typing
from typing import List, Tuple, Union
# Settings
random.seed(69)


def main() -> None:
    params = ParamsParser()
    create_output_dir()
    
    # height_text_space = 750
    height_text_space = 930
    heading = u'Laura & Philipp'
    added_frame_px = 150

    print(params.marker_symbol)

    # --- Map creation and pin setting ----------------------------------------
    img_transforms = [BackgroundDeletion(), Cutout(), Scale(110), AddShadow()]
    # germany = Map('de-neg.shp', 'old-topo.png', [5.7, 15.3, 47.2, 56.2])
    germany = Map('de-neg.shp', 'old-topo.png', [5.32, 15.55, 47.2, 56.2])
    
    for location in params.locations:
        print(location.name)
        specific_transforms = img_transforms + [Ribbon(location.name)] if params.ribbons else img_transforms
        print('TRANSOFRMS', specific_transforms)
        try:
            pin = Pin(location, params.marker_symbol, specific_transforms)
        except (ConnectionRefusedError, LookupError) as e:
            print(f'Had to skip pin at position {str(location)} due to {str(e)}.')
            continue

        germany.add_pin(pin)
        print()

    raw_img_name = f'raw-{round(time())}.png'
    germany.save(raw_img_name)

    # --- Map cropping --------------------------------------------------------
    # cropping = (300, 650, 1760, 2580) # (left, top, right, bottom)
    cropping = (300, 650, 1760, 2525) # (left, top, right, bottom)
    img = Image.open(os.path.join('output', raw_img_name))    
    img = crop_map(img, cropping)

    # --- Embedding into larger image and setting of heading ------------------
    _, height_map = img.size
    img = add_text_space(img, height_text_space)

    font_heading = get_sized_font(params.head_font_path, heading, img.width)
    end_y_heading = write_header(img, heading, font_heading, height_map, added_frame_px)

    # --- Embeds main text ----------------------------------------------------
    t = 'Aufgewachsen in Köln und Magdeburg, verliebt in München, zusammengezogen nach Heidelberg. Ich werde Dich für immer lieben!'
    font_height_heading = font_heading.getsize(heading)[1]

    main_text_font = ImageFont.truetype(params.main_font_path, 70)
    if params.text_coats:
        write_main_text_with_heraldry(
            t, 
            img, 
            main_text_font,
            70,
            30,
            [location.name.lower() for location in params.locations],
            height_map,
            # added_frame_px,
            # font_height_heading
            end_y_heading
        )

    else:
        write_main_text(img, t, main_text_font, end_y_heading)    
        # write_main_text(
            # img,
            # t,
            # main_text_font,
            # height_map,
            # added_frame_px,
            # font_height_heading
        # )

    # --- Sets a frame around image and saves ---------------------------------
    img = frame_img(img, added_frame_px, params.border_wanted)
    img.save(os.path.join(os.getcwd(), 'output', 'written.png'))

town_name_format = lambda word: word.lower().strip('.?,!:;_-%()"\'$€/')

def write_main_text_with_heraldry(
    text: str,
    img: Image.Image,
    font: ImageFont.ImageFont,
    font_size: int,
    line_spacing: int,
    town_names: List[str],
    height_cropped: int,
    # added_frame_px: int,
    # height_heading: int,
    end_y_heading: int, # The y position at which the heading ends.
    coat_text_gap: int = 15
):
    _, font_height = font.getsize('Tg')
    # start_y = height_cropped + added_frame_px + height_heading # + line_spacing
    start_y = end_y_heading + line_spacing
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
    resize_ratio = min(max_w / current_w, max_h / current_h)
    return (round(resize_ratio * current_w), round(resize_ratio * current_h))


def create_output_dir() -> None:
    """Creates a new output directory, if there is none."""

    working_dir_content = os.listdir(os.getcwd())
    if 'output' not in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def crop_map(img: Image.Image, cropping: Tuple[float, float, float, float]) -> Image.Image:
    """Crops the Cartopy map image.
    
    Args:
        raw_img_name (str): The name if the image file with the map in the output directory.
        cropping (Tuple[float, float, float, float]): Pixels from which map will be cropped (left, top, right, bottom).
    
    Returns:
        (Image, Tuple[int, int]): The changed image and the size of the cropped map.
    """
    img = img.crop(cropping)
    
    return img


def add_text_space(img: Image.Image, added_text_height: int) -> Image.Image:
    width_cropped, height_cropped = img.size
    dims_with_text = (width_cropped, height_cropped + added_text_height)
    img_text = Image.new(img.mode, dims_with_text, color = (255, ) * 3)
    img_text.paste(img, (0, 0))

    return img_text


def get_sized_font(font_path: str, text: str, img_width: int) -> Tuple[ImageFont.ImageFont, int]:
    """Erzeugt die Schriftgröße, die die gegebene Breite füllt.

    Args:
        font_path (str): [description]
        text (str): [description]

    Returns:
        ImageFont.ImageFont: [description]
    """
    font_size = 500 # Arbitrary but high start value
    font = ImageFont.truetype(font_path, font_size)
    font_width, _ = font.getsize(text) 

    while font_width > img_width:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_width, _ = font.getsize(text)
    
    return font


def write_header(
    img: Image.Image,
    text: str, 
    font: ImageFont.ImageFont,
    height_map_part: int, 
    frame_width: int,
    adjustment: int = -150
) -> int:
    """[summary]

    Args:
        img (Image.Image): [description]
        text (str): [description]
        font (ImageFont.ImageFont): [description]
        height_map_part (int): [description]
        frame_width (int): [description]
        adjustment (int, optional): [description]. Defaults to -20.

    Returns:
        int: The y position at which the heading stops.
    """
    draw = ImageDraw.Draw(img)
    start_y_heading = height_map_part + frame_width + adjustment 
    draw.text((0, start_y_heading), text, 'black', font)

    _, heading_height = font.getsize(text)
    end_y_heading = start_y_heading + heading_height
    return end_y_heading


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


def town_formatting(town_name: str) -> str:
    """Formats a town's name correctly.

    Args:
        town_name (str): The name.

    Returns:
        str: The formatted name.
    """
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
    img: Image.Image,
    text: str, 
    # font_path: str, # zu font
    # font_size: int,
    font: ImageFont.ImageFont,
    # height_cropped: int,
    # added_frame_px: int,
    # font_height: int,
    end_y_heading: int,
    line_spacing: int = 30
) -> Image.Image:
    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)

    # start_y = height_cropped + added_frame_px + font_height + line_spacing # Height of first heading
    # font = ImageFont.truetype(font_path, font_size)
    start_y = end_y_heading + line_spacing
    font_width, font_height = font.getsize(text)
    
    pattern = pattern_2nd_text(text, img_width, font)
    for vert_start, line in pattern:
        draw_pos = (vert_start, start_y)
        draw.text(draw_pos, line, (0, ) * 3, font)
        start_y += font_height + line_spacing
    
    return img


def frame_img(
    img: Image.Image, 
    added_frame_px: int, 
    border_wanted: bool, 
    border_thickness: int = 3
) -> Image.Image:
    """Puts a uniform frame around the image.

    Args:
        img (Image): The image around which the frame will be put.
        added_frame_px (int): Width of the frame.

    Returns:
        Image: [description]
    """
    # TODO Hier die Breite an gegebene Höhe so anpassen, dass das Verhältnis
    # Breite/Höhe 2/3 ist (12/18).
    # print('FRAMING FUNCTION')
    orig_width, orig_height = img.size
    # frame_dims = (orig_width + added_frame_px * 2, orig_height + added_frame_px * 2)
    new_frame_height = orig_height + added_frame_px
    new_frame_width = (12 / 18) * (orig_height + added_frame_px) # NOTE Falsch, added_frame_px beachten
    if new_frame_width < orig_width:
        raise ValueError(f'Neue Breite ist kleiner als alte {new_frame_width} zu {orig_width}.')
    
    
    frame_dims = (round(new_frame_width), round(new_frame_height))
    # print(frame_dims)
    framed_img = Image.new(img.mode, frame_dims, (255, ) * 3)

    addtional_width = round(new_frame_width - orig_width)
    pasting_pos = (round(addtional_width / 2), round(added_frame_px / 2))
    framed_img.paste(img, pasting_pos)
    
    if border_wanted:
        half_frame_px = round(added_frame_px / 2) # Halbe Randbreite
        upper_left_corner = (half_frame_px, ) * 2
        upper_right_corner = (new_frame_width - half_frame_px, half_frame_px)
        lower_left_corner = (half_frame_px, new_frame_height - half_frame_px)
        lower_right_corner = (new_frame_width - half_frame_px, new_frame_height - half_frame_px)
        shape = [upper_left_corner, upper_right_corner, lower_right_corner, lower_left_corner, upper_left_corner]

        drawing = ImageDraw.Draw(framed_img)
        drawing.line(shape, width = border_thickness, fill = 'black')
    
    return framed_img


if __name__ == '__main__':
    logging.warn('Ich starte.')
    main()
    logging.critical('Ich beende.')
    