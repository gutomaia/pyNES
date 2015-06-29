# -*- coding: utf-8 -*-

import unittest
import ast

from pynes.asm import *
from pynes.block import AsmBlock

from pynes.composer import PyNesVisitor

class PyNesVisitorTest(unittest.TestCase):

    def visit(self, code):
        python_code = ast.parse(code)
        visit = PyNesVisitor()
        visit.visit(python_code)
        return visit.get_symbol_table()

    def test_visit_code_with_from_import(self):
        code = "from pynes.core import press_start"

        symbol_table = self.visit(code)

        self.assertIn('press_start', symbol_table)
        symbol = symbol_table['press_start']
        self.assertEquals(symbol['type'], 'module')
        self.assertEquals(symbol['module'], 'pynes.core.press_start')

    def test_visit_code_with_function(self):
        code = '\n'.join([
                "def reset():",
                "  pass",
            ])

        symbol_table = self.visit(code)

        self.assertIn('reset', symbol_table)
        symbol = symbol_table['reset']
        self.assertEquals(symbol['type'], 'function')

    def test_visit_code_with_integer(self):
        code = 'a = 1'

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')

    def test_visit_code_with_string(self):
        code = 'a = "string"'

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'string')

    def test_visit_code_with_two_integer_assigns(self):
        code = '\n'.join([
                'a = 1',
                'a = 2'
            ])

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['assigns'], 2)

    def test_visit_code_with_two_integer_assigns(self):
        code = '\n'.join([
                'a = "string 1"',
                'a = "string 2"'
            ])

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'string')
        self.assertEquals(symbol['assigns'], 2)

    def test_visit_code_with_two_assing_using_plus_aug(self):
        code = '\n'.join([
                'a = 0',
                'a += 1'
            ])

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['assigns'], 2)

    def test_visit_code_with_two_assing_using_minus_aug(self):
        code = '\n'.join([
                'a = 0',
                'a -= 1'
            ])

        symbol_table = self.visit(code)

        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['assigns'], 2)

    def test_visit_code_with_var_in_function_scope(self):
        code = '\n'.join([
                'def nmi():',
                '  a = 1'
            ])

        symbol_table = self.visit(code)

        self.assertIn('nmi', symbol_table)
        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['scope'], 'nmi')

    def test_visit_code_with_var_in_function_scope(self):
        code = '\n'.join([
                'def nmi():',
                '  a = 1'
            ])

        symbol_table = self.visit(code)

        self.assertIn('nmi', symbol_table)
        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['scope'], 'nmi')

    def test_visit_code_with_var_out_of_function_scope(self):
        code = '\n'.join([
                'def nmi():',
                '  pass',
                'a = 1'
            ])

        symbol_table = self.visit(code)

        self.assertIn('nmi', symbol_table)
        self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['scope'], '')

