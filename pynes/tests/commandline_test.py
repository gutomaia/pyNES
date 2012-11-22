# -*- coding: utf-8 -*-

import os

from pynes import main
from pynes.tests import FileTestCase
from mock import patch, Mock

import shutil

class CommandLineTest(FileTestCase):

    @patch('pynes.compiler.compile')
    def test_asm(self, compiler):
        main("pynes asm fixtures/movingsprite/movingsprite.asm".split())
        self.assertTrue(compiler.called)

    @patch('pynes.composer.compose_file')
    def test_py(self, composer):
        main("pynes py pynes/examples/movingsprite.py".split())
        composer.assert_called_once_with(
            'pynes/examples/movingsprite.py',
            output=None, asm=False, path=None)

    @patch('pynes.composer.compose_file')
    def test_py_with_asm(self, composer):
        main("pynes py pynes/examples/movingsprite.py --asm".split())
        composer.assert_called_once_with(
            'pynes/examples/movingsprite.py',
            output=None, asm=True, path=None)

    @patch('pynes.composer.compose_file')
    def test_py_with_output(self, composer):
        main("pynes py pynes/examples/movingsprite.py --output output.nes".split())
        composer.assert_called_once_with(
            'pynes/examples/movingsprite.py',
            output='output.nes', asm=False, path=None)

    @patch('pynes.composer.compose_file')
    def test_py_with_path(self, composer):
        main("pynes py pynes/examples/movingsprite.py --path fixtures/movingsprite".split())
        composer.assert_called_once_with(
            'pynes/examples/movingsprite.py',
            output=None, path='fixtures/movingsprite', asm=False)

    def test_py_real_build_movingsprite(self):
        args = (
            "pynes py pynes/examples/movingsprite.py "
            "--path fixtures/movingsprite "
            "--output pynes/examples/movingsprite.nes"
            ).split()
        main(args)

    def test_py_real_build_mario(self):
        args = (
            "pynes py pynes/examples/mario.py "
            "--path fixtures/nesasm/scrolling "
            "--output pynes/examples/mario.nes"
            ).split()
        main(args)

    def test_py_real_build_helloworld(self):
        args = (
            "pynes py pynes/examples/helloworld.py "
            "--path fixtures/nesasm/scrolling "
            "--output pynes/examples/helloworld.nes"
            ).split()
        main(args)

