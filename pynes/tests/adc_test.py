# -*- coding: utf-8 -*-
'''
ADC, Add with Carry Test

This is an arithmetic instruction of the 6502.
'''

import unittest
from pynes.tests import MetaInstructionCase


class AdcImmTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between decimal 16
    and the content of the accumulator.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC #$10'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_HEX_NUMBER', '#$10')]
    syn = ['S_IMMEDIATE']
    code = [0x69, 0x10]


class AdcImmWithDecimalTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between decimal 10
    and the content of the accumulator.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC #10'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_DECIMAL_NUMBER', '#10')]
    syn = ['S_IMMEDIATE']
    code = [0x69, 0x0A]


class AdcImmWithBinaryTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between binary %00000100
    (Decimal 4) and the content of the accumulator.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC #%00000100'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_BINARY_NUMBER', '#%00000100')]
    syn = ['S_IMMEDIATE']
    code = [0x69, 0x04]


class AdcZpTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between the content of
    the accumulator and the content of the zero page address.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC $00'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0x65, 0x00]


class AdcZpxTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between the content of the
    accumulator and the content of the zero page with address
    calculated from $10 adding content of X.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC $10,X'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_ADDRESS', '$10'),
           ('T_SEPARATOR', ','),('T_REGISTER','X')]
    syn = ['S_ZEROPAGE_X']
    code = [0x75, 0x10]


class AdcAbsTest(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between the content of
    the accumulator and the content located at address $1234.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC $1234'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0x6d, 0x34, 0x12]


class AdcAbsx(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between the content of the
    accumulator and the content located at address $1234
    adding the content of X.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC $1234,X'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_ADDRESS', '$1234'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ABSOLUTE_X']
    code = [0x7d, 0x34, 0x12]


class AdcAbsy(unittest.TestCase):
    '''
    Test the arithmetic operation ADC between the content of the
    accumulator and the content located at address $1234
    adding the content of Y.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC $1234,Y'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_ADDRESS', '$1234'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'Y')]
    syn = ['S_ABSOLUTE_Y']
    code = [0x79, 0x34, 0x12]


class AdcIndx(unittest.TestCase):
    '''
    Test the arithmetic ADC operation between the content of the
    accumulator and the content located at the address
    obtained from the address calculated from the value
    stored in the address $20 adding the content of Y.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC ($20,X)'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_OPEN', '('),
           ('T_ADDRESS', '$20'), ('T_SEPARATOR', ','),
           ('T_REGISTER', 'X'), ('T_CLOSE', ')')]
    syn = ['S_INDIRECT_X']
    code = [0x61, 0x20]


class AdcIndy(unittest.TestCase):
    '''
    Test arithmetic operation ADC between the content of the
    accumulator and the content located at the address
    obtained from the address calculated from the value
    stored in the address $20 adding the content of Y.
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'ADC ($20),Y'
    lex = [('T_INSTRUCTION', 'ADC'), ('T_OPEN', '('),
           ('T_ADDRESS', '$20'), ('T_CLOSE', ')'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'Y')]
    syn = ['S_INDIRECT_Y']
    code = [0x71, 0x20]
