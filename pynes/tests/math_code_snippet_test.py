# -*- coding: utf-8 -*-
import unittest
import ast
import meta
from pynes.composer import PyNesTransformer
from pynes.asm import *
import os
from glob import glob


class DynamicFixture(type):

    def __new__(mcs, name, bases, args):

        def gen_pynes_test(filename):
            def test(self):
                code = open(filename).read()
                python_land = ast.parse(code)

                builder = PyNesTransformer()
                transformed = builder.visit(python_land)

                actual = meta.dump_python_source(transformed)

                base = os.path.splitext(os.path.basename(filename))[0]
                path = os.path.dirname(filename)
                pynes_filename = '%s/%s.pynes' % (path, base)
                expected = open(pynes_filename).read()
                self.assertEquals(actual.strip(), expected.strip())
            return test

        def gen_asm_test(filename):
            def test(self):
                base = os.path.splitext(os.path.basename(filename))[0]
                path = os.path.dirname(filename)
                pynes_filename = '%s/%s.pynes' % (path, base)
                asm_filename = '%s/%s.asm' % (path, base)
                self.assertTrue(os.path.exists(asm_filename), 'file does not exists %s' % asm_filename)
                python_instructions = open(pynes_filename).read()
                hacked = python_instructions
                expected = open(asm_filename).read().strip()
                context = {}
                exec hacked in context
                actual = context['game'].asm().strip()
                self.assertEquals(actual, expected)

                # exec python_instructions
            return test
        files = []
        files += glob('fixtures/code_snippet/math/*.py')
        files += glob('fixtures/code_snippet/logic/*.py')
        files += glob('fixtures/code_snippet/assign/*.py')
        # TODO: fix asm! files += glob('fixtures/code_snippet/structure/*.py')

        for f in files:
            args['test_pynes_%s' % f] = gen_pynes_test(f)
            args['test_asm_%s' % f] = gen_asm_test(f)

        return type.__new__(mcs, name, bases, args)


class MathOperationTest(unittest.TestCase):
    __metaclass__ = DynamicFixture

    def test_ok(self):
        pass
