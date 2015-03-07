# -*- coding: utf-8 -*-
'''
BCS, Branch on Carry Set Test

This is a test for the branch instruction BMI of
the 6502. This instruction performs the branch
if C == 0.
'''

import unittest
from pynes.tests import MetaInstructionCase


class BcsRelTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'BCS $10'
    lex = [('T_INSTRUCTION', 'BCS'), ('T_ADDRESS', '$10')]
    syn = ['S_RELATIVE']
    code = [0xb0, 0x0e]
