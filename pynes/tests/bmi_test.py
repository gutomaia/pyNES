# -*- coding: utf-8 -*-
'''
BMI, Branch on Result Minus Test

This is a test for the branch instruction BMI of
the 6502. This instruction performs the branch
if N == 1.
'''

import unittest
from pynes.tests import MetaInstructionCase


class BmiRelTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BMI $10'
    lex = [('T_INSTRUCTION', 'BMI'), ('T_ADDRESS', '$10')]
    syn = ['S_RELATIVE']
    code = [0x30, 0x0e]
