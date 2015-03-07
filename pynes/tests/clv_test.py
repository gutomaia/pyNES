# -*- coding: utf-8 -*-
import unittest
from pynes.tests import MetaInstructionCase


class ClvImplTest(unittest.TestCase):
    __metaclass__ = MetaInstructionCase

    asm = 'CLV'
    lex = [('T_INSTRUCTION', 'CLV')]
    syn = ['S_IMPLIED']
    code = [0xb8]
