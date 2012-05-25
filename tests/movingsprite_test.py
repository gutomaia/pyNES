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
        #self.assertTrue(bin in content)

    def test_i_know_db(self):
        f = open('fixtures/movingsprite/movingsprite.nes', 'rb')
        bank1 = 0xfffa / 8
        mod = 0xfffa % 8
        org = (0xe000 & 0xf000) >> 12
        print hex(bank1 + mod + org + 1)
        f.seek(bank1 + mod + org + 1)
        a = f.read(32)
        for b in a:
            print hex(ord(b))
        print f.read(100)
        content = f.read()
        f.close()
        org = 0xe00
        print org
        print len(content)

        print content[org]

        #print hex(content[org])
        #print hex(content[org+1])

        #self.assertTrue(False)

    def test_i_know_db_2(self):
        f = open('fixtures/movingsprite/movingsprite.nes', 'rb')
        bank3 = 0xc000 / 8
        mod = 0xc000 % 8
        org = (0x0000 & 0xf000) >> 12
        org = 0
        print hex(bank3 + mod + org + 1)
        f.seek(bank3 + mod + org + 1)
        a = f.read(32)
        for b in a:
            print hex(ord(b))
        print f.read(100)
        content = f.read()
        f.close()
        org = 0xe00
        print org
        print len(content)

        print content[org]

        #print hex(content[org])
        #print hex(content[org+1])

        #self.assertTrue(False)

