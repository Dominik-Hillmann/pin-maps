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
        """
        Args:
            location (Union[str, Tuple[float, float]]): The location's name or the tuple of coordinates.

        Raises:
            ValueError: If the location parameter does not conform to the expected format as described above.
        """

        if type(location) is str:
            query, coords = location, None
        elif type(location) is tuple:
            query, coords = None, location
        else:
            raise ValueError('Please provide either a location string or the coordinates as a tuple of floats.')

        if query is not None:
            self.__latitude, self.__longitude = self.__resolve(query)
        elif coords is not None:
            self.__latitude, self.__longitude = coords
        else:
            raise ValueError('Please provide either a location string or the coordinates.')
        # When coordinates are resolved or read, check if they are inside the Germany box (top, left, right, bottom.)
    
    
    def __resolve(self, query: str) -> Tuple[float, float]:
        """Resolves the location name to coordinates.

        Args:
            query (str): The location's name.

        Raises:
            ConnectionRefusedError: If there are problems contacting the nominatem API.

        Returns:
            Tuple[float, float]: The coordinates.
        """

        url = self.__base_query.format(query.lower())
        reply = requests.get(url)
        if reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact nominatem to resolve coordinates of "{query}".')
        
        try:
            result = json.loads(reply.content)[0]
        except IndexError:
            exit(f'ERROR: Could not find coordinates for a location named "{query}".')

        lat = float(result['lat'])
        lon = float(result['lon'])

        sleep(1) # nominatem terms of service require this.
        return (lat, lon)


    @property
    def coords(self) -> Tuple[float, float]:
        """The coordinates of the location.

        Returns:
            Tuple[float, float]: The coordinates.
        """

        return (self.__latitude, self.__longitude)


    def __str__(self):
        return f'Coordinates(latitude={self.__latitude}, longitude={self.__longitude})'

    
    def __iter__(self):
        for coord in [self.__latitude, self.__longitude]:
            yield coord
