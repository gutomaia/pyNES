# -*- coding: utf-8 -*-
'''
ADC, Add with Carry Test

This is an arithmetic instruction of the 6502.
'''

import unittest
from pynes.compiler import lexical, syntax, semantic


class AdcTest(unittest.TestCase):


    def test_adc_imm(self):
        '''
        Test the arithmetic operation ADC between decimal 10
        and the content of the accumulator.
        '''
        tokens = lexical('ADC #10')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_HEX_NUMBER', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_IMMEDIATE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x69, 0x10])

    def test_adc_zp(self):
        '''
        Test the arithmetic operation ADC between the content of
        the accumulator and the content of the zero page address.
        '''
        tokens = lexical('ADC $00')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ZEROPAGE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x65, 0x00])

    def test_adc_zpx(self):
        '''
        Test the arithmetic operation ADC between the content of the
        accumulator and the content of the zero page with address
        calculated from $10 adding content of X.
        '''
        tokens = lexical('ADC $10,X')
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
        self.assertEquals(code, [0x75, 0x10])

    def test_adc_abs(self):
        '''
        Test the arithmetic operation ADC between the content of 
        the accumulator and the content located at address $1234.
        '''
        tokens = lexical('ADC $1234')
        self.assertEquals(2 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('$1234', tokens[1]['value'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ABSOLUTE', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x6d, 0x34, 0x12])


    def test_adc_absx(self):
        '''
        Test the arithmetic operation ADC between the content of the
        accumulator and the content located at address $1234
        adding the content of X.
        '''
        tokens = lexical('ADC $1234,X')
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
        self.assertEquals(code, [0x7d, 0x34, 0x12])

    def test_adc_absy(self):
        '''
        Test the arithmetic operation ADC between the content of the
        accumulator and the content located at address $1234
        adding the content of Y.
        '''
        tokens = lexical('ADC $1234,Y')
        self.assertEquals(4 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_ADDRESS', tokens[1]['type'])
        self.assertEquals('T_SEPARATOR', tokens[2]['type'])
        self.assertEquals('T_REGISTER', tokens[3]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_ABSOLUTE_Y', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x79, 0x34, 0x12])

    def test_adc_indx(self):
        '''
        Test the arithmetic ADC operation between the content of the
        accumulator and the content located at the address
        obtained from the address calculated from the value
        stored in the address $20 adding the content of Y.
        '''
        tokens = lexical('ADC ($20,X)')
        self.assertEquals(6 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_OPEN', tokens[1]['type'])
        self.assertEquals('T_ADDRESS', tokens[2]['type'])
        self.assertEquals('$20', tokens[2]['value'])
        self.assertEquals('T_SEPARATOR', tokens[3]['type'])
        self.assertEquals('T_REGISTER', tokens[4]['type'])
        self.assertEquals('T_CLOSE', tokens[5]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_INDIRECT_X', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x61, 0x20])

    def test_adc_indy(self):
        '''
        Test arithmetic operation ADC between the content of the
        accumulator and the content located at the address
        obtained from the address calculated from the value
        stored in the address $20 adding the content of Y.
        '''
        tokens = lexical('ADC ($20),Y')
        self.assertEquals(6 , len(tokens))
        self.assertEquals('T_INSTRUCTION', tokens[0]['type'])
        self.assertEquals('T_OPEN', tokens[1]['type'])
        self.assertEquals('T_ADDRESS', tokens[2]['type'])
        self.assertEquals('T_CLOSE', tokens[3]['type'])
        self.assertEquals('T_SEPARATOR', tokens[4]['type'])
        self.assertEquals('T_REGISTER', tokens[5]['type'])
        ast = syntax(tokens)
        self.assertEquals(1 , len(ast))
        self.assertEquals('S_INDIRECT_Y', ast[0]['type'])
        code = semantic(ast)
        self.assertEquals(code, [0x71, 0x20])
