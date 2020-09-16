# Python libraries
import os
# External modules
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
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
        
        shape_path = os.path.join('data', 'shapefiles', shapefile_name)
        shape = list(shpreader.Reader(shape_path).geometries())
        self.ax.add_geometries(shape, self.projection, edgecolor = 'white', facecolor = 'white', zorder = 10)

        background_path = os.path.join('data', 'img', background_name)
        background = plt.imread(background_path)
        background_extent = (5.5, 15.3, 47.0, 55.5) # (west, east, south, north)
        self.ax.imshow(background, origin = 'upper', extent = background_extent)


    def add_pin(self, file_name: str, coords: Tuple[float, float]) -> None:
        """Adds a pin to the map.

        Args:
            file_name (str): The file name of the pin that will be displayed.
            coords (Tuple[float, float]): The coordinates of where the pin will be placed.
        """

        pin_path = os.path.join('data', 'img', file_name)
        pin = plt.imread(pin_path)

        lat, lon = coords
        pin_extent = (lat, lat + 0.6, lon, lon + 0.5)
        self.ax.imshow(pin, origin = 'upper', extent = pin_extent, transform = self.projection, zorder = 11)


    def save(self, file_name: str) -> None:
        """Saves the file in the output directory.

        Args:
            file_name (str): The name the file will be given in the directory.
        """
        
        self.ax.set_aspect(self.aspect_ratio)
        plt.savefig(os.path.join('output', file_name))
