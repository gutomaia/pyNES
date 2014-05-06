# -*- coding: utf-8 -*-

import unittest

from pynes.compiler import lexical, syntax, semantic


class PlaTest(unittest.TestCase):

    def test_pla_sngl(self):
        tokens = list(lexical('PLA'))
        self.assertEquals(1, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_IMPLIED', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x68])
