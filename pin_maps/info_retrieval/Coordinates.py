# Python libraries
import requests
import json
# Typing 
from typing import Tuple

class Coords:
    def __init__(self, query: str):
        pass
        # gets coords, saves them

    
    @property
    def lat(self):
        pass
        # get the latitude
    

    @property
    def lon(self):
        pass
        # get the longitude



# Python libraries
import requests # pylint: disable=import-error
import json

class ShapeReceiver:
    """Retrieves the shape of the region from Open Street Maps."""

    to_json = '&format=json'

    def __init__(self, region_name: str):
        self._region_name = region_name.lower()

        self._meta_info_link = f'https://nominatim.openstreetmap.org/search.php?q={self._region_name}&polygon_geojson=1'
 

    def get(self):
        r = requests.get(self._meta_info_link + self.to_json)
        try:
            geo_json = json.loads(r.content)[0]['geojson']
        except IndexError:
            raise Exception(f'The region {self._region_name} was not found.')

        return geo_json
