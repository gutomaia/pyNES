"""Python builtins that exist only for the NES target.

Unlike neslib functions (which model the NES platform), these exist to
make normal Python code compile: `print(x)` dispatches to the right
6502 output routine depending on the argument type. Only the variant
that is actually called gets bundled into the ROM.
"""

from unittest import TestCase

from pynes.cart import Cart


def compile_source(source):
    return Cart().compile(source)


MAIN = '''
@reset
def main():
    %s

    while True:
        pass
'''


class PrintDispatchTest(TestCase):
    """print() chooses the NES rendering routine by argument width."""

    def test_print_uint8_emits_put_num(self):
        asm = compile_source(MAIN % 'print(120)')
        self.assertIn('JSR neslib__put_num', asm)

    def test_print_uint8_variable(self):
        asm = compile_source(MAIN % 'value = 42\n    print(value)')
        self.assertIn('LDA main_value', asm)
        self.assertIn('JSR neslib__put_num', asm)

    def test_print_uint16_emits_put_num16(self):
        asm = compile_source(
            MAIN % 'value: uint16 = 1000\n    print(value)'
        )
        self.assertIn('JSR neslib__put_num16', asm)

    def test_print_uint16_call(self):
        asm = compile_source(
            '''
def big() -> uint16:
    return 1000

@reset
def main():
    print(big())

    while True:
        pass
'''
        )
        self.assertIn('JSR neslib__put_num16', asm)


class PrintBundlingTest(TestCase):
    """Only the print-related runtime actually referenced is bundled."""

    def test_put_num16_not_bundled_for_uint8_print(self):
        asm = compile_source(MAIN % 'print(5)')
        self.assertIn('neslib__put_num:', asm)
        self.assertNotIn('neslib__put_num16:', asm)

    def test_put_num_not_bundled_for_uint16_print(self):
        asm = compile_source(
            MAIN % 'value: uint16 = 1000\n    print(value)'
        )
        self.assertIn('neslib__put_num16:', asm)
        self.assertNotIn('neslib__put_num:', asm)
