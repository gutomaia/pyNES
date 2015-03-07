# -*- coding: utf-8 -*-
'''
ASL, Arithmetic Shift Left

This is a test for the bit manipulation instruction ASL.
'''
import unittest
from pynes.tests import MetaInstructionCase


class AslImmTest(unittest.TestCase):
    # TODO see the accumulator type instruction, ASL A
    __metaclass__ = MetaInstructionCase
    asm = 'ASL #$10'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_HEX_NUMBER', '#$10')]
    syn = ['S_IMMEDIATE']
    code = [0x0a, 0x10]


class AslImmWithDecimal(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL #10'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_DECIMAL_NUMBER', '#10')]
    syn = ['S_IMMEDIATE']
    code = [0x0a, 0x0A]


class AslImmWithBinary(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL #%00000100'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_BINARY_NUMBER', '#%00000100')]
    syn = ['S_IMMEDIATE']
    code = [0x0a, 0x04]


class AslZpTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL $00'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0x06, 0x00]


class AslZpxTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL $10,X'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_ADDRESS', '$10'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ZEROPAGE_X']
    code = [0x16, 0x10]


class AslAbsTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL $1234'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0x0e, 0x34, 0x12]


class AslAbsxTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase
    asm = 'ASL $1234,X'
    lex = [('T_INSTRUCTION', 'ASL'), ('T_ADDRESS', '$1234'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ABSOLUTE_X']
    code = [0x1e, 0x34, 0x12]
