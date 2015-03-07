# -*- coding: utf-8 -*-
'''
AND, Logical AND with Accumulator Test

This is a test for the logical instruction AND of
the 6502. In the 6502 the logical AND could be
performed against the content of the accumulator or
a content at a specific location.
'''
import unittest
from pynes.tests import MetaInstructionCase


class AndImmTest(unittest.TestCase):
    '''
    Test the logical operation AND between $10(Decimal 16)
    and the content of the Accumulator
    '''
    __metaclass__ = MetaInstructionCase
    asm = 'AND #$10'
    lex = [('T_INSTRUCTION', 'AND'), ('T_HEX_NUMBER', '#$10')]
    syn = ['S_IMMEDIATE']
    code = [0x29, 0x10]

class AndImmWithDecimal(unittest.TestCase):
    '''
    Test the logical operation AND between #10(Decimal 10)
    and the content of the Accumulator
    '''

    __metaclass__ = MetaInstructionCase
    asm = 'AND #10'
    lex = [('T_INSTRUCTION', 'AND'),('T_DECIMAL_NUMBER', '#10')]
    syn = ['S_IMMEDIATE']
    code = [0x29, 0x0a]

class AndImmWithBinary(unittest.TestCase):
    '''
    Test the logical operation AND between #%00000100 (Decimal 4)
    and the content of the Accumulator
    '''

    __metaclass__ = MetaInstructionCase
    asm = 'AND #%00000100'
    lex = [('T_INSTRUCTION', 'AND'),('T_BINARY_NUMBER', '#%00000100')]
    syn = ['S_IMMEDIATE']
    code = [0x29, 0x04]

class AndZp(unittest.TestCase):
    '''
    Test the logical operation AND between the content of
    accumulator and the content of zero page address $00
    '''

    __metaclass__ = MetaInstructionCase
    asm = 'AND $00'
    lex = [('T_INSTRUCTION', 'AND'),('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0x25, 0x00]

class AndZpx(unittest.TestCase):
    '''
    Test the logical operation AND between the content of
    accumulator and the content located at zero page with
    address calculated from $10 adding content of X
    '''

    __metaclass__ = MetaInstructionCase
    asm = 'AND $10,X'
    lex = [('T_INSTRUCTION', 'AND'),('T_ADDRESS', '$10'),
           ('T_SEPARATOR', ','),('T_REGISTER', 'X')]
    syn = ['S_ZEROPAGE_X']
    code = [0x35, 0x10]

class AndAbs(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'AND $1234'
    lex = [('T_INSTRUCTION', 'AND'),('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0x2d, 0x34, 0x12]

class AndAbsx(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'AND $1234,X'
    lex = [('T_INSTRUCTION', 'AND'),('T_ADDRESS', '$1234'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ABSOLUTE_X']
    code = [0x3d, 0x34, 0x12]

class AndAbsy(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'AND $1234,Y'
    lex = [('T_INSTRUCTION', 'AND'),('T_ADDRESS', '$1234'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'Y')]
    syn = ['S_ABSOLUTE_Y']
    code = [0x39, 0x34, 0x12]

class AndIndx(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'AND ($20,X)'
    lex = [('T_INSTRUCTION', 'AND'),('T_OPEN','('),
           ('T_ADDRESS', '$20'), ('T_SEPARATOR', ','),
           ('T_REGISTER', 'X'), ('T_CLOSE', ')')]
    syn = ['S_INDIRECT_X']
    code = [0x21, 0x20]

class AndIndy(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'AND ($20),Y'
    lex = [('T_INSTRUCTION', 'AND'),('T_OPEN','('),
           ('T_ADDRESS', '$20'), ('T_CLOSE', ')'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'Y'), ]
    syn = ['S_INDIRECT_Y']
    code = [0x31, 0x20]
