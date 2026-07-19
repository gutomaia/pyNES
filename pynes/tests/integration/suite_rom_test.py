"""Suite ROM: one cartridge collecting many test cases, each
running with its asserts ON the cartridge and printing its verdict
('NNN OK' / 'NNN FAIL') on its own line -- the whole test suite
visually checkable on a NES screen.

Expected values come from the CPython twin: each case body runs in
Python first, and the on-cart asserts compare against what CPython
produced.
"""

import os
from unittest import TestCase

from pynes.tests.suite import (
    MetaSuiteRomTest,
    SuiteRom,
    SuiteRomTestCase,
)
from pynes.tests.nes_runner import NESRunner
from pynes.tests.mixins.demos import text
from pynes.tests.array_spec import ArraySpec
from pynes.tests.assign_spec import AssignSpec
from pynes.tests.bitwise_spec import BitwiseSpec
from pynes.tests.comparison_spec import ComparisonSpec
from pynes.tests.cpu_spec import CPUSpec
from pynes.tests.factorial_spec import FactorialSpec
from pynes.tests.fibonacci_spec import FibonacciSpec
from pynes.tests.for_spec import ForSpec
from pynes.tests.function_spec import FunctionSpec
from pynes.tests.if_spec import IfSpec
from pynes.tests.math_spec import MathSpec
from pynes.tests.sort_bubble_spec import SortBubbleSpec
from pynes.tests.sort_insertion_spec import SortInsertionSpec
from pynes.tests.sort_quicksort_spec import SortQuicksortSpec
from pynes.tests.sort_selection_spec import SortSelectionSpec
from pynes.tests.uint16_spec import Uint16Spec
from pynes.tests.while_spec import WhileSpec

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    '..',
    'output',
    'suite',
    'SuiteRomTest.nes',
)


class SuiteRomTest(TestCase):

    @classmethod
    def setUpClass(cls):
        suite = SuiteRom()
        suite.add_case('addition', 'var_a = 2 + 3')
        suite.add_case(
            'loop',
            'var_n = 5\n'
            'var_total = 0\n'
            'while var_n > 0:\n'
            '    var_total += var_n\n'
            '    var_n -= 1\n',
        )
        # a broken expectation must FAIL on the cartridge itself
        suite.add_case('broken', 'var_b = 1 + 1', expect={'var_b': 3})
        cls.suite = suite
        cls.rom_path = suite.write_nes(OUTPUT_PATH)
        cls.runner = NESRunner(suite.python_source())
        cls.runner.run_reset()

    def _line(self, index):
        number = text(self.runner, 2, 2 + index, 3)
        verdict = text(self.runner, 6, 2 + index, 4)
        return number, verdict

    def test_passing_case_prints_ok(self):
        number, verdict = self._line(0)
        self.assertEqual(number, b'001')
        self.assertEqual(verdict[:2], b'OK')

    def test_case_with_loop_prints_ok(self):
        number, verdict = self._line(1)
        self.assertEqual(number, b'002')
        self.assertEqual(verdict[:2], b'OK')

    def test_on_cart_assert_catches_a_failure(self):
        number, verdict = self._line(2)
        self.assertEqual(number, b'003')
        self.assertEqual(verdict, b'FAIL')

    def test_expectations_come_from_the_cpython_twin(self):
        self.assertEqual(self.suite.cases[0].expect, {'var_a': 5})
        self.assertEqual(
            self.suite.cases[1].expect, {'var_n': 0, 'var_total': 15}
        )

    def test_nes_file_written_to_the_output_path(self):
        self.assertTrue(os.path.exists(self.rom_path))
        with open(self.rom_path, 'rb') as f:
            header = f.read(4)
        self.assertEqual(header, b'NES\x1a')

    def test_cases_do_not_share_variables(self):
        # var_a from case 1 must not leak into other cases: each case
        # body lives in its own function scope
        source = self.suite.python_source()
        self.assertIn('def case_1():', source)
        self.assertIn('def case_2():', source)
        self.assertIn('def case_3():', source)


class OnCartSuiteTest(SuiteRomTestCase):
    """Each test gathers its case; tearDownClass builds
    output/suite/OnCartSuiteTest.nes, boots it on FCEUX and demands
    an OK on every line."""

    def test_addition(self):
        self.run_case('var_a = 2 + 3')

    def test_multiplication(self):
        self.run_case('var_m = 6 * 7')

    def test_while_loop(self):
        self.run_case(
            'var_n = 5\n'
            'var_total = 0\n'
            'while var_n > 0:\n'
            '    var_total += var_n\n'
            '    var_n -= 1\n'
        )


class MathOnCartTest(SuiteRomTestCase, MathSpec, metaclass=MetaSuiteRomTest):
    """The math twin spec with its asserts running on the cartridge."""


class IfOnCartTest(SuiteRomTestCase, IfSpec, metaclass=MetaSuiteRomTest):
    """The if twin spec with its asserts running on the cartridge."""


class WhileOnCartTest(SuiteRomTestCase, WhileSpec, metaclass=MetaSuiteRomTest):
    """The while twin spec with its asserts running on the cartridge."""


class ArrayOnCartTest(SuiteRomTestCase, ArraySpec, metaclass=MetaSuiteRomTest):
    """The array twin spec with its asserts running on the cartridge."""


class AssignOnCartTest(
    SuiteRomTestCase, AssignSpec, metaclass=MetaSuiteRomTest
):
    """The assign twin spec with its asserts running on the cartridge."""


class BitwiseOnCartTest(
    SuiteRomTestCase, BitwiseSpec, metaclass=MetaSuiteRomTest
):
    """The bitwise twin spec with its asserts running on the cartridge."""


class ComparisonOnCartTest(
    SuiteRomTestCase, ComparisonSpec, metaclass=MetaSuiteRomTest
):
    """The comparison twin spec with its asserts on the cartridge."""


class CPUOnCartTest(SuiteRomTestCase, CPUSpec, metaclass=MetaSuiteRomTest):
    """The cpu twin spec with its asserts running on the cartridge."""


class FactorialOnCartTest(
    SuiteRomTestCase, FactorialSpec, metaclass=MetaSuiteRomTest
):
    """The factorial twin spec with its asserts on the cartridge."""


class FibonacciOnCartTest(
    SuiteRomTestCase, FibonacciSpec, metaclass=MetaSuiteRomTest
):
    """The fibonacci twin spec with its asserts on the cartridge."""


class ForOnCartTest(SuiteRomTestCase, ForSpec, metaclass=MetaSuiteRomTest):
    """The for twin spec with its asserts running on the cartridge."""


class FunctionOnCartTest(
    SuiteRomTestCase, FunctionSpec, metaclass=MetaSuiteRomTest
):
    """The function twin spec with its asserts on the cartridge."""


class SortBubbleOnCartTest(
    SuiteRomTestCase, SortBubbleSpec, metaclass=MetaSuiteRomTest
):
    """The bubble sort twin spec with its asserts on the cartridge."""


class SortInsertionOnCartTest(
    SuiteRomTestCase, SortInsertionSpec, metaclass=MetaSuiteRomTest
):
    """The insertion sort twin spec with its asserts on the cartridge."""


class SortQuicksortOnCartTest(
    SuiteRomTestCase, SortQuicksortSpec, metaclass=MetaSuiteRomTest
):
    """The quicksort twin spec with its asserts on the cartridge."""


class SortSelectionOnCartTest(
    SuiteRomTestCase, SortSelectionSpec, metaclass=MetaSuiteRomTest
):
    """The selection sort twin spec with its asserts on the cartridge."""


class Uint16OnCartTest(
    SuiteRomTestCase, Uint16Spec, metaclass=MetaSuiteRomTest
):
    """The uint16 twin spec running with its asserts on the cartridge."""
