#!/usr/bin/env python
"""Tests that confirm correctness of the parsing of the parsing of the console parameters."""

# Python libraries
import sys
# External modules
import pytest
# Internal modules
from input_parser.ParamsParser import ParamsParser
from input_parser.Coordinates import Coordinates

root = sys.argv[0]

### TOWN PARAMETERS ###

def test_town_names_parsing():
    sys.argv = [root, '-c', 'de', '-w', 'space', '-t', '"Wanzleben,  Bortfeld   ,  Berlin,Garmisch,Frankfurt am Main,Frankfurt Oder"']
    params = ParamsParser()

    correct_names = ['Wanzleben', 'Bortfeld', 'Berlin', 'Garmisch', 'Frankfurt am Main', 'Frankfurt Oder']
    correct_locations = [Coordinates(name) for name in correct_names]
    for parsed, correct in zip(params.locations, correct_locations):
        assert parsed == correct

    


### COUNTRY PARAMETER ###

def test_error_on_nonexistent_country():
    try:
        sys.argv = [root, '-c', 'I should not be here', '-w', 'space']
        params = ParamsParser()
        pytest.fail('Exception should be caused because of nonexistent country.')
    except ValueError:
        pass

### WALLPAPER PARAMETER ###

def test_error_on_nonexistent_wallpaper():
    try:
        sys.argv = [root, '-c', 'de', '-w', 'I should not be here']
        params = ParamsParser()
        pytest.fail('Exception should be caused because of nonexistent wallpaper.')
    except ValueError:
        pass