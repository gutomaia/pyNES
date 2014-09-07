# -*- coding: utf-8 -*-

import unittest

from pynes.tests import ComposerTestCase


class ComposerConditionalTest(ComposerTestCase):

    def test_if_main(self):
        (
            self.assert_asm_without_ines_from(
                'if __name__ == "main":\n'
                '  pass\n'
            )
            # .has('.rsset $0000')
            # .and_then('variable .rs 1')
        )

    def test_if_true(self):
        (
            self.assert_asm_without_ines_from(
                'variable = True\n'
                'if variable:\n'
                '  variable = False\n'
                'else:\n'
                '  variable = True\n'
            )
            # .has('.rsset $0000')
            # .and_then('variable .rs 1')
        )
