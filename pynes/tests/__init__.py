# -*- coding: utf-8 -*-

from unittest import TestCase
from pynes.composer import compose
from nesasm.compiler import compile
from pynes import sprite
import os

from nesasm.compiler import lexical, syntax, semantic


class FileTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

    def assertFileExists(self, filename):
        try:
            self.assertTrue(os.path.exists(filename))
        except AssertionError:
            raise AssertionError('File %s should exist' % filename)

    def assertFileNotExists(self, filename):
        try:
            self.assertFalse(os.path.exists(filename))
        except AssertionError:
            raise AssertionError('File %s should not exist' % filename)


class WhatElse():

    def __init__(self, testcase):
        self.testcase = testcase
        self.start = 0
        self.last = None

    def has(self, text):
        index = self.testcase.asm.find(text)
        if index > 0:
            self.start = index + len(text)
            self.last = text
        else:
            print(self.testcase.asm)
            raise(AssertionError('"%s" was not found in code' % text))
        return self

    def and_then(self, text):
        index = self.testcase.asm[self.start:].find(text)
        if index > 0:
            self.start += index + len(text)
            self.last = text
        else:
            print(self.testcase.asm)
            raise(
                AssertionError('"%s" was not found after "%s" in code' %
                               (text, self.last)))
        return self

    def and_not_from_then(self, text):
        index = self.testcase.asm[self.start:].find(text)
        if index > 0:
            print(self.testcase.asm)
            raise(
                AssertionError('"%s" was found after "%s" in code' %
                               (text, self.last)))
        return self


class ComposerTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

    def setUp(self):
        self.code = None
        self.game = None
        self.asm = None
        self.path = ''

    def tearDown(self):
        self.code = None
        self.game = None
        self.asm = None
        self.path = ''

    def assert_asm_from(self, code):
        self.code = code
        self.game = compose(code)
        self.asm = self.game.to_asm()
        compile(self.asm, self.path)
        return WhatElse(self)

    def assert_asm_without_ines_from(self, code):
        self.code = code
        self.game = compose(code)
        self.asm = self.game.to_asm()
        compile(self.asm, self.path)
        return WhatElse(self)


def get_printable_sprite(spr):
    ALPHA = '\033[01;40m'
    R = '\033[01;41m'
    G = '\033[01;42m'
    B = '\033[01;44m'
    ENDC = '\033[0m'
    palette = [ALPHA, R, G, B]
    pixel = '  '
    lines = []
    previous = None
    for i in range(8):
        line = ''
        for j in range(8):
            color = spr[i][j]
            if previous != color:
                line += palette[color]
            line += pixel
        lines.append(line)
    return lines
    output = '\n'.join(lines) + ENDC
    print(output)


def show_sprite(spr):
    ENDC = '\033[0m'
    print('\n'.join(get_printable_sprite(spr)) + ENDC + '\n')


def show_sprites(sprs):
    ENDC = '\033[0m'
    length = sprite.length(sprs)
    tiles = []
    for i in range(length):
        spr = get_printable_sprite(sprite.get_sprite(i, sprs))
        tiles.append(spr)
        if len(tiles) % 8 == 0:
            out = ''
            for t in tiles:
                for l in t:
                    out += l + ENDC
                out += '\n'
            tiles = []
            print (out)


class SpriteTestCase(FileTestCase):

    def __init__(self, testname):
        FileTestCase.__init__(self, testname)

    def assertCHRFileEquals(self, expected, actual):
        expected_file = open(expected, 'rb')
        expected_bin = expected_file.read()
        expected_file.close()
        actual_file = open(actual, 'rb')
        actual_bin = actual_file.read()
        actual_file.close()
        try:
            self.assertEquals(expected_bin, actual_bin)
        except AssertionError:
            raise AssertionError('CHR files are not equals')

    def assertPNGFileEquals(self, expected, actual):
        expected_file = open(expected, 'rb')
        expected_bin = expected_file.read()
        expected_file.close()
        actual_file = open(actual, 'rb')
        actual_bin = actual_file.read()
        actual_file.close()
        try:
            self.assertEquals(expected_bin, actual_bin)
        except AssertionError:
            raise AssertionError('PNG files are not equals')

    def assertSpriteEquals(self, expected, actual):
        try:
            self.assertEquals(expected, actual)
        except:
            ENDC = '\033[0m'
            e = get_printable_sprite(expected)
            a = get_printable_sprite(actual)
            out = ''
            for i in range(8):
                if i == 4:
                    out += e[i] + ENDC + ' != ' + a[i] + ENDC + '\n'
                else:
                    out += e[i] + ENDC + '    ' + a[i] + ENDC + '\n'
            raise AssertionError('Sprites are not equal\n\n' + out)
