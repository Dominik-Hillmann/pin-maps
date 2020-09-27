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
            '-w', '--wallpaper',
            required = True,
            type = str,
            help = 'The background image of the country shape.'
        )
        parser.add_argument(
            '-s', '--super',
            type = str,
            help = 'The header line.'
        )
        parser.add_argument(
            '-b', '--body',
            type = str,
            help = 'The main text body below the header.'
        )
        parser.add_argument(
            '-t', '--towns',
            nargs = '+', 
            type = str,
            help = 'A list of names of locations. They will automatically ' + 
            'resolved to coordinates, if they can be found.'
        )
        parser.add_argument(
            '-m', '--markers',
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
            '-a', '--latitudes',
            nargs = '+',
            type = float,
            help = 'A list of the latitudes of the pins. The lists of ' + 
            'latitudes and longitudes need to have the same length.'
        )
        parser.add_argument(
            '-o', '--longitudes',
            nargs = '+',
            type = float,
            help = 'A list of the longitudes of the pins. The lists of ' + 
            'latitudes and longitudes need to have the same length.'
        )

        self.__parsed_args = vars(parser.parse_args())
        print(self.__parsed_args)
        print()
        print(self.__config)
        # Checks pin positions.
        lats = self.__parsed_args['latitudes']
        lons = self.__parsed_args['longitudes']
        if lats is not None and lons is not None:
            if len(lats) != len(lons):
                raise ValueError('Latitudes and longitudes need to have the same length.')
        
        # Checks available countries, wallpapers and fonts.
        possib_countries = list(self.__config['countries'].keys())
        country = self.__parsed_args['country']
        if country not in possib_countries:
            raise ValueError(
                f'Selected country "{country}" not in the list of available countries: ' + 
                f'{", ".join(possib_countries)} are possible.'
            )
        
        possib_wallpapers = list(self.__config['countries'][country]['wallpapers'].keys())
        wallpaper = self.__parsed_args['wallpaper']
        if wallpaper not in possib_wallpapers:
            raise ValueError(f'Wallpaper "{wallpaper}" not available; available are: {", ".join(possib_wallpapers)}.')
        
        fonts = self.__parsed_args['fonts']
        possib_fonts = list(self.__config['fonts'].keys())
        if fonts is not None:
            for font in fonts:
                if font not in possib_fonts:
                    raise ValueError(f'Font "{font}" not available; available are: {", ".join(possib_fonts)}')


        latitudes = self.__parsed_args['latitudes']
        longitudes = self.__parsed_args['longitudes']
        coord_pins = zip(latitudes, longitudes) if latitudes is not None else []
        name_pins = self.__parsed_args['towns'] if self.__parsed_args['towns'] is not None else []
        print('name pins' + str(name_pins))
        self.__pins = []
        for pin in coord_pins + name_pins:
            try:
                self.__pins.append(Coordinates(pin))
            except ConnectionRefusedError as e:
                print(e) # Information about which town name could not be resolved.
    


    @property
    def pins(self) -> Union[List[Coordinates], None]:
        return self.__pins


    @property
    def wallpaper(self) -> Tuple[str, bool, Tuple[float, float, float, float]]:
        """Get the file path, whether a shape is need and the extent of the chosen wallpaper.

        Returns:
            Tuple[str, bool, Tuple[float, float, float, float]]: File path, need for shaping and the extent (west, east, south, north).
        """

        wallpaper_name = self.__parsed_args['wallpaper']
        chosen_country = self.__parsed_args['country']
        wallpaper_data = self.__config['countries'][chosen_country]['wallpapers'][wallpaper_name] 
        file_path = os.path.join('data', 'img', wallpaper_data['filename'])
        shaping_need = wallpaper_data['shaped']
        extent = wallpaper_data['extent']
        
        return file_path, shaping_need, extent 

    
    @property
    def main_text(self) -> Union[str, None]:
        return self.__parsed_args['body']


    @property
    def head_text(self) -> Union[str, None]:
        return self.__parsed_args['super']

    
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
