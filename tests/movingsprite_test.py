# -*- coding: utf-8 -*-

import unittest

import pynes
import pynes.opcodes
from pynes.compiler import lexical, syntax, semantic
from pynes.asm import get_var

class MovingSpriteTest(unittest.TestCase):


    def test_asm_compiler(self):
        f = open ('fixtures/movingsprite/movingsprite.asm')
        line = 91
        lines = f.read().split('\n')[0:line]
        code = '\n'.join(lines)
        f.close()
        tokens = lexical(code)
        ast = syntax(tokens)
        self.assertEquals(61, len(ast))

        #.inesprg 1
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        self.assertEquals('T_DIRECTIVE', ast[0]['directive']['type'])
        self.assertEquals('.inesprg', ast[0]['directive']['value'])

        #.ineschr 1
        self.assertEquals('S_DIRECTIVE', ast[1]['type'])
        self.assertEquals('T_DIRECTIVE', ast[1]['directive']['type'])
        self.assertEquals('.ineschr', ast[1]['directive']['value'])

        #.inesmap 0
        self.assertEquals('S_DIRECTIVE', ast[2]['type'])
        self.assertEquals('T_DIRECTIVE', ast[2]['directive']['type'])
        self.assertEquals('.inesmap', ast[2]['directive']['value'])

        #.inesmir 1
        self.assertEquals('S_DIRECTIVE', ast[3]['type'])
        self.assertEquals('T_DIRECTIVE', ast[3]['directive']['type'])
        self.assertEquals('.inesmir', ast[3]['directive']['value'])

        #.bank 0
        self.assertEquals('S_DIRECTIVE', ast[4]['type'])
        self.assertEquals('T_DIRECTIVE', ast[4]['directive']['type'])
        self.assertEquals('.bank', ast[4]['directive']['value'])

        #.org $C000
        self.assertEquals('S_DIRECTIVE', ast[5]['type'])
        self.assertEquals('T_DIRECTIVE', ast[5]['directive']['type'])
        self.assertEquals('.org', ast[5]['directive']['value'])

        # WAITVBLANK: BIT $2002
        self.assertEquals('S_ABSOLUTE', ast[6]['type'])
        self.assertEquals(['WAITVBLANK'], ast[6]['labels'])
        self.assertEquals('T_INSTRUCTION', ast[6]['instruction']['type'])
        self.assertEquals('BIT', ast[6]['instruction']['value'])

        # BPL WAITVBLANK
        self.assertEquals('S_RELATIVE', ast[7]['type'])
        self.assertFalse('labels' in ast[7])
        self.assertEquals('T_INSTRUCTION', ast[7]['instruction']['type'])
        self.assertEquals('BPL', ast[7]['instruction']['value'])

        # RTS
        self.assertEquals('S_IMPLIED', ast[8]['type'])
        self.assertFalse('labels' in ast[8])
        self.assertEquals('T_INSTRUCTION', ast[8]['instruction']['type'])
        #self.assertEquals('RTS', ast[8]['instruction']['value'])

        opcodes = semantic(ast, True)
        self.assertEquals(1, get_var('inesprg'))
        self.assertEquals(1, get_var('ineschr'))
        self.assertEquals(0, get_var('inesmap'))
        self.assertEquals(1, get_var('inesmir'))
        self.assertIsNotNone(opcodes)

        #self.assertTrue(False)
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
