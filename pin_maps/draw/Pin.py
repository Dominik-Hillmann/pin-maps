# Python libraries
import requests
import os
import io
# External modules
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
# Internal modules
from input_parser.Coordinates import Coordinates
from draw.ImageTransform import ImageTransform
from draw.AddShadow import AddShadow
from draw.BackgroundDeletion import BackgroundDeletion
# Typing
from typing import Union, Tuple, List

class Pin:
    """Represents a pin on the map.
    
    Args:
        location (Union[str, Tuple[float, float]]): Location name or position as latitude and longitude.
        symbol_path (str): Path to the image used as a pin.
    """

    __pin_cache_path = os.path.join('data', 'img', 'pin-cache')
    __wiki_base_url = 'https://de.wikipedia.org/wiki/'
    __seach_url = 'https://de.wikipedia.org/w/index.php?search={}'

    def __init__(self, location: Union[str, Coordinates], symbol_path: str, transforms: List[ImageTransform]):
        self.__location = location if type(location) is Coordinates else Coordinates(location)
        self.__transforms = transforms

        if symbol_path != 'heraldry':
            self.img = Image.open(symbol_path)
        else:
            try:
                self.img = self.__get_heraldry_cached(self.__location.name.lower())
                print(f'Retrieving {self.__location.name} from cache.')
            except LookupError:
                self.img = self.__get_heraldry_wiki(self.__location.name.lower())
                print(f'Retrieving {self.__location.name} from Wikipedia.')
    

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

        wiki_url = self.__wiki_base_url + location_name.replace(' ', '_')
        reply = requests.get(wiki_url)
        if reply.status_code not in [200, 404]:
            raise ConnectionRefusedError(f'Status code {reply.status_code}: cannot contact {wiki_url}.') # 404 accepted because of wrong spelling possibilty.
        
        # TODO Refactor this part! Ugly!
        heraldry_url = self.__search_heraldry_link(reply.content, location_name.replace(' ', '_'))        
        if heraldry_url is None:
            search_url = self.__seach_url.format(location_name.replace(' ', '+'))
            search_reply = requests.get(search_url)
            if search_reply.status_code != 200:
                raise ConnectionRefusedError(f'Status code {search_reply.status_code}: cannot contact {search_url}.')
            
            heraldry_url = self.__search_heraldry_link(search_reply.content, location_name)
            if heraldry_url is None:
                city_url = self.__search_city_link(search_reply.content)
                attempt_2_reply = requests.get(city_url)
                if attempt_2_reply.status_code != 200:
                    raise ConnectionRefusedError(f'Status code {attempt_2_reply.status_code}: cannot contact {city_url} at attempt two.')

                heraldry_url = self.__search_heraldry_link(attempt_2_reply.content, location_name)
                print('Heraldry URL is', heraldry_url)
                if heraldry_url is None:
                    raise LookupError(f'Unable to find a heraldry image for {location_name}.')
        
        heraldry_url = 'http:' + heraldry_url        
        img_reply = requests.get(heraldry_url)
        if img_reply.status_code != 200:
            raise ConnectionRefusedError(f'Status code {img_reply.status_code}: cannot contact {heraldry_url}.')

        img_data = io.BytesIO(img_reply.content)
        heraldry = Image.open(img_data)
        # heraldry = self.__flood_delete_background(heraldry)
        # heraldry = self.__add_shadow(heraldry)
        for transform in self.__transforms:
            heraldry = transform(heraldry)
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
    def __search_heraldry_link(html: str, location_name: str) -> Union[str, None]:
        soup = BeautifulSoup(html, 'html.parser')
        
        heraldry_url = None
        imgs = soup.find_all('img')
        for img in imgs:
            heraldry_in_alt = 'wappen' in img['alt'].lower()
            heraldry_in_src = 'wappen' in img['src'].lower()
            # name_in_alt = location_name.lower() in img['alt'].lower()
            # name_in_src = location_name.lower() in img['src'].lower()
            if (heraldry_in_alt or heraldry_in_src):# and (name_in_alt or name_in_src):
                heraldry_url = img['src']
                break
        
        return heraldry_url


    @staticmethod
    def __search_city_link(html: str) -> Union[str, None]:
        soup = BeautifulSoup(html, 'html.parser')
        lis = soup.find_all('li')
        for li in lis:
            text = li.get_text().lower()
            if 'stadt ' in text or 'metropole ' in text or 'ort' in text:
                return 'https://de.wikipedia.org' + li.a['href']

        return None
        

    def __str__(self):
        return 'Pin(symbol=' + self.__symbol_path + ', loc=' + str(tuple(self.location)) + ')'

    
    def __iter__(self):
        for coord in self.location.coords:
            yield float(coord)
