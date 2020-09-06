# Internal modules
from input_parser.ParamsParser import ParamsParser
# Python libraries
import os
from copy import deepcopy 
# External modules
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
# Typing
from typing import List, Tuple


def create_output_dir() -> None:
    working_dir_content = os.listdir(os.getcwd())
    if not 'output' in working_dir_content:
        os.mkdir(os.path.join(os.getcwd(), 'output'))


def frame_img(img: Image, added_frame_px: int) -> Image:
    width, height = img.size
    frame_dims = (width + added_frame_px * 2, height + added_frame_px * 2)
    framed_img = Image.new(img.mode, frame_dims, (255, ) * 3)
    framed_img.paste(img, (added_frame_px, ) * 2)

    return framed_img


def pattern_2nd_text(
    text: str, 
    img_width: int, 
    # start_height: int, 
    font: ImageFont, 
    font_size: int = 80, 
    line_dist: int = 10
) -> List[Tuple[int, str]]:
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


def main() -> None:
    height_text_space = 700
    text = u'Inge & Maik-Günter'
    added_frame_px = 150

    ### DIR, CROPPING & ERWEITERUNG ###
    create_output_dir()
    img = Image.open(os.path.join('output', 'test.png'))
    (left, right, top, bottom) = (300, 1745, 650, 2580)
    img = img.crop((left, top, right, bottom))
    width_cropped, height_cropped = img.size

    dims_new = (width_cropped, height_cropped + height_text_space)
    img_new = Image.new(img.mode, dims_new, (255, ) * 3)
    img_new.paste(img, (0, 0))
    img_new.save(os.path.join(os.getcwd(), 'output', 'edited.png'))
    
    ### WRITING FIRST HEADER ###
    img_new_width, img_new_height = img_new.size
    font_size = 500 # Arbitrary start value
    anton_font = ImageFont.truetype('open-sans-bold.ttf', font_size)
    font_width, font_height = anton_font.getsize(text) 
    
    print(f'Width: {font_width}, Size: {font_size}')
    while font_width > img_new_width:
        print(f'Width: {font_width}, Size: {font_size}')
        font_size -= 1
        anton_font = ImageFont.truetype('open-sans-bold.ttf', font_size)
        font_width, font_height = anton_font.getsize(text)

    print('Size Anton:', anton_font.getsize(text))
  
    # Add text below using the width of the frame that will be added later on.
    adjustment = 20 # Number of adjustment pixels to make text look better
    draw = ImageDraw.Draw(img_new)
    draw.text((0, height_cropped + added_frame_px - adjustment), text, 'black', anton_font)
    # draw.text((0, height_cropped), text, 'black', anton_font)

    ### WRITING SECOND HEADER ###
    line_spacing = 30

    t = 'Das ist ein sehr langer Text. ' * 5 
    hori_start = height_cropped + added_frame_px + font_height + line_spacing # Height of first heading

    font_below = ImageFont.truetype('prata-regular.ttf', 70)
    font_below_width, font_below_height = font_below.getsize(t)
    
    pattern = pattern_2nd_text(t, img_new_width, font_below)
    for vert_start, line in pattern:
        draw_pos = (vert_start, hori_start)
        draw.text(draw_pos, line, 'black', font_below)
        hori_start += font_below_height + line_spacing


    ### FRAMING ###
    framed_img = frame_img(img_new, added_frame_px)
    framed_img.save(os.path.join(os.getcwd(), 'output', 'written.png'))
    
    # Eigentliche Schritte zum richtigen Einrichten der Bildunterschrift
    # Ermittle Hauptzeile, packe ganz oben hin, einzeilig, gemacht
    # Danach Zweitsatz solange aufteilen, bis auf fester Größe in den Rahmen
    # Platziere die Zeilen so, dass Rand unten und zur Hauptzeile gleich groß

    # img_new.save(os.path.join(os.getcwd(), 'output', 'written.png'))

if __name__ == '__main__':
    main()
