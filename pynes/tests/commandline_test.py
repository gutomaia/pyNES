# -*- coding: utf-8 -*-

import unittest

import os

from pynes import main
from mock import patch, Mock


import shutil

class CommandLineTest(unittest.TestCase):

    @patch('pynes.compiler.compile')
    def test_asm(self, compiler):
        main("pynes --asm fixtures/movingsprite/movingsprite.asm".split())
        self.assertTrue(compiler.called)

    def test_asm_c(self,):
        shutil.copyfile("fixtures/movingsprite/movingsprite.asm", "/tmp/movingsprite.asm")
        shutil.copyfile("fixtures/movingsprite/player.chr", "/tmp/player.chr")
        main("pynes --asm /tmp/movingsprite.asm".split())
        #self.assertTrue(os.path.exists('/tmp/movingsprite.nes'))
        #os.remove('/tmp/movingsprite.nes')

        #self.assertTrue(compiler.called)

    