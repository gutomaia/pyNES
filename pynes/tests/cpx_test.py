# -*- coding: utf-8 -*-
'''
CPX, Compare with X Test
'''

import unittest

from pynes.compiler import lexical, syntax, semantic

class CpxTest(unittest.TestCase):

    def test_cpx_imm(self):
        tokens = list(lexical('CPX #$10'))
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xe0, 0x10])

    def test_cpx_imm_with_decimal(self):
        tokens = list(lexical('CPX #10'))
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xe0, 0x0a])

    def test_cpx_imm_with_binary(self):
        tokens = list(lexical('CPX #%00000100'))
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_BINARY_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xe0, 0x04])

    def test_cpx_zp(self):
        tokens = list(lexical('CPX $00'))
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xe4, 0x00])

    def test_cpx_abs(self):
        tokens = list(lexical('CPX $1234'))
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xec, 0x34, 0x12])
