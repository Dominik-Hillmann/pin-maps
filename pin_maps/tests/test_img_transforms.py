# Python libraries
import os
# External modules
from PIL import Image
import pytest
import numpy as np
# Internal modules
from draw.AddShadow import AddShadow
from draw.BackgroundDeletion import BackgroundDeletion
from draw.Ribbon import Ribbon

compare_imgs_path = os.path.join('data', 'img', 'test')

def test_shadow():
    shadow_transformer = AddShadow(height_change = 1.1, ell_start = 0.9, fill_col = (0, 0, 0, 100))
    empty_img = Image.new('RGBA', (100, 100), color = (0, 0, 0, 0))
    ell_img = shadow_transformer(empty_img)

    # Image was visually compared beforehand.
    comparison_img = Image.open(os.path.join(compare_imgs_path, 'shadow.png'))
    assert (np.array(ell_img) == np.array(comparison_img)).all()


def test_background_deletion():
    deletion = BackgroundDeletion(px_dist = 50, replace_val = (255, 255, 255, 0))
    white_img = Image.new('RGBA', (100, 100), color = (255, ) * 4)
    deleted_img = deletion(white_img)
    
    # Image was visually compared beforehand.
    comparison_img = Image.open(os.path.join(compare_imgs_path, 'empty.png'))
    assert (np.array(deleted_img) == np.array(comparison_img)).all()


def test_ribbon():
    ribbon = Ribbon('testname', ribbon_choice = 1)
    white_img = Image.new('RGBA', (100, 100), color = (255, ) * 4)
    ribbon_added = ribbon(white_img)
    # ribbon_added.save(os.path.join(compare_imgs_path, 'ribbon.png'))

    # Visually compared beforehand.
    comparison_img = Image.open(os.path.join(compare_imgs_path, 'ribbon.png'))
    assert (np.array(ribbon_added) == np.array(comparison_img)).all()

