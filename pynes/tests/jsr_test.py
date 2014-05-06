# -*- coding: utf-8 -*-

import unittest

from pynes.compiler import lexical, syntax, semantic


class JsrTest(unittest.TestCase):

    def test_jsr_abs(self):
        tokens = list(lexical('JSR $1234'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x20, 0x34, 0x12])

# TODO: http://www.6502.buss.hk/6502-instruction-set/jmp says that there
# is a indirect
