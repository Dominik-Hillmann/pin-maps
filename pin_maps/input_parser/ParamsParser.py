# Python libraries
import json
# External modules
import argparse


class ParamsParser:
    """Class that makes it easy to retrieve parsed parameters."""

    QUERY = 'query'
    COORDS = 'coordinates'


    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-q', 
            '--query',
            nargs = '+',
            # required = True,
            type = str,
            help = 'The city or region of which you want to create a map.'
                )
        parser.add_argument(
            '-a',
            '--latitude',
            type = float
        )
        parser.add_argument(
            '-o',
            '--longitude',
            type = float
        )
        self.parsed_args = vars(parser.parse_args())
        print(self.parsed_args)
        query_given = self.parsed_args['query'] is not None
        lat_given = self.parsed_args['latitude'] is not None
        lon_given = self.parsed_args['longitude']  is not None
        print(query_given, lat_given, lon_given)

        if query_given and (lat_given or lon_given):
            raise Exception('Please input EITHER a city name or coordinates, not both.') 

        if not query_given and not lat_given and not lon_given:
            raise Exception('Please input coordinates or a location name.')

        if (lat_given and not lon_given) or (lon_given and not lat_given):
            raise Exception('Please input both coordinates: --latitude or -a and --longitude or -o.')

        if query_given:
            self.parsed_args['mode'] = self.QUERY
        elif lat_given and lon_given:
            self.parsed_args['mode'] = self.COORDS
        else:
            raise Exception('Unforeseen combination of console parameters.')


        with open('settings.json') as settings_file:
            settings = json.load(settings_file)
            
        key = settings['key']
        self.parsed_args['key'] = key
        
   
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
