# Python libraries
import requests
import json
from time import sleep
# Typing 
from typing import Tuple, Union

class Coordinates:
    """Contains and automatically resolves locations to coordinates."""

    __base_query = 'https://nominatim.openstreetmap.org/search.php?q={}&format=json'

    def __init__(self, location: Union[str, Tuple[float, float]]):
        if type(location) is str:
            query, coords = location, None
        elif type(location) is tuple:
            query, coords = None, location
        else:
            raise Exception('Please provide either a location string or the coordinates as a tuple of floats.')

        if query is not None:
            self.__latitude, self.__longitude = self.__resolve(query)
        elif coords is not None:
            self.__latitude, self.__longitude = coords
        else:
            raise Exception('Please provide either a location string or the coordinates.')
        # When coordinates are resolved or read, check if they are inside the Germany box (top, left, right, bottom.)
    
    
    def __resolve(self, query: str) -> Tuple[float, float]:
        url = self.__base_query.format(query.lower())
        reply = requests.get(url)
        if reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact nominatem to resolve coordinates of "{query}".')
        
        try:
            result = json.loads(reply.content)[0]
        except IndexError:
            exit(f'ERROR: Could not find coordinates for a location named "{query}".')

        lat = result['lat']
        lon = result['lon']

        sleep(1) # nominatem terms of service require this.
        return (lat, lon)


    @property
    def lat(self) -> float:
        return self.__latitude 


    @property
    def lon(self) -> float:
        return self.__longitude


    @property
    def coords(self) -> Tuple[float, float]:
        return (self.__latitude, self.__longitude)


    def __str__(self):
        return f'(Latitude: {self.__latitude} | Longitude: {self.__longitude})'