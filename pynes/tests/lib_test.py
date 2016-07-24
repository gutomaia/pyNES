# -*- coding: utf-8 -*-
import unittest
import ast
import meta

from pynes.asm import *
from pynes.composer import PyNesTransformer


class LibTest(unittest.TestCase):

    def transform(self, code):
        python_land = ast.parse(code)
        transformer = PyNesTransformer()
        builder = PyNesTransformer()
        transformed = builder.visit(python_land)
        return meta.dump_python_source(transformed)

    def assert_valid_code(self, code):
        context = {}
        exec(code) in context

    @unittest.skip("TODO")
    def test_assert_that_press_start_does_is_not_translated(self):
        code = '\n'.join([
            "from pynes.core import press_start",
            "press_start()",
            ])

        actual = self.transform(code).strip()
        self.assert_valid_code(actual)

        expected = '\n'.join([
            "from pynes.asm import *",
            "from pynes.core import press_start",
        ]).strip()

        self.assertEquals(actual, expected)

    @unittest.skip("TODO")
    def test_assert_that_any_def_with_ignore_is_not_translated(self):
        code = '\n'.join([
            "from pynes.lib import ignoredef",
            "@ignoredef",
            "def ignore_me():",
            "  pass"
            ])

        actual = self.transform(code).strip()
        self.assert_valid_code(actual)

        expected = '\n'.join([
            "from pynes.asm import *",
            "from pynes.lib import ignoredef",
            ]).strip()

        # TODO: self.assertEquals(actual, expected)
