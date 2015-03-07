# -*- coding: utf-8 -*-
import unittest
from pynes.tests import MetaInstructionCase


class CldImplTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CLD'
    lex = [('T_INSTRUCTION', 'CLD')]
    syn = ['S_IMPLIED']
    code = [0xd8]
