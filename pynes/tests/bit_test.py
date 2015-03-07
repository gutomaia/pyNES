# -*- coding: utf-8 -*-

import unittest
from pynes.tests import MetaInstructionCase


class BitZpTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BIT $00'
    lex = [('T_INSTRUCTION', 'BIT'), ('T_ADDRESS', '$00')]
    syn = ['S_ZEROPAGE']
    code = [0x24, 0x00]

class BitAbsTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BIT $1234'
    lex = [('T_INSTRUCTION', 'BIT'), ('T_ADDRESS', '$1234')]
    syn = ['S_ABSOLUTE']
    code = [0x2c, 0x34, 0x12]
