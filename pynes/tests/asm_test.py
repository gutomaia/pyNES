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
            (
                SEI +
                CLD +
                LDX('#$40')
            )
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

    def test_waitvblank(self):

        @asm_context
        def waitvblank():
            BIT('$2002')
            BPL(waitvblank)
            RTS()

        actual = waitvblank()

        expected = (
                'BIT $2002\n'
                'BPL WAITVBLANK\n'
                'RTS\n')

        # TODO: self.assertEquals(expected, actual)



    def test_clearmem(self):

        @asm_context
        def clearmem():
            LDA('#$00')
            STA('$0000', X)
            STA('$0100', X)
            STA('$0200', X)
            STA('$0400', X)
            STA('$0500', X)
            STA('$0600', X)
            STA('$0700', X)
            LDA('#$FE')
            STA('$0300', X)
            INX()
            BNE(clearmem)

        actual = clearmem()
