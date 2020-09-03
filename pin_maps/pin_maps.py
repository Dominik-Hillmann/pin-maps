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
    

def main() -> None:
    create_output_dir()
    img = Image.open(os.path.join('output', 'test.png'))
    print(img)
    print(img.size)
    (left, right, top, bottom) = (300, 1745, 650, 2580)
    img = img.crop((left, top, right, bottom))
    width_cropped, height_cropped = img.size
    print(width_cropped, height_cropped)

    dims_new = (width_cropped, height_cropped + 500)
    img_new = Image.new(img.mode, dims_new, (255, 255, 255))
    img_new.paste(img, (0, 0))
    
    img_new.save(os.path.join(os.getcwd(), 'output', 'edited.png'))
    
    text = u'Das ist ein Test äöü!'

    font = ImageFont.load_default().font
    anton_font = ImageFont.truetype('anton.ttf', 120)
    print('Size Anton:', anton_font.getsize(text))
    playfair_font = ImageFont.truetype('playfair.ttf', 120)
    print('playfair size:', playfair_font.getsize(text))

    draw = ImageDraw.Draw(img_new)
    draw.text((200, 1620), text, 'black', playfair_font)
    img_new.save(os.path.join(os.getcwd(), 'output', 'written.png'))


if __name__ == '__main__':
    main()
