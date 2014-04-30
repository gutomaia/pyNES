# -*- coding: utf-8 -*-

import unittest

import pynes

from pynes.tests import HexTestCase
from pynes.compiler import lexical, syntax, semantic
from pynes.cartridge import Cartridge


class ScrollingTest(HexTestCase):

    def __init__(self, testname):
        HexTestCase.__init__(self, testname)

    def assertAsmResults(self, source_file, bin_file):
        path = 'fixtures/nerdynights/scrolling/'
        f = open(path + source_file)
        code = f.read()
        f.close()
        tokens = lexical(code)
        ast = syntax(tokens)

        cart = Cartridge()
        cart.path = 'fixtures/nerdynights/scrolling/'

        opcodes = semantic(ast, True, cart=cart)

        self.assertIsNotNone(opcodes)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        f = open(path + bin_file, 'rb')
        content = f.read()
        f.close()
        self.assertHexEquals(content, bin)

    def test_asm_compiler_scrolling_1(self):
        self.assertAsmResults('scrolling1.asm', 'scrolling1.nes')

    def test_asm_compiler_scrolling_2(self):
        self.assertAsmResults('scrolling2.asm', 'scrolling2.nes')

    def test_asm_compiler_scrolling_3(self):
        self.assertAsmResults('scrolling3.asm', 'scrolling3.nes')

    def test_asm_compiler_scrolling_4(self):
        self.assertAsmResults('scrolling4.asm', 'scrolling4.nes')
