# -*- coding: utf-8 -*-

from unittest import TestCase
from pynes.composer import compose, Game

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
            print self.testcase.asm
            raise(AssertionError('"%s" was not found in code' % text))
        return self

    def and_then(self, text):
        index = self.testcase.asm[self.start:].find(text)
        if index > 0:
            self.start += index + len(text)
            self.last = text
        else:
            print self.testcase.asm
            raise(AssertionError('"%s" was not found after "%s" in code' % (text, self.last)))
        return self

    def and_not_from_then(self, text):
        index = self.testcase.asm[self.start:].find(text)
        if index > 0:
            print self.testcase.asm
            raise(AssertionError('"%s" was found after "%s" in code' % (text, self.last)))
        return self


class ComposerTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

    def setUp(self):
        self.code = None
        self.game = None
        self.asm = None

    def tearDown(self):
        self.code = None
        self.game = None
        self.asm = None

    def assert_asm_from(self, code):
        self.code = code
        self.game = compose(code)
        self.asm = self.game.to_asm()
        return WhatElse(self)

class HexTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

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
                        if expected[cursor] != actual[cursor] and line not in lines:
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
            raise AssertionError('Hex are not equal')

class SpriteTestCase(TestCase):

    def __init__(self, testname):
        TestCase.__init__(self, testname)

    def get_printable_sprite(self, spr):
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
        print output

    def show_sprite(self, spr):
        ENDC = '\033[0m'
        return '\n'.join(self.get_printable_sprite(spr)) + ENDC

    def assertSpriteEquals(self, expected, actual):
        try:
            self.assertEquals(expected, actual)
        except:
            ENDC = '\033[0m'
            e = self.get_printable_sprite(expected)
            a = self.get_printable_sprite(actual)
            out = ''
            for i in range(8):
                if i == 4:
                    out += e[i] + ENDC + ' != ' + a[i] + ENDC + '\n'
                else:
                    out += e[i] + ENDC + '    ' + a[i] + ENDC + '\n'
            raise AssertionError('Sprites are not equal\n\n' + out)
