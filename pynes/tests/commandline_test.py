# -*- coding: utf-8 -*-

import unittest

import os

from pynes import main
from mock import patch, Mock


import shutil

class CommandLineTest(unittest.TestCase):

    @patch('pynes.compiler.compile')
    def test_asm(self, compiler):
        main("pynes asm fixtures/movingsprite/movingsprite.asm".split())
        self.assertTrue(compiler.called)

    @patch('pynes.composer.compose')
    def test_py(self, composer):
        main("pynes py pynes/examples/movingsprite.py".split())
        self.assertTrue(composer.called)
