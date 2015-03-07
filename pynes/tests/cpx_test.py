# -*- coding: utf-8 -*-
'''
CPX, Compare with X Test
'''

import unittest
from pynes.tests import MetaInstructionCase

from pynes.compiler import lexical, syntax, semantic

class CpxImmTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CPX #$10'
    lex = [('T_INSTRUCTION', 'CPX'), ('T_HEX_NUMBER', '#$10')]
    syn = ['S_IMMEDIATE']
    code = [0xe0, 0x10]


class CpxImmDecimalTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CPX #10'
    lex = [('T_INSTRUCTION', 'CPX'), ('T_DECIMAL_NUMBER', '#10')]
    syn = ['S_IMMEDIATE']
    code = [0xe0, 0x0a]


class CpxImmBinaryTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CPX #%00000100'
    lex = [('T_INSTRUCTION', 'CPX'), ('T_BINARY_NUMBER', '#%00000100')]
    syn = ['S_IMMEDIATE']
    code = [0xe0, 0x04]


class CpxZpTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CPX $00'
    lex = [('T_INSTRUCTION', 'CPX'), ('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0xe4, 0x00]


class CpxAbsTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CPX $1234'
    lex = [('T_INSTRUCTION', 'CPX'), ('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0xec, 0x34, 0x12]
