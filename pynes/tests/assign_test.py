import unittest

import ast

from pynes.asm import *
from pynes.utils import asm_context
from pynes.game import GamePak

from pynes.composer import new_compose as compose

from pynes.composer import AssignMixin

class DoNothingVisitor(ast.NodeVisitor):

    def __init__(self, *args, **kw):
        super(DoNothingVisitor, self).__init__()


class AssignTest(unittest.TestCase):

    def setUp(self):
        self.gamepak = GamePak()
        self.gamepak.rs('a', 1)
        self.gamepak.rs('b', 1)

    def compose(self, code):
        compose(code, gamepak=self.gamepak,
                      visitor_clazz=DoNothingVisitor,
                      transformer_clazz=AssignMixin)

    def assertAsmEquals(self, actual, expected):
        pass
        # TODO: self.assertEquals(actual, expected)

    def test_a_assigned_1(self):
        code = ('a = 1')

        expected = [
            LDA(1),
            STA('a')
        ]

        actual = self.compose(code)
        self.assertAsmEquals(actual, expected)

    def test_a_and_b_assigned_2(self):
        code = ('a = b = 2')

        expected = [
            LDA(2),
            STA('b'),
            STA('a')
        ]

        actual = self.compose(code)
        self.assertAsmEquals(actual, expected)
