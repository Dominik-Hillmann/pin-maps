# Python libraries
import argparse
import json
import sys
# Internal modules
from input_parser.Coordinates import Coordinates

# NOTE Needed information
# Country name => shapefile name
    # Rahmen Land
    # Rahmen Hintergrund
    # 
# Pin => Dateiname, Pin-Koordinaten
# Hintergrundname => Dateiname 
# Text1, Text2
# Font1, Font2

class ParamsParser:
    """Class that makes it easy to retrieve parsed parameters."""

    QUERY = 'query'
    COORDS = 'coordinates'

    def __init__(self):
        # Load configuration file.
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)


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

        self.parsed_args = vars(parser.parse_args())
        print(self.parsed_args)
        print()
        print(config)
        # Checks pin positions.
        if self.parsed_args['latitudes'] is not None and self.parsed_args['longitudes'] is not None:
            if len(self.parsed_args['latitudes']) != len(self.parsed_args['longitudes']):
                raise ValueError('Latitudes and longitudes need to have the same length.')
        
        # Checks available countries, wallpapers and fonts.
        possib_countries = [country['name'] for country in config['countries']]
        country = self.parsed_args['country']
        if country not in possib_countries:
            raise ValueError(f'Selected country "{country}" not in the list of available countries: {", ".join(possib_countries)}.')
        
        possib_wallpapers = list(config['wallpapers'].keys())
        wallpaper = self.parsed_args['wallpaper']
        if wallpaper not in possib_wallpapers:
            raise ValueError(f'Wallpaper "{wallpaper}" not available; available are: {", ".join(possib_wallpapers)}.')
        
        fonts = self.parsed_args['fonts']
        possib_fonts = list(config['fonts'].keys())
        if fonts is not None:
            for font in fonts:
                if font not in possib_fonts:
                    raise ValueError(f'Font "{font}" not available; available are: {", ".join(possib_fonts)}')


        # Converting parameters and setting defaults.
        # Wallpaper + extent
        # country + extent
        # fonts
        # pin positions and pin markers
        latitudes = self.parsed_args['latitudes']
        longitudes = self.parsed_args['longitudes']
        coord_pins = zip(latitudes, longitudes) if latitudes is not None else []
        name_pins = self.parsed_args['towns']
        self.__pins = []
        for pin in coord_pins + name_pins:
            try:
                self.__pins.append(Coordinates(pin))
            except ConnectionRefusedError as e:
                print(e) # Information about which town name could not be resolved.

        