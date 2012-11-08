# -*- coding: utf-8 -*-

import unittest

from pynes.composer import pynes_compiler

class ComposerMovingSpriteTest(unittest.TestCase):

    def test_moving_sprite(self):
        f = open('pynes/examples/movingsprite.py')
        code = f.read()
        f.close()
        cart = pynes_compiler(code)
        asm = cart.to_asm()
