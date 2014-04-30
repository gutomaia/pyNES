# -*- coding: utf-8 -*-

import unittest

from pynes.compiler import lexical, syntax, semantic


class NopTest(unittest.TestCase):

    def test_nop_sngl(self):
        tokens = lexical('NOP')
        self.assertEquals(1, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMPLIED', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0xea])
