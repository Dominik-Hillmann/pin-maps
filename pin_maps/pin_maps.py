# Internal modules
from input_parser.ParamsParser import ParamsParser 
# Python libraries
import os
# External modules
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


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


def main() -> None:
    create_output_dir()
    img = Image.open(os.path.join('output', 'test.png'))
    print(img)
    print(img.size)
    (left, right, top, bottom) = (300, 1745, 650, 2580)
    img = img.crop((left, top, right, bottom))
    print(img.__doc__)
    print(img.crop.__doc__)
    width_cropped, height_cropped = img.size
    print(width_cropped, height_cropped)

    dims_new = (width_cropped, height_cropped + 500)
    img_new = Image.new(img.mode, dims_new, (255, ) * 3)
    img_new.paste(img, (0, 0))
    
    img_new.save(os.path.join(os.getcwd(), 'output', 'edited.png'))
    
    text = u'Das ist ein Test äöü!'

    font = ImageFont.load_default().font
    img_new_width, img_new_height = img_new.size
    font_size = 500 # Arbitrary start value
    anton_font = ImageFont.truetype('anton.ttf', font_size)
    font_width, font_height = anton_font.getsize(text) 
    
    print('Img dims:', img_new_width)
    print(f'Width: {font_width}, Size: {font_size}')
    while font_width > img_new_width:
        print(f'Width: {font_width}, Size: {font_size}')
        font_size -= 1
        anton_font = ImageFont.truetype('anton.ttf', font_size)
        font_width, font_height = anton_font.getsize(text)


    print('Size Anton:', anton_font.getsize(text))
    playfair_font = ImageFont.truetype('playfair.ttf', 120)
    print('playfair size:', playfair_font.getsize(text))
    
    added_frame_px = 150
    draw = ImageDraw.Draw(img_new)
    draw.text((0, height_cropped + added_frame_px), text, 'black', anton_font)

    framed_img = frame_img(img_new, added_frame_px)
    framed_img.save(os.path.join(os.getcwd(), 'output', 'written.png'))
    
    # img_new.save(os.path.join(os.getcwd(), 'output', 'written.png'))

if __name__ == '__main__':
    main()
