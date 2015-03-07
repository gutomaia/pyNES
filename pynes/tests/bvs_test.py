# -*- coding: utf-8 -*-
'''
BVS, Branch on Overflow Set Test

This is a test for the branch instruction BMI of
the 6502. This instruction performs the branch
if V == 1.
'''

import unittest
from pynes.tests import MetaInstructionCase


class BvsRelTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BVS $10'
    lex = [('T_INSTRUCTION', 'BVS'), ('T_ADDRESS', '$10')]
    syn = ['S_RELATIVE']
    code = [0x70, 0x0e]
