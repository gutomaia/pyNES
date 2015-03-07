# -*- coding: utf-8 -*-
'''
CLC, Clear Carry

This is a test for the clear carry instruction
'''


import unittest
from pynes.tests import MetaInstructionCase


class ClsImplTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CLC'
    lex = [('T_INSTRUCTION', 'CLC')]
    syn = ['S_IMPLIED']
    code = [0x18]
