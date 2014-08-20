# -*- coding: utf-8 -*-
'''
ROR, Rotate Right Test

This is an Bit Manipulation of the 6502.

'''

import unittest

from pynes.compiler import lexical, syntax, semantic


class RorTest(unittest.TestCase):

    def test_ror_imm(self):
        tokens = list(lexical('ROR #$10'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x6a, 0x10])

    def test_ror_imm_with_decimal(self):
        tokens = list(lexical('ROR #10'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x6a, 0x0a])

    def test_ror_imm_with_binary(self):
        tokens = list(lexical('ROR #%00000100'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_BINARY_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x6a, 0x04])

    def test_ror_zp(self):
        tokens = list(lexical('ROR $00'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x66, 0x00])

    def test_ror_zpx(self):
        tokens = list(lexical('ROR $10,X'))
        self.assertEquals(4, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE_X', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x76, 0x10])

    def test_ror_abs(self):
        tokens = list(lexical('ROR $1234'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x6e, 0x34, 0x12])

    def test_ror_absx(self):
        tokens = list(lexical('ROR $1234,X'))
        self.assertEquals(4, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE_X', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x7e, 0x34, 0x12])
