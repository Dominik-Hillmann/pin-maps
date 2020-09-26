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
    """Represents a pin on the map.
    
    Args:
        location (Union[str, Tuple[float, float]]): Location name or position as latitude and longitude.
        symbol_path (str): Path to the image used as a pin.
    """

    __pin_cache_path = os.path.join('data', 'img', 'pin-cache')
    __base_url = 'https://de.wikipedia.org/wiki/'

    def __init__(self, location: Union[str, Tuple[float, float]], symbol_path: str):
        self.__location = Coordinates(location)

        if symbol_path != 'heraldry':
            self.img = Image.open(symbol_path)
        else:
            try:
                self.img = self.__get_heraldry_cached(location.lower())
                print(f'Retrieving {location} from cache.')
            except LookupError:
                self.img = self.__get_heraldry_wiki(location)
                print(f'Retrieving {location} from Wikipedia.')
    

    @property
    def position(self) -> Tuple[float, float]:
        """The coordinates of the pin.

        Returns:
            Tuple[float, float]: The coordinates.
        """

        return self.__location.coords


    def __get_heraldry_wiki(self, location_name: str) -> Image.Image:
        """Retrieves the location's heraldry frim the Wikipedia.

        Args:
            location_name (str): The location's name.

        Raises:
            ConnectionRefusedError: Wikipedia cannot be contacted due to network errors.
            LookupError: The Wikipedia page does not contain a heraldry image.

        Returns:
            Image.Image: The heraldry image.
        """

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
            big_heraldry = 'groß' in img['src'].lower() or 'groß' in img['alt'].lower()
            if (heraldry_in_alt or heraldry_in_src) and (name_in_alt or name_in_src) and not big_heraldry:
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
        heraldry = self.__add_shadow(heraldry)
        heraldry.save(os.path.join(self.__pin_cache_path, location_name.lower() + '-pin.png')) # Caching

        return heraldry


    def __get_heraldry_cached(self, location_name: str) -> Image.Image:
        """Retrieves cached heraldry.

        Args:
            location_name (str): The location's name.

        Raises:
            LookupError: If the heraldry is not yet cached.

        Returns:
            Image.Image: The heraldry image.
        """

        cached_pins = os.listdir(self.__pin_cache_path)
        filename = f'{location_name.lower()}-pin.png'
        if filename not in cached_pins:
            raise LookupError(f'{location_name} is not yet cached.')
        
        return Image.open(os.path.join(self.__pin_cache_path, filename))

    
    @staticmethod
    def __flood_delete_background(heraldry: Image.Image, px_dist: int = 50) -> Image.Image:
        """Removes background of the heraldry if it is not transparent.

        Args:
            heraldry (Image.Image): The image from which background should be removed.
            px_dist (int, optional): Max. pixel distance in the flood fill algorithm. Defaults to 50.

        Returns:
            Image.Image: The image with transparent background.
        """
        
        heraldry = heraldry.convert('RGBA')
        new_val = (255, 255, 255, 0) # Last zero important: transparency.
        seed_right = (val - 1 for val in heraldry.size)
        ImageDraw.floodfill(heraldry, xy = seed_right, value = new_val, thresh = px_dist)

        _, height = heraldry.size
        seed_left = (0, height - 1)
        ImageDraw.floodfill(heraldry, xy = seed_left, value = new_val, thresh = px_dist)

        return heraldry

    
    @staticmethod
    def __add_shadow(heraldry: Image.Image, height_change: float = 1.1, ell_start: float = 0.9) -> Image.Image:
        """Adds a shadow below the heraldry.

        Args:
            heraldry (Image.Image): The image to which you want to add the shadow.
            height_change (float, optional): Percentage change to make space for the shadow. Defaults to 1.1.
            ell_start (float, optional): Upper start of shadow as percentage of the height of the input image. Defaults to 0.9.

        Returns:
            Image.Image: The image containing a shadow.
        """

        heraldry = heraldry.convert('RGBA')
        orig_width, orig_height = heraldry.size

        new_height = int(height_change * orig_height)
        ell_img = Image.new('RGBA', (orig_width, new_height))
        draw = ImageDraw.Draw(ell_img)

        top_left = (0, int(ell_start * orig_height))
        bot_right = (orig_width - 1, new_height - 1)
        draw.ellipse((*top_left, *bot_right), fill = (0, 0, 0, 100))
        ell_img.paste(heraldry, (0, 0), heraldry)

        return ell_img


    def __str__(self):
        return 'Pin(symbol=' + self.__symbol_path + ', loc=' + str(tuple(self.location)) + ')'

    
    def __iter__(self):
        for coord in self.location.coords:
            yield float(coord)