#!/usr/bin/env python
"""This program designs posters of maps with pins and undertitles."""

# Internal modules
from input_parser.ParamsParser import ParamsParser
from heraldry_transforms.AddShadow import AddShadow
from heraldry_transforms.BackgroundDeletion import BackgroundDeletion
from heraldry_transforms.Ribbon import Ribbon
from heraldry_transforms.OffsetLettering import OffsetLettering
from heraldry_transforms.Scale import Scale
from heraldry_transforms.Cutout import Cutout
from complete_image_transforms.CompleteImageTransform import CompleteImageTransform
from complete_image_transforms.Superscale import Superscale
from complete_image_transforms.Frame import Frame
from complete_image_transforms.Logo import Logo
from draw.Map import Map
from draw.Pin import Pin
# Python libraries
import os
from copy import deepcopy
from time import time
import logging
import random
from datetime import datetime
# External modules
from PIL import Image, ImageDraw, ImageFont
# Typing
from typing import List, Tuple, Union
# Settings
random.seed(69)


def main() -> None:
    params = ParamsParser()
    create_output_dir()

    # --- Map creation and pin setting ----------------------------------------
    img_transforms = [BackgroundDeletion(), Cutout(), Scale(110), AddShadow()]
    # TODO Cropping und Koordination des Kartenausschnitts in die config.json
    germany = Map('de-neg.shp', 'old-topo.png', [5.32, 15.55, 47.2, 56.2])
    
    for location in params.locations:
        logging.info('Creating pin: ' + location.name)
        specific_transforms = img_transforms + [Ribbon(location.name)] if params.ribbons else img_transforms
        try:
            pin = Pin(location, params.marker_symbol, specific_transforms)
        except (ConnectionRefusedError, LookupError) as e:
            logging.warn(f'Had to skip pin at position {str(location)} due to {str(e)}.')
            continue

        germany.add_pin(pin)

    raw_img_name = f'raw-{round(time())}.png'
    germany.save(raw_img_name)

    # --- Map cropping --------------------------------------------------------
    # TODO Cropping und Koordination des Kartenausschnitts in die config.json
    cropping = (300, 650, 1760, 2525) # (left, top, right, bottom)
    img = Image.open(os.path.join('output', raw_img_name))    
    img = crop_map(img, cropping)

    # --- Embedding into larger image and setting of heading ------------------
    _, height_map = img.size
    img = add_text_space(img, params.height_text_space)

    font_heading = get_sized_font(params.head_font_path, params.heading, img.width)
    end_y_heading = write_header(img, params.heading, font_heading, height_map, params.added_frame_px)

    # --- Embeds main text ----------------------------------------------------
    font_height_heading = font_heading.getsize(params.heading)[1]

    main_text_font = ImageFont.truetype(params.main_font_path, 70)
    # start_y_undertitles = calc_start_y_undertitles(img, params.body, main_text_font, end_y_heading, params.undertitle_line_spacing, params.text_coats)
    if params.text_coats:
        town_names = [location.name.lower() for location in params.locations]
        write_main_text_with_heraldry(img, params.body, main_text_font, params.undertitle_line_spacing, town_names, end_y_heading)
    else:
        write_main_text(img, params.body, main_text_font, end_y_heading, params.undertitle_line_spacing)

    # --- Edits of the complete image -----------------------------------------
    complete_img_transforms = get_complete_img_transforms(params)
    for transform in complete_img_transforms:
        img = transform(img)

    img.save(os.path.join(os.getcwd(), 'output', 'written.png'))


# --- Functions placing the raw map into the later total image ----------------
def crop_map(img: Image.Image, cropping: Tuple[float, float, float, float]) -> Image.Image:
    """Crops the raw map such that there is no white space around it.

    Args:
        img (Image.Image): The image to be cropped.
        cropping (Tuple[float, float, float, float]): Croppings.

    Returns:
        Image.Image: The cropped image.
    """
    img = img.crop(cropping)    
    return img


def add_text_space(img: Image.Image, added_text_height: int) -> Image.Image:
    """Adds a space where text can be placed under the raw map.

    Args:
        img (Image.Image): The image where the space will be added.
        added_text_height (int): The height of the space in pixels.

    Returns:
        Image.Image: The image with text space added.
    """
    width_cropped, height_cropped = img.size
    dims_with_text = (width_cropped, height_cropped + added_text_height)
    img_text = Image.new(img.mode, dims_with_text, color = (255, ) * 3)
    img_text.paste(img, (0, 0))

    return img_text


# --- Functions for writing the heading ---------------------------------------
def write_header(
    img: Image.Image,
    text: str, 
    font: ImageFont.ImageFont,
    height_map_part: int, 
    frame_width: int,
    adjustment: int = -150
) -> int:
    """Inserts the header into the image.

    Args:
        img (Image.Image): The image where the header will be inserted.
        text (str): The text to be inserted.
        font (ImageFont.ImageFont): The font used for the heading.
        height_map_part (int): The height of the raw map.
        frame_width (int): The width of the frame.
        adjustment (int, optional): Adjustment to the height. Defaults to -150.

    Returns:
        int: The lowest y position to which the heading reaches.
    """
    draw = ImageDraw.Draw(img)
    start_y_heading = height_map_part + frame_width + adjustment 
    draw.text((0, start_y_heading), text, 'black', font)

    _, heading_height = font.getsize(text)
    end_y_heading = start_y_heading + heading_height

    return end_y_heading


# --- Functions concerned with writing the main undertitles (not heading) -----
def pattern_2nd_text(text: str, img_width: int, font: ImageFont, line_dist: int = 10) -> List[Tuple[int, str]]:
    """Creates the pattern of the undertitles.

    Args:
        text (str): The text to be inserted as undertitles.
        img_width (int): The width of the image.
        font (ImageFont): The font used for undertitles.
        line_dist (int, optional): Distance between lines. Defaults to 10.

    Returns:
        List[Tuple[int, str]]: The pattern.
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


def pattern_2nd_text_with_coats(
    text: str,
    img: Image.Image,
    font: ImageFont.ImageFont,
    line_spacing: int,
    town_names: List[str],
    coats_width: int = 150
) -> List[Tuple[bool, List[str]]]:
    """Creates the pattern of the undertitles including coats of arms.

    Args:
        text (str): The text to be inserted as undertitles.
        img (Image.Image): The image into which undertitles will be inserted.
        font (ImageFont.ImageFont): The font of the undertitles.
        line_spacing (int): The spacing between lines in pixels.
        town_names (List[str]): The list of the names of the towns for which 
        heraldry is provided.
        coats_width (int, optional): The width of the coats of arms in the text. 
        Defaults to 150.

    Returns:
        List[Tuple[bool, List[str]]]: The pattern.
    """
    pattern = []
    for start_x, line in pattern_2nd_text(text, img.width - coats_width, font, line_spacing):
        words = line.split(' ')
        line_pattern = [(False, [])]

        num_coats = 0
        for word in words:
            n_splits = len(line_pattern)
            if town_formatting(word) in town_names:
                line_pattern.append((True, [word]))
                num_coats += 1
            else:
                line_pattern[n_splits - 1][1].append(word)
        
        if line_pattern[0] == (False, []):
            line_pattern = line_pattern[1:]
        
        pattern.append((start_x, line_pattern, num_coats))

    return pattern


def calc_start_y_undertitles(
    img: Image.Image, 
    undertitles_text: str, 
    undertitles_font: ImageFont.ImageFont,
    end_y_heading: int,
    line_spacing: int,
    town_names: Union[None, List[str]]
) -> int:
    """Calculates where to put the undertitles.

    Args:
        img (Image.Image): The image into which the undertitles will be put.
        undertitles_text (str): The undertitle as string.
        undertitles_font (ImageFont.ImageFont): The font of the undertitles.
        end_y_heading (int): The lowest y position of the heading.
        line_spacing (int): The spacing between the lines of the undertitles.
        town_names (Union[None, List[str]]): The names of possible towns.

    Returns:
        int: The y position at which the undertitles to start.
    """
    img_width, img_height = img.size
    empty_height = img_height - end_y_heading

    coats_wanted = town_names is not None
    if coats_wanted:
        pattern = pattern_2nd_text_with_coats(undertitles_text, img, undertitles_font, line_spacing, town_names)
        lines = [compile_to_line(line) for _, line, _ in pattern]
    else:
        pattern = pattern_2nd_text(undertitles_text, img.width, undertitles_font, line_dist = line_spacing)    
        lines = [line for _, line in pattern]

    num_lines = len(lines)
    num_gaps = num_lines - 1
    _, line_height = undertitles_font.getsize('Tg')

    undertitles_height = line_height * num_lines + line_spacing * num_gaps
    assert empty_height > undertitles_height
    diff = empty_height - undertitles_height

    return round(diff / 2)


def compile_to_line(line_pattern: List[Tuple[bool, List[str]]]) -> List[Union[Image.Image, str]]:
    """Will convert the pattern into actual lines.

    Args:
        line_pattern (List[Tuple[bool, List[str]]]): The pattern to be compiled.

    Returns:
        List[Union[Image.Image, str]]: The lines as list of images and strings.
    """
    written_line = []
    for coat_wanted, words in line_pattern:
        if coat_wanted:
            written_line.append(get_coat_from_cache(town_formatting(words[0])))
        written_line.append(' '.join(words))

    return written_line


def write_main_text(
    img: Image.Image,
    text: str,
    font: ImageFont.ImageFont,
    end_y_heading: int,
    line_spacing: int
) -> None:
    """Inserts the undertitles into the image.

    Args:
        img (Image.Image): The image into which undertitles will be inserted.
        text (str): The text to be inserted.
        font (ImageFont.ImageFont): The font used for the inserted text.
        end_y_heading (int): The lowest y of the heading.
        line_spacing (int, optional): Spacing between lines. Defaults to 30.

    Returns:
        Image.Image: The image into which undertitles are inserted.
    """
    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)

    # start_y = end_y_heading + line_spacing
    # TODO hier start y einsetzen
    start_y = calc_start_y_undertitles(img, text, font, end_y_heading, line_spacing, None) + end_y_heading
    font_width, font_height = font.getsize(text)
    
    pattern = pattern_2nd_text(text, img_width, font)
    for vert_start, line in pattern:
        draw_pos = (vert_start, start_y)
        draw.text(draw_pos, line, (0, ) * 3, font)
        start_y += font_height + line_spacing


def write_main_text_with_heraldry(
    img: Image.Image,
    text: str,
    font: ImageFont.ImageFont,
    line_spacing: int,
    town_names: List[str],
    end_y_heading: int, # The y position at which the heading ends.
    coat_text_gap: int = 15
) -> None:
    """Inserts the undertitles into the image uncluding heraldry.

    Args:
        img (Image.Image): The image into which undertitles will be inserted.
        text (str): The text to be inserted.
        font (ImageFont.ImageFont): The font used for the inserted text.
        line_spacing (int): Spacing between lines.
        town_names (List[str]): The town names for which coats are provided.
        end_y_heading (int): The lowest y position of the heading.
    """
    _, font_height = font.getsize('Tg')
    
    # start_y = end_y_heading + line_spacing TODO hier start_y einsetzen
    start_y = calc_start_y_undertitles(img, text, font, end_y_heading, line_spacing, town_names) + end_y_heading
    complete_text_pattern = pattern_2nd_text_with_coats(text, img, font, line_spacing, town_names)
    
    added_width_of_line_by_coat = []
    for _, line_pattern, _ in complete_text_pattern:
        line = compile_to_line(line_pattern)
        added_width_in_this_line = 0
        for line_element in line:
            if type(line_element) is not str:
                element_width, _ = proportional_size(font_height, line_element)
                added_width_in_this_line += element_width + 2 * coat_text_gap
        
        added_width_of_line_by_coat.append(added_width_in_this_line)

    for iter_num, (start_x, line_pattern, num_coats) in enumerate(complete_text_pattern):
        added_coat_width = added_width_of_line_by_coat[iter_num]
        print(max(added_width_of_line_by_coat) - added_coat_width)
        start_x += round((max(added_width_of_line_by_coat) - added_coat_width) / 2)
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


# --- Functions for edits concerning the complete image -----------------------
def get_complete_img_transforms(params: ParamsParser) -> List[CompleteImageTransform]:
    """Creates the list of transformations applied to the complete image.

    Args:
        params (ParamsParser): The command line parameters.

    Returns:
        List[CompleteImageTransform]: The list of transformations.
    """
    transforms = [Frame(params.added_frame_px, params.border_wanted)]

    if params.logo_wanted:
        transforms.append(Logo())

    if params.superscale_wanted:
        transforms.append(Superscale())
    
    return transforms


# --- Utility functions -------------------------------------------------------
def create_output_dir() -> None:
    """Creates a new output directory, if there is none."""
    working_dir_content = os.listdir(os.getcwd())
    if 'output' not in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def town_formatting(town_name: str) -> str:
    """Formats the town name (first letter upper case) and deletion of special
    symbols.

    Args:
        town_name (str): The town name to be formatted.

    Returns:
        str: The formatted town name.
    """
    return town_name.lower().strip('.?,!:;-%()"\'$€/')


def get_sized_font(font_path: str, text: str, img_width: int) -> ImageFont.ImageFont:
    """Creates a fitting font.

    Args:
        font_path (str): The path to the font file (*.ttf).
        text (str): The text for which font should be found.
        img_width (int): The width of the image where text will be inserted.

    Returns:
        ImageFont.ImageFont: The fitting font.
    """
    font_size = 500 # Arbitrary but high start value
    font = ImageFont.truetype(font_path, font_size)
    font_width, _ = font.getsize(text) 

    while font_width > img_width:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_width, _ = font.getsize(text)
    
    return font


def get_coat_from_cache(town_name: str) -> Image.Image:
    """Returns the coat of arms as retrieved from the cache.

    Args:
        town_name (str): The name of the coat of arms.

    Returns:
        Image.Image: The coat of arms.
    """
    return Image.open(os.path.join('data', 'img', 'pin-cache', f'{town_name}-pin.png'))


def proportional_size(set_height: int, img: Image.Image) -> Tuple[int, int]:
    """Computes the new size of the image proportional to new height (`set_height`).

    Args:
        set_height (int): The height for which you search proportional dimensions.
        img (Image.Image): The images with original dimensions.

    Returns:
        Tuple[int, int]: The proportional new size.
    """
    current_w, current_h = img.size
    max_w, max_h = current_w, set_height,
    resize_ratio = min(max_w / current_w, max_h / current_h)
    return (round(resize_ratio * current_w), round(resize_ratio * current_h))


if __name__ == '__main__':
    main()
    