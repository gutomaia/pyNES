# -*- coding: utf-8 -*-

import unittest

import pynes
from pynes.compiler import lexical, syntax, semantic
from pynes.cartridge import Cartridge
from pynes.asm import get_var

class MovingSpriteTest(unittest.TestCase):

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
                                exp += '%s%02x%s' % (FAIL, ord(expected[cursor]), ENDC)
                                act += '%s%02x%s' % (FAIL, ord(actual[cursor]), ENDC)
                            else:
                                exp += '%02x' % ord(expected[cursor])
                                act += '%02x' % ord(actual[cursor])
                    if ((a+1) % 2) == 0:
                        exp += ' '
                        act += ' '
                out += '%s- %d \n' % (exp, line + 1)
                out += '%s- %d \n' % (act, line + 1)
                a
            print out

    def test_asm_compiler(self):
        f = open ('fixtures/movingsprite/movingsprite.asm')
        code = f.read()
        f.close()
        tokens = lexical(code)
        ast = syntax(tokens)
        #self.assertEquals(61, len(ast))

        #.inesprg 1
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        self.assertEquals('T_DIRECTIVE', ast[0]['children'][0]['type'])
        self.assertEquals('.inesprg', ast[0]['children'][0]['value'])
        self.assertEquals(5, ast[0]['children'][0]['line']);
        self.assertEquals(3, ast[0]['children'][0]['column']);

        #.ineschr 1
        self.assertEquals('S_DIRECTIVE', ast[1]['type'])
        self.assertEquals('T_DIRECTIVE', ast[1]['children'][0]['type'])
        self.assertEquals('.ineschr', ast[1]['children'][0]['value'])
        self.assertEquals(6, ast[1]['children'][0]['line']);
        self.assertEquals(3, ast[1]['children'][0]['column']);

        #.inesmap 0
        self.assertEquals('S_DIRECTIVE', ast[2]['type'])
        self.assertEquals('T_DIRECTIVE', ast[2]['children'][0]['type'])
        self.assertEquals('.inesmap', ast[2]['children'][0]['value'])
        self.assertEquals(7, ast[2]['children'][0]['line']);
        self.assertEquals(3, ast[2]['children'][0]['column']);

        #.inesmir 1
        self.assertEquals('S_DIRECTIVE', ast[3]['type'])
        self.assertEquals('T_DIRECTIVE', ast[3]['children'][0]['type'])
        self.assertEquals('.inesmir', ast[3]['children'][0]['value'])
        self.assertEquals(8, ast[3]['children'][0]['line']);
        self.assertEquals(3, ast[3]['children'][0]['column']);

        #.bank 0
        self.assertEquals('S_DIRECTIVE', ast[4]['type'])
        self.assertEquals('T_DIRECTIVE', ast[4]['children'][0]['type'])
        self.assertEquals('.bank', ast[4]['children'][0]['value'])
        self.assertEquals(11, ast[4]['children'][0]['line']);
        self.assertEquals(3, ast[4]['children'][0]['column']);

        #.org $C000
        self.assertEquals('S_DIRECTIVE', ast[5]['type'])
        self.assertEquals('T_DIRECTIVE', ast[5]['children'][0]['type'])
        self.assertEquals('.org', ast[5]['children'][0]['value'])
        self.assertEquals(12, ast[5]['children'][0]['line']);
        self.assertEquals(3, ast[5]['children'][0]['column']);

        # WAITVBLANK: BIT $2002
        self.assertEquals('S_ABSOLUTE', ast[6]['type'])
        self.assertEquals(['WAITVBLANK'], ast[6]['labels'])
        self.assertEquals('T_INSTRUCTION', ast[6]['children'][0]['type'])
        self.assertEquals('BIT', ast[6]['children'][0]['value'])
        self.assertEquals(15, ast[6]['children'][0]['line']);
        self.assertEquals(3, ast[6]['children'][0]['column']);

        # BPL WAITVBLANK
        self.assertEquals('S_RELATIVE', ast[7]['type'])
        self.assertFalse('labels' in ast[7])
        self.assertEquals('T_INSTRUCTION', ast[7]['children'][0]['type'])
        self.assertEquals('BPL', ast[7]['children'][0]['value'])
        self.assertEquals(16, ast[7]['children'][0]['line']);
        self.assertEquals(3, ast[7]['children'][0]['column']);

        # RTS
        self.assertEquals('S_IMPLIED', ast[8]['type'])
        self.assertFalse('labels' in ast[8])
        self.assertEquals('T_INSTRUCTION', ast[8]['children'][0]['type'])
        self.assertEquals('RTS', ast[8]['children'][0]['value'])
        self.assertEquals(17, ast[8]['children'][0]['line']);
        self.assertEquals(3, ast[8]['children'][0]['column']);

        cart = Cartridge()
        cart.path = 'fixtures/movingsprite/'

        opcodes = semantic(ast, True, cart=cart)
        self.assertEquals(1, get_var('inesprg'))
        self.assertEquals(1, get_var('ineschr'))
        self.assertEquals(0, get_var('inesmap'))
        self.assertEquals(1, get_var('inesmir'))
        self.assertIsNotNone(opcodes)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        f = open('fixtures/movingsprite/movingsprite.nes', 'rb')
        content = f.read()
        f.close()
        self.assertHexEquals(content,bin)
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
