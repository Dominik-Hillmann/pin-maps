# Python libraries
import requests
import json
# Typing 
from typing import Tuple

class Coordinates:

    __base_query = 'https://nominatim.openstreetmap.org/search.php?q={}&format=json'

    def __init__(self, query: str = None, coords: Tuple[float, float] = None):
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
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact nominatem.')
        
        try:
            result = json.loads(reply.content)[0]
        except IndexError:
            exit(f'ERROR: Could not find coordinates for a location named "{query}".')

        lat = result['lat']
        lon = result['lon']
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
