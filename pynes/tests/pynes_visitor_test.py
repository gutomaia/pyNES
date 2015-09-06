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

    def test_visitor_with_custom_symbol_table(self):
        class CustomSymbolTable(dict):
            pass

        symbol_table = CustomSymbolTable()
        visitor = PyNesVisitor(symbol_table=symbol_table)
        self.assertIsNotNone(visitor.symbol_table)
        self.assertEquals(visitor.symbol_table, symbol_table)

    def test_visit_code_with_from_import(self):
        code = "from pynes.core import press_start"

        symbol_table = self.visit(code)

        self.assertIn('press_start', symbol_table)
        symbol = symbol_table['press_start']
        self.assertEquals(symbol['type'], 'module')
        self.assertEquals(symbol['module'], 'pynes.core.press_start')

    def test_visit_code_with_from_import_using_stdlib(self):
        code = "from pynes_stdlib.core import wait_vblank"

        symbol_table = self.visit(code)

        # self.assertIn('wait_vblank', symbol_table)
        symbol = symbol_table['wait_vblank']
        self.assertEquals(symbol['type'], 'module')
        self.assertEquals(symbol['module'], 'pynes_stdlib.core.wait_vblank')


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
        self.assertEquals(symbol['assigns'], 1)

    def test_visit_code_with_one_integer_assign(self):
        code = 'a = 1'

        symbol_table = self.visit(code)

        # self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['assigns'], 1)


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

    def test_visit_code_with_three_integer_assigns(self):
        code = '\n'.join([
            'a = 1',
            'a = 2',
            'a = 3'
            ])

        symbol_table = self.visit(code)

        # self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['assigns'], 3)

    def test_visit_code_with_two_strings_assigns(self):
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

        # self.assertIn('nmi', symbol_table)
        # self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        self.assertEquals(symbol['type'], 'int')
        self.assertEquals(symbol['scope'], '')

    def test_visit_same_varname_in_two_scopes(self):
        code = '\n'.join([
            'def nmi():',
            '  a = 2',
            'a = 1'
            ])

        symbol_table = self.visit(code)

        # self.assertIn('nmi', symbol_table)
        # self.assertIn('a', symbol_table)
        symbol = symbol_table['a']
        # TODO: self.assertEquals(symbol['name'], 'a')
        self.assertEquals(symbol['type'], 'int')
        # TODO: self.assertEquals(symbol['scope'], '')


    def test_visit_code_with_several_immutable_string_assing_in_scope(self):
        code = '\n'.join([
            'title = "Super Game"',
            'one_player = "One Player"',
            'two_player = "Two Player"',
            'text = title',
            'text = one_player'
            ])

        symbol_table = self.visit(code)

        # self.assertIn('nmi', symbol_table)
        # self.assertIn('a', symbol_table)
        symbol = symbol_table['title']
        self.assertEquals(symbol['type'], 'string')
        self.assertEquals(symbol['scope'], '')
        self.assertEquals(symbol['assigns'], 1)

    def test_visit_function_called_once(self):
        code = '\n'.join([
            'def move(x, y):',
            '   pass',
            'move(1,2)'
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['move']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['calls'], 1)

    def test_visit_function_called_twice(self):
        code = '\n'.join([
            'def move(x, y):',
            '   pass',
            'move(1,2)',
            'move(3,4)'
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['move']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['calls'], 2)

    def test_visit_function_with_arguments(self):
        code = '\n'.join([
            'def move(x, y):',
            '   pass',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['move']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['arguments'], ['x', 'y'])

    def test_single_argument_type_hint(self):
        code = '\n'.join([
            'def sqrt(x):',
            '   pass',
            'sqrt(2)',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['sqrt']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['argument']['x']['types'], set(['int']))

    def test_single_argument_type_hint_using_named_arg(self):
        code = '\n'.join([
            'def sqrt(x):',
            '   pass',
            'sqrt(x=2)',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['sqrt']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['argument']['x']['types'], set(['int']))

    def test_positional_argument_type_hint(self):
        code = '\n'.join([
            'def move(x, y):',
            '   pass',
            'move(1, 2)',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['move']
        self.assertEquals(symbol['type'], 'function')
        # self.assertEquals(symbol['argument']['x']['types'], set(['int']))

    def test_positional_argument_type_hint_using_name_arg(self):
        code = '\n'.join([
            'def move(x, y):',
            '   pass',
            'move(x=3, y=4)',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['move']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['argument']['x']['types'], set(['int']))
        self.assertEquals(symbol['argument']['y']['types'], set(['int']))

    def test_positional_argument_type_hint_using_symbols(self):
        code = '\n'.join([
            'pi = 3',
            'def sqrt(x):',
            '   pass',
            'sqrt(pi)',
            ])

        symbol_table = self.visit(code)

        symbol = symbol_table['sqrt']
        self.assertEquals(symbol['type'], 'function')
        self.assertEquals(symbol['argument']['x']['types'], set(['int']))
