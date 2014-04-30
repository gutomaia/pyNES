# -*- coding: utf-8 -*-
from pynes import main
from pynes.tests import FileTestCase
from mock import patch


class CommandLineTest(FileTestCase):

    @patch('pynes.compiler.compile_file')
    def test_asm(self, compiler):
        main("pynes asm fixtures/movingsprite/movingsprite.asm".split())
        compiler.assert_called_once_with(
            'fixtures/movingsprite/movingsprite.asm',
            output=None, path=None)

    @patch('pynes.compiler.compile_file')
    def test_asm_with_output(self, compiler):
        main("pynes asm fixtures/movingsprite/movingsprite.asm --output"
             " /tmp/movingsprite.nes".split())
        compiler.assert_called_once_with(
            'fixtures/movingsprite/movingsprite.asm',
            output='/tmp/movingsprite.nes', path=None)

    @patch('pynes.compiler.compile_file')
    def test_asm_with_path(self, compiler):
        main("pynes asm fixtures/movingsprite/movingsprite.asm --path "
             "fixtures/movingsprite".split())
        compiler.assert_called_once_with(
            'fixtures/movingsprite/movingsprite.asm',
            output=None, path='fixtures/movingsprite')

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
        main("pynes py pynes/examples/movingsprite.py --output "
             "output.nes".split())
        composer.assert_called_once_with(
            'pynes/examples/movingsprite.py',
            output='output.nes', asm=False, path=None)

    @patch('pynes.composer.compose_file')
    def test_py_with_path(self, composer):
        main("pynes py pynes/examples/movingsprite.py --path "
             "fixtures/movingsprite".split())
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
            "--path fixtures/nerdynights/scrolling "
            "--output pynes/examples/mario.nes"
        ).split()
        main(args)

    def test_py_real_build_helloworld(self):
        args = (
            "pynes py pynes/examples/helloworld.py "
            "--path fixtures/nerdynights/scrolling "
            "--output pynes/examples/helloworld.nes"
        ).split()
        main(args)

    def test_py_real_build_slides(self):
        args = (
            "pynes py pynes/examples/slides.py "
            "--path fixtures/nerdynights/scrolling "
            "--output pynes/examples/slides.nes --asm"
        ).split()
        main(args)
