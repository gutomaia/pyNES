# -*- coding: utf-8 -*-

import unittest

from pynes.compiler import lexical, syntax, semantic
class LsrTest(unittest.TestCase):

    def test_lsr_imm(self):
        tokens = lexical('LSR #10')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x4a, 0x10])

    def test_lsr_zp(self):
        tokens = lexical('LSR $00')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x46, 0x00])

    def test_sta_zpx(self):
        tokens = lexical('LSR $10,X')
        self.assertEquals(4 , len(tokens))
        token = tokens[0]
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ZEROPAGE_X', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x56, 0x10])

    def test_sta_abs(self):
        tokens = lexical('LSR $1234')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x4e, 0x34, 0x12])


    def test_sta_absx(self):
        tokens = lexical('LSR $1234,X')
        self.assertEquals(4 , len(tokens))
        token = tokens[0]
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ABSOLUTE_X', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x5e, 0x34, 0x12])