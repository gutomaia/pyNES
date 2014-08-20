# -*- coding: utf-8 -*-
'''
LDX, Load Register X

This is one of the memory operations on the 6502
'''

import unittest

from pynes.compiler import lexical, syntax, semantic


class LdxTest(unittest.TestCase):

    def test_ldx_imm(self):
        tokens = list(lexical('LDX #$10'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xa2, 0x10])

    def test_ldx_imm_with_decimal(self):
        tokens = list(lexical('LDX #10'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xa2, 0x0a])

    def test_ldx_imm_with_binary(self):
        tokens = list(lexical('LDX #%00000100'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_BINARY_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xa2, 0x04])

    def test_ldx_zp(self):
        tokens = list(lexical('LDX $00'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xa6, 0x00])

    def test_ldx_zpy(self):
        tokens = list(lexical('LDX $10,Y'))
        self.assertEquals(4, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE_Y', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xb6, 0x10])

    def test_ldx_abs(self):
        tokens = list(lexical('LDX $1234'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xae, 0x34, 0x12])

    def test_ldx_absy(self):
        tokens = list(lexical('LDX $1234,Y'))
        self.assertEquals(4, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE_Y', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xbe, 0x34, 0x12])
