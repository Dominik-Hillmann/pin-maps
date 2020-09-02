# Python libraries
import requests
import json
# Typing 
from typing import Tuple

class Coordinates:
    def __init__(self, query: str = None, coords: Tuple[float, float] = None):
        if query is not None:
            self.latitude, self.longitude = self._resolve(query)
        elif coords is not None:
            self.latitude, self.longitude = coords
        else:
            raise Exception('Please provide either a location string or the coordinates.')
        # When coordinates are resolved or read, check if they are inside the Germany box (top, left, right, bottom.)
    
    def _resolve(self, location: str) -> Tuple[float, float]:
        pass
        # Contact nominatem API and resolve city name to coordinates if possible.


    @property
    def lat(self) -> float:
        return self.latitude 


    @property
    def lon(self) -> float:
        return self.longitude


    @property
    def coords(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)
