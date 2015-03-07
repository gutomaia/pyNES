# -*- coding: utf-8 -*-

from unittest import TestCase
from pynes.composer import compose
from pynes.compiler import compile
from pynes import sprite
import os

from pynes.compiler import lexical, syntax, semantic

class MetaInstructionCase(type):

    def __new__(cls, name, bases, args):
        def gen_lex():
            def test(self):
                tokens = list(lexical(self.asm))
                self.assertEquals(len(tokens), len(self.lex))
                for i,l in enumerate(self.lex):
                    self.assertEquals(l[0], tokens[i]['type'])
                    self.assertEquals(l[1], tokens[i]['value'])
            return test

        def gen_syn():
            def test(self):
                tokens = [
                    {'type': l[0], 'value': l[1]}
                    for l in self.lex
                ]

                ast = syntax(tokens)
                self.assertEquals(1, len(self.syn))
            return test

        def gen_sem():
            def test(self):
                tokens = [
                    {'type': l[0], 'value': l[1]}
                    for l in self.lex
                ]
                ast = [{'type': self.syn[0], 'children': tokens}]
                compiled = semantic(ast)
                self.assertEquals(compiled, self.code)
            return test

        args['test_lexical'] = gen_lex()
        args['test_syntax'] = gen_syn()
        args['test__semantic'] = gen_sem()

        return type.__new__(cls, name, bases, args)


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


class HexTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

    def assertHexEquals(self, expected, actual):
        OKGREEN = '\033[92m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        try:
            self.assertEquals(expected, actual)
        except AssertionError:
            line = 0
            cursor = 0
            lines = []
            out = ''
            while (cursor < len(expected) or cursor < len(actual)):
                for a in range(16):
                    if cursor < len(expected) and cursor < len(actual):
                        if expected[cursor] != actual[cursor] and line not in \
                                lines:
                            lines.append(line)
                    cursor += 1
                line += 1
            exp = ''
            act = ''
            for line in lines:
                exp = 'Expected: %04x: ' % (line)
                act = 'Actual  : %04x: ' % (line)
                for a in range(16):
                    cursor = (line * 16) + a
                    if cursor < len(expected) and cursor < len(actual):
                            if expected[cursor] != actual[cursor]:
                                exp += '%s%02x%s' % (
                                    OKGREEN, ord(expected[cursor]), ENDC)
                                act += '%s%02x%s' % (
                                    FAIL, ord(actual[cursor]), ENDC)
                            else:
                                exp += '%02x' % ord(expected[cursor])
                                act += '%02x' % ord(actual[cursor])
                    if ((a + 1) % 2) == 0:
                        exp += ' '
                        act += ' '
                out += '%s- %d \n' % (exp, line + 1)
                out += '%s- %d \n' % (act, line + 1)
            print(out)
            raise AssertionError('Hex are not equal')


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
