# -*- coding: utf-8 -*-
'''
CMP, Compare with Accumulator Test
'''

import unittest
from pynes.tests import MetaInstructionCase


class CpmImmTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP #$10'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_HEX_NUMBER', '#$10')]
    syn = ['S_IMMEDIATE']
    code = [0xc9, 0x10]


class CpmImmDecimalTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP #10'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_DECIMAL_NUMBER', '#10')]
    syn = ['S_IMMEDIATE']
    code = [0xc9, 0x0a]


class CpmImmBinaryTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP #%00000100'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_BINARY_NUMBER', '#%00000100')]
    syn = ['S_IMMEDIATE']
    code = [0xc9, 0x04]


class CpmZpTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP $00'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0xc5, 0x00]


class CpmZpxTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP $10,X'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_ADDRESS', '$10'), ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ZEROPAGE_X']
    code = [0xd5, 0x10]


class CpmAbsTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP $1234'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0xcd, 0x34, 0x12]


class CpmAbsxTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP $1234, X'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_ADDRESS', '$1234'), ('T_SEPARATOR', ','), ('T_REGISTER', 'X')]
    syn = ['S_ABSOLUTE_X']
    code = [0xdd, 0x34, 0x12]


class CpmAbsyTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP $1234, Y'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_ADDRESS', '$1234'), ('T_SEPARATOR', ','), ('T_REGISTER', 'Y')]
    syn = ['S_ABSOLUTE_Y']
    code = [0xd9, 0x34, 0x12]


class CpmIndxTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP ($20, X)'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_OPEN', '('), ('T_ADDRESS', '$20'),
           ('T_SEPARATOR', ','), ('T_REGISTER', 'X'), ('T_CLOSE', ')')]
    syn = ['S_INDIRECT_X']
    code = [0xc1, 0x20]


class CpmIndyTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CMP ($20),Y'
    lex = [('T_INSTRUCTION', 'CMP'), ('T_OPEN', '('), ('T_ADDRESS', '$20'),
           ('T_CLOSE', ')'), ('T_SEPARATOR', ','), ('T_REGISTER', 'Y'), ]
    syn = ['S_INDIRECT_Y']
    code = [0xd1, 0x20]
