# -*- coding: utf-8 -*-
'''
BEQ, Branch on Result Zero Test

This is a test for the branch instruction BMI of
the 6502. This instruction performs the branch
if Z == 1.
'''

import unittest
from pynes.tests import MetaInstructionCase


class BeqRelTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BEQ $10'
    lex = [('T_INSTRUCTION', 'BEQ'), ('T_ADDRESS', '$10')]
    syn = ['S_RELATIVE']
    code = [0xf0, 0x0e]
