# -*- coding: utf-8 -*-

import unittest
from pynes.compiler import lexical, syntax, semantic

# TODO: from pynes.asm import get_var


class DirectiveTest(unittest.TestCase):

    def test_label(self):
        tokens = list(lexical('label:'))
        self.assertEquals(1, len(tokens))
        self.assertEquals('T_LABEL', tokens[0]['type'])
        # ast = syntax(tokens)
        # self.assertEquals(1 , len(ast))

    def test_inesprg(self):
        tokens = list(lexical('.inesprg 1'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_ARGUMENT', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        # self.assertEquals(1, get_var('inesprg'))
        self.assertEquals(code[4], 1)

    def test_ineschr(self):
        tokens = list(lexical('.ineschr 1'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_ARGUMENT', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        # self.assertEquals(1, get_var('ineschr'))
        self.assertEquals(code[5], 1)

    def test_inesmap(self):
        tokens = list(lexical('.inesmap 1'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_ARGUMENT', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        # self.assertEquals(1, get_var('inesmap'))
        self.assertEquals(code[6], 1)

    def test_inesmir(self):
        tokens = list(lexical('.inesmir 1'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_ARGUMENT', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast, True)
        # self.assertEquals(1, get_var('inesmir'))
        self.assertEquals(code[7], 1)

    def test_bank_0(self):
        tokens = list(lexical('.bank 0'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_DECIMAL_ARGUMENT', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        # code = semantic(ast)

    def test_org_0000(self):
        tokens = list(lexical('.org $0000'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        # code = semantic(ast)
        # self.assertEquals(0x0000, get_pc())

    def test_org_c000(self):
        tokens = list(lexical('.org $C000'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        # code = semantic(ast)
        # self.assertEquals(0xc000, get_pc())

    def test_org_fffa(self):
        tokens = list(lexical('.org $FFFA'))
        self.assertEquals(2, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        # code = semantic(ast)
        # self.assertEquals(0xfffa, get_pc())

    def test_db_1(self):
        code = ('.db $0F,$01,$02,$03,$04,$05,$06,$07,' # One-liner string
                    '$08,$09,$0A,$0B,$0C,$0D,$0E,$0F')
        tokens = list(lexical(code))
        self.assertEquals(32, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        # self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertIsNotNone(code)
        expected = [
            0x0f, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
            0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
        ]
        self.assertEquals(expected, code)

    def test_db_2(self):
        code = ('.db $0F,$30,$31,$32,$33,$35,$36,$37,' # One-liner string
                    '$38,$39,$3A,$3B,$3C,$3D,$3E,$0F')
        tokens = list(lexical(code))
        self.assertEquals(32, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        # self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertIsNotNone(code)
        expected = [0x0f, 0x30, 0x31, 0x32, 0x33, 0x35, 0x36, 0x37, 0x38,
                    0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x0F]
        self.assertEquals(expected, code)

    def test_db_3(self):
        tokens = list(lexical('.db $80, $00, $03, $80'))
        self.assertEquals(8, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        # self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertIsNotNone(code)
        expected = [0x80, 0x0, 0x03, 0x80]
        self.assertEquals(expected, code)

    def test_db_4(self):
        code = '''.db $80, $00, $03, $80
        .db $01, $02, $03, $04
        '''
        tokens = list(lexical(code))
        self.assertEquals(18, len(tokens))
        self.assertEquals('T_DIRECTIVE', tokens[0]['type'])
        # self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(2, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        code = semantic(ast)
        self.assertIsNotNone(code)
        expected = [0x80, 0x0, 0x03, 0x80, 1, 2, 3, 4]
        self.assertEquals(expected, code)
