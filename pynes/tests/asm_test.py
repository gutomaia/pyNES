import unittest

from pynes.asm import *
from pynes.utils import asm_context

class AsmTest(unittest.TestCase):

    def test_asm_context(self):
        with asm_context() as f:
            SEI()
            CLD()
            LDX('#$40')
            actual = f

        expected = ('SEI\n'
                    'CLD\n'
                    'LDX #$40\n')

        self.assertEquals(expected, actual.asm)

    def test_asm_context_2(self):
        return
        with asm_context() as f:
            SEI
            CLD
            LDX('#$40')
            actual = f

        expected = ('SEI\n'
                    'CLD\n'
                    'LDX #$40\n')

        self.assertEquals(expected, actual.asm)

    def test_asm(self):

        @asm_context
        def func():
            SEI()
            CLD()
            LDX('#$40')

        actual = func()

        expected = ('SEI\n'
                    'CLD\n'
                    'LDX #$40\n')

        self.assertEquals(expected, actual)

