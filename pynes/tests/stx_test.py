# -*- coding: utf-8 -*-

import unittest

from pynes.compiler import lexical, syntax, semantic


class StxTest(unittest.TestCase):

    def test_stx_zp(self):
        tokens = list(lexical('STX $00'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x86, 0x00])

    def test_stx_zpy(self):
        tokens = list(lexical('STX $10,Y'))
        self.assertEquals(4, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ZEROPAGE_Y', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x96, 0x10])

    def test_stx_abs(self):
        tokens = list(lexical('STX $1234'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x8e, 0x34, 0x12])
