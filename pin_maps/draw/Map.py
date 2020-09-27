# Python libraries
import os
# Internal modules
from draw.Pin import Pin
# External modules
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
# Typing
from typing import List, Tuple

class Map:
    """Represents the map on which one can draw.
    Args:
        shapefile_name (str): Name of the shapefile.
        background_name (str): Name of the background file.
        extent (List[float]): Extent of the map.
        aspect_ratio (float, optional): Aspect ratio of the map. Defaults to 1.49.
    """

    width = 2000
    height = 3000
    dpi = 96
    projection = ccrs.PlateCarree()

    def __init__(
        self,
        shapefile_name: str,
        background_name: str, 
        extent: List[float],
        aspect_ratio: float = 1.49
    ):
        self.aspect_ratio = aspect_ratio
        self.fig = plt.figure(figsize = (self.width / self.dpi, self.height / self.dpi), dpi = self.dpi, frameon = False)
        self.ax = plt.axes(projection = self.projection)
        self.ax.set_extent(extent, self.projection)
        
        # shape_path = os.path.join('data', 'shapefiles', shapefile_name)
        # shape = list(shpreader.Reader(shape_path).geometries())
        # self.ax.add_geometries(shape, self.projection, edgecolor = 'white', facecolor = 'white', zorder = 10)

        background_path = os.path.join('data', 'img', background_name)
        background = plt.imread(background_path)
        # background_extent = (5.5, 15.3, 47.0, 55.5) # (west, east, south, north)

        background_extent = (5.82, 15.12, 47.19, 55.31) # (west, east, south, north)

        self.ax.imshow(background, origin = 'upper', extent = background_extent)
        self.pins = []


    def add_pin(self, pin: Pin, lat_width: float = 0.6, shadow_factor: float = 1.35) -> None:
        # Wir wollen Pins mit gleicher Größe, aber originalem Verhältnis auf der Karte sehen.
        pin_img = pin.img
        width, height = pin_img.size
        print(pin_img.size)
        pin_arr = np.array(pin_img) / 255.0
        lon, lat = pin.position

        if lon < 49.9:
            lon -= 0.2
        elif lon > 53.5:
            lon += 0.1 

        lon_height = lat_width / width * (height / shadow_factor)
        lat_start = lat - 0.5 * lat_width
        lat_end = lat + 0.5 * lat_width
        extent = (lat_start, lat_end, lon, lon + lon_height)
        
        # Will be drawn in the save method because the list needs order by longitude first.
        self.pins.append({
            'img': pin_arr,
            'extent': extent,
            'lon': lon
        })

    
    def to_PIL(self) -> Image:
        """tbi"""

        raise NotImplementedError


    def save(self, file_name: str) -> None:
        """First, draws list of pins, then saves the file in the output directory.

        Args:
            file_name (str): The name the file will be given in the directory.
        """
        
        # Order pins by longitude, so no shadow is draw on top of other pin.
        self.pins.sort(key = lambda pin: pin['lon'])
        self.pins.reverse()
        for pin in self.pins:
            self.ax.imshow(pin['img'], origin = 'upper', extent = pin['extent'], transform = self.projection, zorder = 11)

        self.ax.set_aspect(self.aspect_ratio)
        plt.savefig(os.path.join('output', file_name))
