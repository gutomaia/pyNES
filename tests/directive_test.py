# -*- coding: utf-8 -*-

import unittest
from pynes.compiler import lexical, syntax, semantic
from pynes.asm import get_var
from pynes.directives import get_pc


class DirectiveTest(unittest.TestCase):

    def test_label(self):
        tokens = lexical('label:')
        self.assertEquals(1 , len(tokens))
        self.assertEquals('T_LABEL', tokens[0]['type'])
        ast = syntax(tokens)
        #self.assertEquals(1 , len(ast))

    def test_inesprg(self):
        tokens = lexical('.inesprg 1')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_NUM', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        self.assertEquals(1, get_var('inesprg'))
        self.assertEquals(code[4], 1)

    def test_ineschr(self):
        tokens = lexical('.ineschr 1')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_NUM', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        self.assertEquals(1, get_var('ineschr'))
        self.assertEquals(code[5], 1)

    def test_inesmap(self):
        tokens = lexical('.inesmap 1')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_NUM', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        #self.assertEquals(1, get_var('inesmap'))
        self.assertEquals(code[6], 1)

    def test_inesmir(self):
        tokens = lexical('.inesmir 1')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_NUM', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        self.assertEquals(1, get_var('inesmir'))
        self.assertEquals(code[7], 1)

    def test_bank_0(self):
        tokens = lexical('.bank 0')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_NUM', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)

    def test_org_0000(self):
        tokens = lexical('.org $0000')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(0x0000, get_pc())

    def test_org_c000(self):
        tokens = lexical('.org $C000')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(0xc000, get_pc())

    def test_org_fffa(self):
        tokens = lexical('.org $FFFA')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(0xfffa, get_pc())
