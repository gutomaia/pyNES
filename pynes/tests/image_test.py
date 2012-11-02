# -*- coding: utf-8 -*-

import unittest
import os

from PIL import Image
from pynes import image, sprite

class ImageTest(unittest.TestCase):

    def setUp(self):
        self.mario1 = [
            [0,0,0,0,0,0,1,1],
            [0,0,0,0,1,1,1,1],
            [0,0,0,1,1,1,1,1],
            [0,0,0,1,1,1,1,1],
            [0,0,0,3,3,3,2,2],
            [0,0,3,2,2,3,2,2],
            [0,0,3,2,2,3,3,2],
            [0,3,3,2,2,3,3,2]
        ]

        self.mario2 = [
            [1,1,1,0,0,0,0,0],
            [1,1,2,0,0,0,0,0],
            [1,2,2,0,0,0,0,0],
            [1,1,1,1,1,1,0,0],
            [3,2,2,2,0,0,0,0],
            [3,3,2,2,2,2,0,0],
            [2,2,2,2,2,2,2,0],
            [2,2,3,2,2,2,2,0]
        ]

    def test_palette(self):
        palette = image.create_palette()
        self.assertEquals(64, len(palette))
        self.assertEquals((0x78, 0x80, 0x84), palette[0])
        self.assertEquals((0x00, 0x00, 0xfc), palette[1])
        self.assertEquals((0x00, 0x00, 0xc4), palette[2])

    def test_fetch_chr_0(self):
        img = Image.open('fixtures/mario.png')
        pixels = img.load()
        spr = image.fetch_chr(pixels, 0, 0)
        self.assertEquals(self.mario1, spr)

    def test_fetch_chr_1(self):
        img = Image.open('fixtures/mario.png')
        pixels = img.load()
        spr = image.fetch_chr(pixels, 1, 0)
        self.assertEquals(self.mario2, spr)

    def test_convert_chr(self):
        img = Image.open('fixtures/mario.png')
        sprs = image.convert_chr(img)
        self.assertIsNotNone(sprs)
        self.assertEquals(8192, len(sprs))
        self.assertEquals(self.mario1, sprite.get_sprite(0, sprs))
        self.assertEquals(self.mario2, sprite.get_sprite(1, sprs))

    def test_import_chr(self):
        try:
            os.remove('/tmp/mario.chr')
        except:
            pass
        self.assertFalse(os.path.exists('/tmp/mario.chr'))
        image.import_chr('fixtures/mario.png', '/tmp/mario.chr')
        self.assertTrue(os.path.exists('/tmp/mario.chr'))

        expected = open('fixtures/nesasm/scrolling/mario.chr', 'rb').read()
        actual = open('/tmp/mario.chr', 'rb').read()
        self.assertEquals(expected, actual)

        os.remove('/tmp/mario.chr')

    def test_export_chr(self):
        try:
            os.remove('/tmp/mario.png')
        except:
            pass
        self.assertFalse(os.path.exists('/tmp/mario.png'))
        image.export_chr('fixtures/nesasm/scrolling/mario.chr', '/tmp/mario.png')
        self.assertTrue(os.path.exists('/tmp/mario.png'))

        expected = open('fixtures/mario.png', 'rb').read()
        actual = open('/tmp/mario.png', 'rb').read()
        self.assertEquals(expected, actual)

        os.remove('/tmp/mario.png')

    def test_export_namespace(self):
        try:
            os.remove('/tmp/level.png')
        except:
            pass

        self.assertFalse(os.path.exists('/tmp/level.png'))
        image.export_nametable(
            'fixtures/nesasm/scrolling/SMBlevel.bin',
            'fixtures/nesasm/scrolling/mario.chr',
            '/tmp/level.png')
        self.assertTrue(os.path.exists('/tmp/level.png'))
        os.remove('/tmp/level.png')

    def assertHexEquals(self, expected, actual):
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        try:
            self.assertEquals(expected, actual)
        except:
            line = 0
            cursor = 0
            lines = []
            out = ''
            while (cursor < len(expected) or cursor < len(actual)):
                for a in range(16):
                    if cursor < len(expected) and cursor < len(actual):
                        if expected[cursor] != actual[cursor]:
                            lines.append(line)
                    cursor += 1
                line += 1
            exp = ''
            act = ''
            for line in lines:
                exp = 'Expected: %04x: ' % (line)
                act = 'Actual  : %04x: ' % (line)
                for a in range(16):
                    cursor = (line * 16)+ a
                    if cursor < len(expected) and cursor < len(actual):
                            if expected[cursor] != actual[cursor]:
                                exp += '%s%02x%s' % (OKGREEN, ord(expected[cursor]), ENDC)
                                act += '%s%02x%s' % (FAIL, ord(actual[cursor]), ENDC)
                            else:
                                exp += '%02x' % ord(expected[cursor])
                                act += '%02x' % ord(actual[cursor])
                    if ((a+1) % 2) == 0:
                        exp += ' '
                        act += ' '
                out += '%s- %d \n' % (exp, line + 1)
                out += '%s- %d \n' % (act, line + 1)
            print out

    def test_import_nametable(self):
        try:
            os.remove('/tmp/level.bin')
        except:
            pass

        self.assertFalse(os.path.exists('/tmp/level.bin'))
        
        image.import_nametable(
            'fixtures/level.png',
            'fixtures/nesasm/scrolling/mario.chr',
            '/tmp/level.bin')

        expected = open('fixtures/nesasm/scrolling/SMBlevel.bin', 'rb').read()
        actual = open('/tmp/level.bin', 'rb').read()
        size = len(actual)
        self.assertHexEquals(expected[:size], actual[:size])
        self.assertEquals(expected[:size], actual[:size])