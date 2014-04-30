# -*- coding: utf-8 -*-
'''
CLC, Clear Carry

This is a test for the clear carry instruction
'''
import unittest
from pynes.compiler import lexical, syntax, semantic


class ClcTest(unittest.TestCase):


    def test_clc_sngl(self):
        tokens = list(lexical('CLC'))
        self.assertEquals(1 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMPLIED', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x18])
