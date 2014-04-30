# -*- coding: utf-8 -*-

import unittest

from pynes import sprite


class SpriteTest(unittest.TestCase):

    def __init__(self, testcase_name):
        unittest.TestCase.__init__(self, testcase_name)
        f = open('fixtures/nerdynights/scrolling/mario.chr', 'rb')
        content = f.read()
        self.bin = [ord(c) for c in content]

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

        self.blank = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def test_load_sprites(self):
        sprites = sprite.load_sprites(
            'fixtures/nerdynights/scrolling/mario.chr')
        self.assertEquals(self.bin, sprites)

    def test_decode_first_sprite(self):
        channelA = self.bin[0:8]
        channelB = self.bin[8:16]
        s1 = sprite.decode_sprite(channelA, channelB)
        self.assertEquals(self.mario1, s1)

    def test_decode_second_sprite(self):
        channelA = self.bin[16:24]
        channelB = self.bin[24:32]

        s2 = sprite.decode_sprite(channelA, channelB)
        self.assertEquals(self.mario2, s2)

    def test_get_first_sprite(self):
        s1 = sprite.get_sprite(0, self.bin)
        self.assertEquals(self.mario1, s1)

    def test_get_second_sprite(self):
        s2 = sprite.get_sprite(1, self.bin)
        self.assertEquals(self.mario2, s2)

    def test_sprite_length(self):
        length = sprite.length(self.bin)
        self.assertEquals(512, length)

    def test_encode_first_sprite(self):
        encoded = sprite.encode_sprite(self.mario1)
        expected = self.bin[0:16]
        self.assertEquals(expected, encoded)

    def test_encode_second_sprite(self):
        encoded = sprite.encode_sprite(self.mario2)
        expected = self.bin[16:32]
        self.assertEquals(expected, encoded)

    def test_put_first_sprite(self):
        expected = [
            [0, 1, 2, 3, 0, 1, 2, 3],
            [1, 0, 1, 2, 3, 0, 1, 2],
            [2, 1, 0, 1, 2, 3, 0, 1],
            [3, 2, 1, 0, 1, 2, 3, 0],
            [0, 3, 2, 1, 0, 1, 2, 3],
            [1, 0, 3, 2, 1, 0, 1, 2],
            [2, 1, 0, 3, 2, 1, 0, 1],
            [3, 2, 1, 0, 3, 2, 1, 0]
        ]
        sprite.put_sprite(0, self.bin, expected)
        s1 = sprite.get_sprite(0, self.bin)
        self.assertEquals(expected, s1)

    def test_put_second_sprite(self):
        expected = [
            [0, 1, 2, 3, 0, 1, 2, 3],
            [1, 0, 1, 2, 3, 0, 1, 2],
            [2, 1, 0, 1, 2, 3, 0, 1],
            [3, 2, 1, 0, 1, 2, 3, 0],
            [0, 3, 2, 1, 0, 1, 2, 3],
            [1, 0, 3, 2, 1, 0, 1, 2],
            [2, 1, 0, 3, 2, 1, 0, 1],
            [3, 2, 1, 0, 3, 2, 1, 0]
        ]
        sprite.put_sprite(1, self.bin, expected)
        s1 = sprite.get_sprite(1, self.bin)
        self.assertEquals(expected, s1)

    def test_find_sprite_1(self):
        index = sprite.find_sprite(self.bin, self.mario1)
        self.assertEquals(0, index)

    def test_find_sprite_2(self):
        index = sprite.find_sprite(self.bin, self.mario2)
        self.assertEquals(1, index)

    def test_find_sprite_3(self):
        index = sprite.find_sprite(self.bin, self.blank, 256)
        self.assertEquals(292 - 256, index)
