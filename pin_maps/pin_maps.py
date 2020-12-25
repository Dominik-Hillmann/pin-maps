#!/usr/bin/env python
"""This program designs posters of maps with pins and undertitles."""









# Upscaling redbubble
# import cv2
from cv2 import dnn_superres
import numpy as np
















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

    height_text_space = 930
    added_frame_px = 150

    # --- Map creation and pin setting ----------------------------------------
    img_transforms = [BackgroundDeletion(), Cutout(), Scale(110), AddShadow()]
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
    cropping = (300, 650, 1760, 2525) # (left, top, right, bottom)
    img = Image.open(os.path.join('output', raw_img_name))    
    img = crop_map(img, cropping)

    # --- Embedding into larger image and setting of heading ------------------
    _, height_map = img.size
    img = add_text_space(img, height_text_space)

    font_heading = get_sized_font(params.head_font_path, params.heading, img.width)
    end_y_heading = write_header(img, params.heading, font_heading, height_map, added_frame_px)

    # --- Embeds main text ----------------------------------------------------
    # t = 'Aufgewachsen in Köln und Magdeburg, verliebt in München, zusammengezogen nach Heidelberg. Ich werde Dich für immer lieben!'
    font_height_heading = font_heading.getsize(params.heading)[1]

    main_text_font = ImageFont.truetype(params.main_font_path, 70)
    if params.text_coats:
        town_names = [location.name.lower() for location in params.locations]
        write_main_text_with_heraldry(img, params.body, main_text_font, 30, town_names, end_y_heading)
    else:
        write_main_text(img, params.body, main_text_font, end_y_heading)

    # --- Sets a frame around image and saves ---------------------------------
    img = frame_img(img, added_frame_px, params.border_wanted)
    if params.logo_wanted:
        img = add_logo(img, added_frame_px)

    print(params.superscale_wanted)
    if params.superscale_wanted:
        img = superscale(img)

    img.save(os.path.join(os.getcwd(), 'output', 'written.png'))


def superscale(img: Image.Image, scal_factor: int = 4, model_name: str = 'lapsrn') -> Image.Image:
    """Performs upscaling with superresolution neural networks.
    At the moment, OpenCV offers four models, three of which you can choose here:
    LAPSRN, ESPCN, FSRCNN. Which can upscale by the factor of 4.
    Other versions can be downloaded too, the EDSR model is too large and too slow.

    Quellen:
    https://towardsdatascience.com/deep-learning-based-super-resolution-with-opencv-4fd736678066
    https://docs.opencv.org/master/d5/d29/tutorial_dnn_superres_upscale_image_single.html


    Args:
        img (Image.Image): Image to be upscaled.
        scal_factor (int, optional): Factor by which the input image will be upscaled. Defaults to 4.
        model_name (str, optional): The name of the model you want to use, available are lapsrn, espcn
        and fsrcnn. Defaults to lapsrn.

    Returns:
        Image.Image: [description]
    """
    superscaler = dnn_superres.DnnSuperResImpl_create()
    model_path = os.path.join('data', 'models', f'{model_name.upper()}_x{scal_factor}.pb')
    superscaler.readModel(model_path)
    superscaler.setModel(model_name, scal_factor)

    img = img.convert('RGB')
    img = np.array(img)
    img = superscaler.upsample(img)
    img = Image.fromarray(img.astype('uint8'), 'RGB')
    return img

# --- Functions placing the raw map into the later total image ----------------
def crop_map(img: Image.Image, cropping: Tuple[float, float, float, float]) -> Image.Image:
    img = img.crop(cropping)    
    return img


def add_text_space(img: Image.Image, added_text_height: int) -> Image.Image:
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
    draw = ImageDraw.Draw(img)
    start_y_heading = height_map_part + frame_width + adjustment 
    draw.text((0, start_y_heading), text, 'black', font)

    _, heading_height = font.getsize(text)
    end_y_heading = start_y_heading + heading_height

    return end_y_heading


# --- Functions concerned with writing the main undertitles (not heading) -----
def pattern_2nd_text(text: str, img_width: int, font: ImageFont, line_dist: int = 10) -> List[Tuple[int, str]]:
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


def calc_pattern_size(
    pattern: Union[List[Tuple[int, str]], List[Tuple[bool, List[str]]]],
    line_spacing: int = 30
) -> Tuple[int, int]:
    if type(pattern[0][0]) is int:
        pass
    elif type(patter[0][0]) is bool:
        pass
    else:
        pass


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
    font: ImageFont.ImageFont,
    end_y_heading: int,
    line_spacing: int = 30
) -> Image.Image:
    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)

    start_y = end_y_heading + line_spacing
    font_width, font_height = font.getsize(text)
    
    pattern = pattern_2nd_text(text, img_width, font)
    for vert_start, line in pattern:
        draw_pos = (vert_start, start_y)
        draw.text(draw_pos, line, (0, ) * 3, font)
        start_y += font_height + line_spacing
    
    return img


def write_main_text_with_heraldry(
    img: Image.Image,
    text: str,
    font: ImageFont.ImageFont,
    line_spacing: int,
    town_names: List[str],
    end_y_heading: int, # The y position at which the heading ends.
    coat_text_gap: int = 15
) -> None:
    _, font_height = font.getsize('Tg')
    
    start_y = end_y_heading + line_spacing
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

    print(added_width_of_line_by_coat)
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


# --- Functions adding last details to the image ------------------------------
def frame_img(img: Image.Image, added_frame_px: int, border_wanted: bool, border_thickness: int = 3) -> Image.Image:
    orig_width, orig_height = img.size
    new_frame_height = orig_height + added_frame_px
    new_frame_width = (12 / 18) * (orig_height + added_frame_px)
    if new_frame_width < orig_width:
        raise ValueError(f'Neue Breite ist kleiner als alte {new_frame_width} zu {orig_width}.')
        
    frame_dims = (round(new_frame_width), round(new_frame_height))
    framed_img = Image.new(img.mode, frame_dims, (255, ) * 3)

    addtional_width = round(new_frame_width - orig_width)
    pasting_pos = (round(addtional_width / 2), round(added_frame_px / 2))
    framed_img.paste(img, pasting_pos)
    
    if border_wanted:
        half_frame_px = round(added_frame_px / 2) # Halbe Breits des Rands
        upper_left_corner = (half_frame_px, ) * 2
        upper_right_corner = (new_frame_width - half_frame_px, half_frame_px)
        lower_left_corner = (half_frame_px, new_frame_height - half_frame_px)
        lower_right_corner = (new_frame_width - half_frame_px, new_frame_height - half_frame_px)
        shape = [upper_left_corner, upper_right_corner, lower_right_corner, lower_left_corner, upper_left_corner]

        drawing = ImageDraw.Draw(framed_img)
        drawing.line(shape, width = border_thickness, fill = 'black')
    
    return framed_img


def add_logo(img: Image.Image, added_frame_px: int) -> Image.Image:
    logo = Image.open(os.path.join('data', 'img', 'brainrain-logo-lang.jpg'))
    logo = logo.resize(proportional_size(50, logo))
    logo_width, logo_height = logo.size
    
    half_img_width = round(img.width / 2)
    half_logo_width = round(logo_width / 2)
    paste_pos = (
        half_img_width - half_logo_width, 
        img.height - logo_height - 50
    )
    img.paste(logo, paste_pos)

    return img

    
# --- Utility functions -------------------------------------------------------
def create_output_dir() -> None:
    """Creates a new output directory, if there is none."""
    working_dir_content = os.listdir(os.getcwd())
    if 'output' not in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def town_formatting(town_name: str) -> str:
    return town_name.lower().strip('.?,!:;-%()"\'$€/')


def get_sized_font(font_path: str, text: str, img_width: int) -> Tuple[ImageFont.ImageFont, int]:
    font_size = 500 # Arbitrary but high start value
    font = ImageFont.truetype(font_path, font_size)
    font_width, _ = font.getsize(text) 

    while font_width > img_width:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_width, _ = font.getsize(text)
    
    return font


def get_coat_from_cache(town_name):
    return Image.open(os.path.join('data', 'img', 'pin-cache', f'{town_name}-pin.png'))


def proportional_size(set_height, img) -> Tuple[int, int]:
    current_w, current_h = img.size
    max_w, max_h = current_w, set_height,
    resize_ratio = min(max_w / current_w, max_h / current_h)
    return (round(resize_ratio * current_w), round(resize_ratio * current_h))


if __name__ == '__main__':
    main()
    