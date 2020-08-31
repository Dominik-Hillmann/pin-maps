# Python libraries
import json
# External modules
import argparse


class ParamsParser:
    """Class that makes it easy to retrieve parsed parameters."""

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-q', 
            '--query',
            nargs = '+',
            required = True, 
            help = 'The city or region of which you want to create a map.'
        )
        self.parsed_args = vars(parser.parse_args())

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
    def key(self) -> str:
        """The key used to communicate with the Google Maps API.

        Returns:
            str: The key.
        """

        return self.parsed_args['key']