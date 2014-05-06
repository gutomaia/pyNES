# -*- coding: utf-8 -*-

import unittest
from types import GeneratorType
from pynes.compiler import (lexical, syntax,
                            t_zeropage, t_address, t_separator, get_labels)


class CompilerTest(unittest.TestCase):

    def setUp(self):
        self.zeropage = dict(
            type='T_ADDRESS',
            value='$00'
        )
        self.address10 = dict(
            type='T_ADDRESS',
            value='$1234'
        )
        self.separator = dict(
            type='T_SEPARATOR',
            value=','
        )

    def test_t_zeropage(self):
        self.assertTrue(t_zeropage([self.zeropage], 0))

    def test_t_address(self):
        self.assertTrue(t_address([self.address10], 0))

    def test_t_separator(self):
        self.assertTrue(t_separator([self.separator], 0))

    def test_compile_more_than_on_instruction(self):
        code = '''
            SEC         ;clear the carry
            LDA $20     ;get the low byte of the first number
            '''
        tokens = list(lexical(code))
        self.assertEquals(6, len(tokens))
        self.assertEquals('T_ENDLINE', tokens[0]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[1]['type'])
        self.assertEquals('T_ENDLINE', tokens[2]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[3]['type'])
        self.assertEquals('T_ADDRESS', tokens[4]['type'])
        self.assertEquals('T_ENDLINE', tokens[5]['type'])
        ast = syntax(tokens)
        self.assertEquals(2, len(ast))

    def test_compile_decimal(self):
        code = '''
            LDA #128
            STA $0203
        '''
        tokens = list(lexical(code))
        self.assertEquals(7, len(tokens))
        self.assertEquals('T_ENDLINE', tokens[0]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[1]['type'])
        self.assertEquals('T_DECIMAL_NUMBER', tokens[2]['type'])
        self.assertEquals('T_ENDLINE', tokens[3]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[4]['type'])
        self.assertEquals('T_ADDRESS', tokens[5]['type'])
        self.assertEquals('T_ENDLINE', tokens[6]['type'])

    def test_compile_list(self):
        code = '''
            palette:
              .db $0F,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,$0E,$0F
              .db $0F,$30,$31,$32,$33,$35,$36,$37,$38,$39,$3A,$3B,$3C,$3D,$3E,$0F
        '''
        tokens = list(lexical(code))
        ast = syntax(tokens)
        self.assertEquals(2, len(ast))

        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        self.assertEquals('.db', ast[0]['children'][0]['value'])
        self.assertEquals(32, len(ast[0]['children']))
        palette1 = [0x0f, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
                    0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]
        for i in range(len(palette1)):
            h = '$%02X' % palette1[i]
            self.assertEquals(h, ast[0]['children'][i * 2 + 1]['value'])
            self.assertEquals('S_DIRECTIVE', ast[1]['type'])

        self.assertEquals('S_DIRECTIVE', ast[1]['type'])
        self.assertEquals('.db', ast[0]['children'][0]['value'])
        self.assertEquals(32, len(ast[1]['children']))
        palette2 = [0x0f, 0x30, 0x31, 0x32, 0x33, 0x35, 0x36, 0x37, 0x38, 0x39,
                    0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x0f]
        for i in range(len(palette2)):
            h = '$%02X' % palette2[i]
            self.assertEquals(h, ast[1]['children'][i * 2 + 1]['value'])

    def test_instructions_with_labels(self):
        code = '''
              .org $C000

            WAITVBLANK:
              BIT $2002
              BPL WAITVBLANK
              RTS'''

        tokens = list(lexical(code))
        ast = syntax(tokens)
        self.assertEquals(4, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        self.assertEquals('S_ABSOLUTE', ast[1]['type'])
        self.assertEquals(['WAITVBLANK'], ast[1]['labels'])

        labels = get_labels(ast)
        expected = {'WAITVBLANK': 0xc000}

        self.assertEquals(expected, labels)

    def test_several_lists_with_labels(self):
        code = '''
            .org $E000

            palette:
              .db $0F,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,$0E,$0F
              .db $0F,$30,$31,$32,$33,$35,$36,$37,$38,$39,$3A,$3B,$3C,$3D,$3E,$0F

            sprites:
              .db $80, $00, $03, $80; Y pos, tile id, attributes, X pos
              '''

        tokens = list(lexical(code))
        ast = syntax(tokens)
        self.assertEquals(4, len(ast))
        self.assertEquals('S_DIRECTIVE', ast[0]['type'])
        self.assertEquals('.org', ast[0]['children'][0]['value'])
        self.assertEquals('S_DIRECTIVE', ast[1]['type'])
        self.assertEquals('.db', ast[1]['children'][0]['value'])
        self.assertEquals(['palette'], ast[1]['labels'])

        self.assertEquals('S_DIRECTIVE', ast[2]['type'])
        self.assertEquals('.db', ast[2]['children'][0]['value'])

        self.assertEquals('S_DIRECTIVE', ast[3]['type'])
        self.assertEquals('.db', ast[3]['children'][0]['value'])
        self.assertEquals(['sprites'], ast[3]['labels'])

        labels = get_labels(ast)
        expected = {'palette': 0xE000, 'sprites': 0xE000 + 32}

        self.assertEquals(expected, labels)

    def test_raise_erro_with_unknow_label(self):
        return
        with self.assertRaises(Exception):
            tokens = lexical('LDA unknow')
            list(tokens)

    def test_lexical_returns_a_generator(self):
        tokens = lexical('BIT $00')
        self.assertIsInstance(tokens, GeneratorType)

