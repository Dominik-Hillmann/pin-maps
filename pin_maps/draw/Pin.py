# Python librairies
import requests
import os
import io
# External modules
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
# Internal modules
from input_parser.Coordinates import Coordinates
# Typing
from typing import Union, Tuple

class Pin:
    """Represents a pin on the map."""

    __pin_cache_path = os.path.join('data', 'img', 'pin-cache')
    __base_url = 'https://de.wikipedia.org/wiki/'

    def __init__(self, location: Union[str, Tuple[float, float]], symbol_path: str):
        """Args:
            location (Union[str, Tuple[float, float]]): Location name or position as latitude and longitude.
            symbol_path (str): Path to the image used as a pin.
        """

        self.location = Coordinates(location)

        try:
            self.__get_heraldry_cached(location.lower())
            print('')
        except LookupError as e:
            print(e)
            self.__get_heraldry_wiki(location)
        
        if symbol_path == 'heraldry':
            pass
        else:
            pass

        self.__symbol_path = symbol_path


    def __get_heraldry_wiki(self, location_name: str) -> Image.Image:
        reply = requests.get(self.__base_url + location_name)
        if reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact {self.__base_url + location_name}.')
        
        soup = BeautifulSoup(reply.content, 'html.parser')
        
        heraldry_url = None
        imgs = soup.find_all('img')
        for img in imgs:
            heraldry_in_alt = 'wappen' in img['alt'].lower()
            heraldry_in_src = 'wappen' in img['src'].lower()
            name_in_alt = location_name.lower() in img['alt'].lower()
            name_in_src = location_name.lower() in img['src'].lower()
            if (heraldry_in_alt or heraldry_in_src) and (name_in_alt or name_in_src):
                heraldry_url = img['src']
                break
        
        if heraldry_url is None:
            raise LookupError(f'Unable to find a heraldry image in {self.__base_url + location_name}.')
        
        heraldry_url = 'http:' + heraldry_url        
        img_reply = requests.get(heraldry_url)
        if img_reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {img_reply.status_code}: cannot contact {heraldry_url}.')

        img_data = io.BytesIO(img_reply.content)
        heraldry = Image.open(img_data)
        heraldry = self.__flood_delete_background(heraldry)
        heraldry.save(os.path.join(self.__pin_cache_path, location_name.lower() + '-pin.png')) # Caching

        return heraldry


    def __get_heraldry_cached(self, location_name: str) -> Image.Image:
        
        cached_pins = os.listdir(self.__pin_cache_path)
        filename = f'{location_name.lower()}.png'
        if filename not in cached_pins:
            raise LookupError(f'{location_name} is not yet cached.')
        
        return Image.open(os.path.join(self.__pin_cache_path, filename))

    
    @staticmethod
    def __flood_delete_background(heraldry: Image.Image) -> Image.Image:
        
        heraldry.convert('RGBA')
        new_val = (255, 255, 255, 0) # Last zero important: transparency.
        seed_right = (val - 1 for val in heraldry.size)
        ImageDraw.floodfill(heraldry, xy = seed_right, value = new_val, thresh = 20)

        _, height = heraldry.size
        seed_left = (0, height - 1)
        ImageDraw.floodfill(heraldry, xy = seed_left, value = new_val, thresh = 20)

        return heraldry

    
    @staticmethod
    def __add_shadow(heraldry: Image.Image) -> Image.Image:
        pass


    def __str__(self):
        return 'Pin(symbol=' + self.__symbol_path + ', loc=' + str(tuple(self.location)) + ')'

    
    def __iter__(self):
        for coord in self.location.coords:
            yield float(coord)