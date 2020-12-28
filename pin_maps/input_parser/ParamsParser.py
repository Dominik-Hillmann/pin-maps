# Python libraries
import argparse
import json
import os
from copy import deepcopy
# Internal modules
from input_parser.Coordinates import Coordinates
# External modules
from PIL import ImageFont
# Typing
from typing import Union, List, Tuple


class ParamsParser:
    """Class that makes it easy to retrieve parsed parameters."""

    __standard_head_font = os.path.join('data', 'fonts', 'grandhotel.ttf')
    __standard_main_font = os.path.join('data', 'fonts', 'josefin-sans-regular.ttf')
    __standard_marker_name = 'heraldry'

    def __init__(self):
        # Load configuration file.
        with open('config.json', 'r') as config_file:
            self.__config = json.load(config_file)


        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--country',
            required = True,
            type = str,
            help = 'The country shape which will be displayed.'
        )
        parser.add_argument(
            '--heading',
            type = str,
            required = True,
            help = 'The header line.'
        )
        parser.add_argument(
            '-b', '--body',
            required = True,
            type = str,
            help = 'The main text body below the header.'
        )
        parser.add_argument(
            '-t', '--towns',
            type = str,
            help = 'A list of names of locations. They will automatically ' + 
            'resolved to coordinates, if they can be found.'
        )
        parser.add_argument(
            '-m', '--marker',
            type = str,
            help = 'The name of the image the locations will be marked with.'
        )
        parser.add_argument(
            '-f', '--fonts',
            nargs = 2,
            type = str,
            help = 'The name of the fonts. The first will be used for the header, ' + 
            'the second for the body.'
        )
        parser.add_argument(
            '--ribbons',
            action = 'store_true',
            help = 'Whether ribbons should be added to the pins.'
        )
        parser.add_argument(
            '--notextcoats',
            action = 'store_true',
            help = 'Whether heraldry should be displayed in the text below.'
        )
        parser.add_argument(
            '--noborder',
            action = 'store_true',
            help = 'Whether a thin border will surround the image and the text.'
        )
        parser.add_argument(
            '--nologo',
            action = 'store_true',
            help = 'Use if you do not want the logo at the bottom.'
        )
        parser.add_argument(
            '--superscale',
            action = 'store_true',
            help = "Set, if you want to upscale the image by the factor 4."
        )

        self.__parsed_args = vars(parser.parse_args())
        print(self.__parsed_args)

        # COUNTRY POSSIBILITY COUNTRY
        possib_countries = list(self.__config['countries'].keys())
        country = self.__parsed_args['country']
        if country not in possib_countries:
            raise ValueError(
                f'Selected country "{country}" not in the list of available countries: ' + 
                f'{", ".join(possib_countries)} are possible.'
            )
        
        # CHECK POSSIBILITY FONT
        fonts = self.__parsed_args['fonts']
        possib_fonts = list(self.__config['fonts'].keys())
        if fonts is not None:
            for font in fonts:
                if font not in possib_fonts:
                    raise ValueError(f'Font "{font}" not available; available are: {", ".join(possib_fonts)}.')
        
        # CHECK POSSIBILITY MARKERS
        marker = self.__parsed_args['marker']
        possib_markers = list(self.__config['markers'].keys())
        if (marker not in possib_markers) and (marker is not None):
            raise ValueError(f'Marker {marker} not available; available are: {", ".join(possib_markers)}.')
        
        # PARSING ALL POSITIONS
        name_pins = self.__parsed_args['towns']
        if name_pins is not None:
            sep = ','
            name_pins = [town.replace(sep, '').lstrip().strip() for town in name_pins.split(sep)]
        else:
            name_pins = []
        self.locations = []
        for location in name_pins:
            try:
                self.locations.append(Coordinates(location))
            except NameError as e:
                print(str(e))    
                continue

        # RIBBON
        self.ribbons = self.__parsed_args['ribbons']
        # TEXT COATS
        self.text_coats = not self.__parsed_args['notextcoats']
        # BORDER
        self.border_wanted = not self.__parsed_args['noborder']


    @property
    def marker_symbol(self):
        available_markers = self.__config['markers']
        try:
            marker_name = available_markers[self.__parsed_args['marker']]
            return os.path.join('data', 'img', marker_name)
        except KeyError:
            return available_markers[self.__standard_marker_name]

    
    @property
    def body(self) -> Union[str, None]:
        return self.__parsed_args['body']


    @property
    def heading(self) -> str:
        return self.__parsed_args['heading']

    
    @property
    def head_font_path(self) -> str:
        try:
            font_name = self.__config['fonts'][self.__parsed_args['fonts'][0]]
            return os.path.join('data', 'fonts', font_name)
        except TypeError:
            return self.__standard_head_font

    
    @property
    def main_font_path(self) -> str:
        try:
            font_name = self.__config['fonts'][self.__parsed_args['fonts'][1]]
            return os.path.join('data', 'fonts', font_name)
        except TypeError:
            return self.__standard_main_font

    
    @property
    def country(self) -> str:
        possib_countries = self.__config['countries']
        country_data = deepcopy(possib_countries[self.__parsed_args['country']])
        del country_data['wallpapers']
        
        return country_data


    @property
    def logo_wanted(self) -> bool:
        return not self.__parsed_args['nologo']


    @property
    def superscale_wanted(self) -> bool:
        return self.__parsed_args['superscale']


    @property
    def added_frame_px(self) -> int:
        return self.__config['general']['added-frame-px']


    @property
    def height_text_space(self) -> int:
        return self.__config['general']['height-text-space']

    
    @property
    def undertitle_line_spacing(self) -> int:
        return self.__config['general']['undertitle-line-spacing']

    
    @property
    def logo_height(self) -> int:
        """The height of the logo at the lower image end.

        Returns:
            int: The height.
        """
        return self.__config['general']['logo-height']
