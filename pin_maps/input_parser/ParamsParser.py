# Python libraries
import argparse
import json
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
            '-h', '--header',
            required = True,
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
            '-f', '--fonts',
            nargs = 2,
            type = str,
            help = 'The name of the fonts. The first will be used for the header, ' + 
            'the second for the body.'
        )
        parser.add_argument(
            '-a', '--latitude',
            nargs = '+',
            type = float,
            help = 'A list of the latitudes of the pins. The lists of ' + 
            'latitudes and longitudes need to have the same length.'
        )
        parser.add_argument(
            '-o', '--longitude',
            nargs = '+',
            type = float,
            help = 'A list of the longitudes of the pins. The lists of ' + 
            'latitudes and longitudes need to have the same length.'
        )

        self.parsed_args = vars(parser.parse_args())
        # print(self.parsed_args)
        query_given = self.parsed_args['query'] is not None
        lat_given = self.parsed_args['latitude'] is not None
        lon_given = self.parsed_args['longitude']  is not None
        # print(query_given, lat_given, lon_given)

        if query_given and (lat_given or lon_given):
            raise TypeError('Please input EITHER a city name or coordinates, not both.') 

        if not query_given and not lat_given and not lon_given:
            raise TypeError('Please input coordinates or a location name.')

        if (lat_given and not lon_given) or (lon_given and not lat_given):
            raise TypeError('Please input both coordinates: --latitude or -a and --longitude or -o.')

        if query_given:
            self.parsed_args['mode'] = self.QUERY
        elif lat_given and lon_given:
            self.parsed_args['mode'] = self.COORDS
        else:
            raise TypeError('Unforeseen combination of console parameters.')


        # with open('config.yml') as config_file:
        #     config = yaml.load(config_file)
            
        # key = settings['key']
        # self.parsed_args['key'] = key

    @property
    def coords(self):
        return self.parsed_args['latitude'], self.parsed_args['longitude']
        
   
    @property
    def query(self) -> str:
        """The region or city that will be mapped.

        Returns:
            str: The query.
        """

        return self.parsed_args['query']


    @property
    def mode(self) -> str:
        """Wether the user used location strings or coordinates as input.

        Returns:
            str: The mode.
        """

        return self.parsed_args['mode']


    @property
    def key(self) -> str:
        """The key used to communicate with the Google Maps API.

        Returns:
            str: The key.
        """

        return self.parsed_args['key']
