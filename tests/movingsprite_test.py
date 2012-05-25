# -*- coding: utf-8 -*-

import unittest

import pynes
import pynes.opcodes
from pynes.compiler import lexical, syntax, semantic
from pynes.asm import get_var

class MovingSpriteTest(unittest.TestCase):


    def test_asm_compiler(self):
        f = open ('fixtures/movingsprite/movingsprite.asm')
        line = 15
        lines = f.read().split('\n')[0:line]
        code = '\n'.join(lines)
        f.close()
        tokens = lexical(code)
        ast = syntax(tokens)
        self.assertEquals(7, len(ast))
        opcodes = semantic(ast, True)
        self.assertEquals(1, get_var('inesprg'))
        self.assertEquals(1, get_var('ineschr'))
        self.assertEquals(0, get_var('inesmap'))
        self.assertEquals(1, get_var('inesmir'))
        self.assertIsNotNone(opcodes)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        f = open('fixtures/movingsprite/movingsprite.nes', 'rb')
        content = f.read(len(bin))
        f.close()
        self.assertEquals(content, bin)

    def test_fragment(self):
        fragment = '''
          LDA #$00
          STA $2003
          LDA #$02
          STA $4014
          '''
        tokens = lexical(fragment)
        ast = syntax(tokens)
        opcodes = semantic(ast)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        f = open('fixtures/nesasm/scrolling/scrolling5.nes', 'rb')
        content = f.read()
        f.close()
        self.assertTrue(bin in content)
