# -*- coding: utf-8 -*-
import os

from PIL import Image
from pynes import image, sprite
from pynes.tests import SpriteTestCase


class ImageTest(SpriteTestCase):

    def __init__(self, testname):
        SpriteTestCase.__init__(self, testname)

    def setUp(self):
        self.mario1 = [
            [0, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 3, 3, 3, 2, 2],
            [0, 0, 3, 2, 2, 3, 2, 2],
            [0, 0, 3, 2, 2, 3, 3, 2],
            [0, 3, 3, 2, 2, 3, 3, 2]
        ]

        self.mario2 = [
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 2, 0, 0, 0, 0, 0],
            [1, 2, 2, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0],
            [3, 2, 2, 2, 0, 0, 0, 0],
            [3, 3, 2, 2, 2, 2, 0, 0],
            [2, 2, 2, 2, 2, 2, 2, 0],
            [2, 2, 3, 2, 2, 2, 2, 0]
        ]

    def test_palette(self):
        palette = image.create_palette()
        self.assertEquals(64, len(palette))
        self.assertEquals((0x78, 0x80, 0x84), palette[0])
        self.assertEquals((0x00, 0x00, 0xfc), palette[1])
        self.assertEquals((0x00, 0x00, 0xc4), palette[2])

    '''Test if a portion of a image when fetched is equal
    to the same sprite'''

    def test_fetch_chr_0(self):
        pixels = Image.open('fixtures/mario.png').load()
        spr = image.fetch_chr(pixels, 0, 0)
        self.assertSpriteEquals(self.mario1, spr)

    '''Test if a portion of a image when fetched is equal
    to the same sprite'''

    def test_fetch_chr_1(self):
        pixels = Image.open('fixtures/mario.png').load()
        spr = image.fetch_chr(pixels, 1, 0)
        self.assertSpriteEquals(self.mario2, spr)

    '''Test the acquisition of a image file into a CHR'''

    def test_acquire_chr(self):
        img = Image.open('fixtures/mario.png')
        sprs, indexes = image.acquire_chr(img)
        self.assertEquals(8192, len(sprs))
        self.assertSpriteEquals(self.mario1, sprite.get_sprite(0, sprs))

    def test_import_chr(self):
        try:
            os.remove('/tmp/mario.chr')
        except:
            pass
        self.assertFileNotExists('/tmp/mario.chr')
        image.import_chr('fixtures/mario.png', '/tmp/mario.chr')
        self.assertFileExists('/tmp/mario.chr')
        self.assertCHRFileEquals(
            'fixtures/nerdynights/scrolling/mario.chr',
            '/tmp/mario.chr')
        os.remove('/tmp/mario.chr')

    def test_export_chr(self):
        try:
            os.remove('/tmp/mario.png')
        except:
            pass
        self.assertFileNotExists('/tmp/mario.png')
        image.export_chr(
            'fixtures/nerdynights/scrolling/mario.chr', '/tmp/mario.png')
        self.assertFileExists('/tmp/mario.png')
        self.assertPNGFileEquals('fixtures/mario.png', '/tmp/mario.png')

        img = Image.open('/tmp/mario.png')
        sprs, indexes = image.acquire_chr(img)
        self.assertIsNotNone(sprs)
        self.assertEquals(8192, len(sprs))
        self.assertSpriteEquals(self.mario1, sprite.get_sprite(0, sprs))
        self.assertSpriteEquals(self.mario2, sprite.get_sprite(1, sprs))

        os.remove('/tmp/mario.png')

    def test_export_namespace(self):
        try:
            os.remove('/tmp/level.png')
        except:
            pass

        self.assertFileNotExists('/tmp/level.png')
        image.export_nametable(
            'fixtures/nerdynights/scrolling/SMBlevel.bin',
            'fixtures/nerdynights/scrolling/mario.chr',
            '/tmp/level.png')
        self.assertFileExists('/tmp/level.png')

        img = Image.open('/tmp/level.png')
        sprs, indexes = image.acquire_chr(img, optimize_repeated=False)
        sprite.length(sprs)
        self.assertEquals(1024, sprite.length(sprs))
        return  # TODO why?!
        nt_file = open('fixtures/nerdynights/scrolling/SMBlevel.bin')
        nt = nt_file.read()
        nt_file.close()
        nts = [ord(n) for n in nt]
        mario = sprite.load_sprites('fixtures/nerdynights/scrolling/mario.chr')
        for i in range(32):
            for j in range(32):
                self.assertSpriteEquals(
                    sprite.get_sprite(nts[i * j] + 256, mario),
                    sprite.get_sprite(i * j, sprs)
                )
        os.remove('/tmp/level.png')

    def test_import_nametable(self):
        try:
            os.remove('/tmp/level.bin')
        except:
            pass

        self.assertFalse(os.path.exists('/tmp/level.bin'))

        image.import_nametable(
            'fixtures/level.png',
            'fixtures/nerdynights/scrolling/mario.chr',
            '/tmp/level.bin')

        expected = open(
            'fixtures/nerdynights/scrolling/SMBlevel.bin', 'rb').read()
        actual = open('/tmp/level.bin', 'rb').read()
        size = len(actual)
        self.assertEquals(expected[:size], actual[:size])
        # todo import entire namespace

    def test_read_nametable(self):
        # level = Image.open('fixtures/level.png')
        sprs = sprite.load_sprites('fixtures/nerdynights/scrolling/mario.chr')
        # nt = image.read_nametable(level, sprs)
        return
        expected = open(
            'fixtures/nerdynights/scrolling/SMBlevel.bin', 'rb').read()
        actual = open('/tmp/level.bin', 'rb').read()
        size = len(actual)
        self.assertEquals(expected[:size], actual[:size])
        return
        # sprs = image.convert_chr(img)
        self.assertEquals(8192, len(sprs))
        self.assertEquals(self.mario1, sprite.get_sprite(0, sprs))
        self.assertEquals(self.mario2, sprite.get_sprite(1, sprs))

    def test_acquire_pythonbrasil8(self):
        (nt, sprs) = image.acquire_nametable('fixtures/pythonbrasil8.png')
        # debug
        image.export_chr(sprs, '/tmp/pythonbrasil8_sprite.png')
        # debug
        image.export_nametable(nt, sprs, '/tmp/pythonbrasil8_nametable.png')
        from pynes import write_bin_code
        write_bin_code(nt, '/tmp/pythonbrasil8.bin')
        write_bin_code(sprs[0], '/tmp/pythonbrasil8.chr')

    def test_convert_to_nametable(self):
        return
        (nt, sprs) = image.convert_to_nametable('fixtures/level.png')
        # self.assertEquals(sprite.length(sprs), 15)

    def test_convert_to_nametable_pythonbrasil(self):
        return
        (nt, sprs) = image.convert_to_nametable('fixtures/pythonbrasil8.png')

    def test_convert_to_nametable_pythonbrasil2(self):
        return
        nt, sprs = image.convert_to_nametable('fixtures/pythonbrasil8.png')
        image.export_chr('sprite.chr', 'pythonbrasil8.png')
        image.export_nametable(
            'nametable.bin', 'sprite.chr', 'pythonbrasil8.png')
        import os
        os.rename('nametable.bin', 'pythonbrasil8.bin')
        image.export_nametable(
            'fixtures/nerdynights/scrolling/garoa.bin',
            'fixtures/nerdynights/scrolling/sprite.chr',
            'garoa.png')
