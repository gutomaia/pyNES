# -*- coding: utf-8 -*-
'''
BNE, Branch on Result not Zero Test

This is a test for the branch instruction BMI of
the 6502. This instruction performs the branch
if Z == 0.
'''

import unittest
from pynes.tests import MetaInstructionCase


class BneRelTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BNE $10'
    lex = [('T_INSTRUCTION', 'BNE'), ('T_ADDRESS', '$10')]
    syn = ['S_RELATIVE']
    code = [0xd0, 0x0e]
