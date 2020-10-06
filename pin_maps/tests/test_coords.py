# Python libraries
import os
import csv
# External modules
import pytest
# Internal modules
from input_parser.Coordinates import Coordinates

def add_to_cache(name: str, lat: float, lon: float) -> None:
    cache_file_name = os.path.join('data', 'coords-cache.csv')
    with open(cache_file_name, 'a+', encoding = 'utf-8', newline = '') as cache_file:
        cache_csv = csv.writer(cache_file)
        cache_csv.writerow([name, lat, lon])

def remove_from_cache(name: str) -> None:
    cache_file_name = os.path.join('data', 'coords-cache.csv')
    with (
        open(cache_file_name, 'rb', encoding = 'utf-8', newline = '') as cache_in,
        open(cache_file_name, 'a+', encoding = 'utf-8', newline = '') as cache_out
    ):
        cache_reader = csv.reader(cache_in)
        cache_writer = csv.writer(cache_out)
        for name, lat, lon in cache_reader:
            print(name)


def test_cache_resolve():
    name = 'testtown'
    lat, lon = 1.0, 1.0
    # add_to_cache('testtown', 1.0, 1.0)
    remove_from_cache(name)

@pytest.mark.skip
def test_nominatem_resolve():
    raise NotImplementedError()


def test_fail_on_nonexistent_town():
    with pytest.raises(NameError):
        Coordinates('IDoNotExistAtAllTown')

