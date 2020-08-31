# Python libraries
import json
# External modules
import argparse


class ParamsParser:
    """Class that makes it easy to retrieve parsed parameters."""

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-q', '--query',
            nargs = '+',
            type = str,
            help = 'The city or region of which you want to create a map.'
        )
        parser.add_argument(
            '-a', '--latitude',
            type = float,
            help = 'The latitude of the pin.'
        )
        parser.add_argument(
            '-o', '--longitude',
            type = float,
            help = 'The longitude of the pin.'
        )
        self.parsed_args = vars(parser.parse_args())
        
   
    @property
    def query(self) -> str:
        """The region or city that will be mapped.

        Returns:
            str: The query.
        """

        return self.parsed_args['query']
        

    @property
    def key(self) -> str:
        """The key used to communicate with the Google Maps API.

        Returns:
            str: The key.
        """

        return self.parsed_args['key']