# Python libraries
import requests
import os
import json
import csv
from time import sleep
# Typing 
from typing import Tuple, Union

class Coordinates:
    """Contains and resolves locations to coordinates.
    Args:
        location (Union[str, Tuple[float, float]]): The location's name or the tuple of coordinates.

    Raises:
        NameError: The location cannot be resolved to coordinates.
    """

    __base_query = 'https://nominatim.openstreetmap.org/search.php?q={}&format=json'
    __cache_path = os.path.join('data', 'coords-cache.csv')

    def __init__(self, location: str):
        self.name = location
        try:
            self.__latitude, self.__longitude = self.__resolve(location)
        except (ConnectionRefusedError, ValueError) as e:
            raise NameError(f'Location {location} could not be resolved.')
            

    
    def __resolve(self, query: str) -> Union[Tuple[float, float], None]:
        """Resolves the location name to coordinates using either the cache 
        or the nominatem API.

        Args:
            query (str): The location's name.

        Raises:
            ConnectionRefusedError: If there are problems contacting the nominatem API.
            ValueError: Connection to nominatem succesful but location does not exist.

        Returns:
            Tuple[float, float]: The coordinates.
        """

        # First, try to resolve via cache.
        coords = self.__search_cache(query.lower())
        if coords is not None:
            return coords

        # Otherwise, resolve via the internet.
        url = self.__base_query.format(query.lower())
        reply = requests.get(url)
        if reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact nominatem to resolve coordinates of "{query}".')
        
        try:
            result = json.loads(reply.content)[0]
        except IndexError:
            raise ValueError(f'No coordinates found for "{query}".')

        lat = float(result['lat'])
        lon = float(result['lon'])
        self.__write_cache(query.lower(), (lat, lon))
        sleep(1) # nominatem terms of service require this.
        return (lat, lon)


    @property
    def coords(self) -> Tuple[float, float]:
        """The coordinates of the location.

        Returns:
            Tuple[float, float]: The coordinates.
        """

        return (self.__latitude, self.__longitude)


    def __write_cache(self, location_name: str, coords: Tuple[float, float]) -> None:
        """Writes a location to cache.

        Args:
            location_name (str): The name of the location.
            coords (Tuple[float, float]): The coordinates of the location.
        """

        with open(self.__cache_path, 'a+', encoding = 'utf-8', newline = '') as cache_file:
            cache = csv.writer(cache_file, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
            cache.writerow([location_name, str(coords[0]), str(coords[1])])


    def __search_cache(self, location: str) -> Union[Tuple[float, float], None]:
        """Returns coordinates for the location name if it was searched before.

        Args:
            location (str): The name of the location of which you want the coordinates.

        Returns:
            Union[Tuple[float, float], None]: The coordinates or None, if the location is not cached yet.
        """

        with open(self.__cache_path, 'r', encoding = 'utf-8') as cache_file:
            location = location.lower()
            cache = csv.reader(cache_file, delimiter = ',')
            for line in cache:
                name = line[0]
                lat = float(line[1])
                lon = float(line[2])
                if name == location:
                    return lat, lon
            
        return None


    def __str__(self) -> str:
        return f'Coordinates(latitude={self.__latitude}, longitude={self.__longitude})'

    
    def __iter__(self) -> Tuple[float, float]:
        for coord in [self.__latitude, self.__longitude]:
            yield coord

    
    def __eq__(self, other: object) -> bool:
        if type(other) is not Coordinates:
            return False
        else:
            other_lat, other_lon = other.coords
            return other_lat == self.__latitude and other_lon == self.__longitude
