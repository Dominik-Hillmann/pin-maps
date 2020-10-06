# Python libraries
import os
import csv
# External modules
import pytest
# Internal modules
from input_parser.Coordinates import Coordinates

def add_to_cache(name: str, lat: float, lon: float) -> None:
    cache_file_name = os.path.join('data', 'coords-cache.csv')
    test_found = False
    with open(cache_file_name, 'r', encoding = 'utf-8', newline = '') as cache_in:
        cache_reader = csv.reader(cache_in)
        for read_name, read_lat, read_lon in cache_reader:
            print(read_name, read_name == name, read_lat, lat, read_lat == lat, read_lon, lon, read_lon == lon)
            if name == read_name and float(read_lat) == lat and float(read_lon) == lon:
                test_found = True
                break
    
    if not test_found:
        with open(cache_file_name, 'a+', encoding = 'utf-8', newline = '') as cache_file:
            cache_csv = csv.writer(cache_file)
            cache_csv.writerow([name, lat, lon])


def test_cache_resolve():
    name = 'testtown'
    lat, lon = 1.0, 1.0
    add_to_cache(name, lat, lon)

    coords = Coordinates(name)
    read_lat, read_lon = coords.coords
    assert read_lat == lat
    assert read_lon == lon


@pytest.mark.skip
def test_nominatem_resolve():
    raise NotImplementedError()


def test_fail_on_nonexistent_town():
    with pytest.raises(NameError):
        Coordinates('IDoNotExistAtAllTown')

