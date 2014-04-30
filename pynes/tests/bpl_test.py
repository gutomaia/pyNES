# -*- coding: utf-8 -*-

'''
BPL, Branch on Result Plus Test

This is a test for the branch instruction BPL of
the 6502. This instruction performs the branch
if N == 0.

'''

import unittest
from pynes.compiler import lexical, syntax, semantic


class BplTest(unittest.TestCase):

    '''This is an relative instruction, so it works quite different
    from others. The instruction uses an offset witch can range from
    -128 to +127. The offset is added to the program counter.'''

    def test_bpl_rel(self):
        tokens = lexical('BPL $10')
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_RELATIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x10, 0x0e])
