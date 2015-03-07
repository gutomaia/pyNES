# -*- coding: utf-8 -*-
import unittest
from pynes.tests import MetaInstructionCase


class CliImplTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CLI'
    lex = [('T_INSTRUCTION', 'CLI')]
    syn = ['S_IMPLIED']
    code = [0x58]
