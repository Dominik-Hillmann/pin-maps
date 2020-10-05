#!/usr/bin/env python
"""Tests that confirm correctness of the parsing of the parsing of the console parameters."""

# Python libraries
import sys
import os
# External modules
import pytest
from PIL import ImageFont
# Internal modules
from input_parser.ParamsParser import ParamsParser
from input_parser.Coordinates import Coordinates

root = sys.argv[0]

### GENERAL TESTS ###
def test_on_missing_required_param():
    sys.argv = [root]
    with pytest.raises(SystemExit):
        params = ParamsParser()


### TOWN PARAMETERS ###

def test_town_names_parsing():
    sys.argv = [root, '-c', 'de', '-w', 'space', '-t', '"Wanzleben,  Bortfeld   ,  Berlin,Garmisch,Frankfurt am Main,Frankfurt Oder"']
    params = ParamsParser()

    correct_names = ['Wanzleben', 'Bortfeld', 'Berlin', 'Garmisch', 'Frankfurt am Main', 'Frankfurt Oder']
    correct_locations = [Coordinates(name) for name in correct_names]
    for parsed, correct in zip(params.locations, correct_locations):
        assert parsed == correct


def test_skip_on_nonexistent_town():
    sys.argv = [root, '-c', 'de', '-w', 'space', '-t', '"Wanzleben, Idonotexistatalltowm"']
    params = ParamsParser()

    correct_locations = [Coordinates('Wanzleben')]
    assert len(correct_locations) == len(params.locations)
    for parsed, correct in zip(params.locations, correct_locations):
        assert parsed == correct


def test_no_towns_allowed():
    sys.argv = [root, '-c', 'de', '-w', 'space']
    params = ParamsParser()

    assert type(params.locations) is list and len(params.locations) == 0


### COUNTRY PARAMETER ###

def test_error_on_nonexistent_country():
    sys.argv = [root, '-c', 'I should not be here', '-w', 'space']
    with pytest.raises(ValueError):
        ParamsParser()
        

### WALLPAPER PARAMETER ###

def test_error_on_nonexistent_wallpaper():
    sys.argv = [root, '-c', 'de', '-w', 'I should not be here']
    with pytest.raises(ValueError):
        params = ParamsParser()
        

### FONTS PARAMETER ###

def test_standard_fonts():
    sys.argv = [root, '-c', 'de', '-w', 'space']
    params = ParamsParser()

    assert os.path.isfile(params.head_font_path)
    assert os.path.isfile(params.main_font_path)
    
    ImageFont.truetype(params.head_font_path)
    ImageFont.truetype(params.main_font_path)
    

def test_fail_on_nonexistent_fonts():
    sys.argv = [root, '-c', 'de', '-w', 'space', '-f', 'testeins', 'testzwei']
    with pytest.raises(ValueError):
        ParamsParser()


def test_fail_on_wrong_font_input_format():
    sys.argv = [root, '-c', 'de', '-w', 'space', '-f', 'nureine']
    with pytest.raises(SystemExit):
        ParamsParser()

