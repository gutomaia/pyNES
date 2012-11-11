# -*- coding: utf-8 -*-

import unittest

from pynes.tests import ComposerTestCase


class ComposerMovingSpriteTest(ComposerTestCase):

    def test_moving_sprite(self):
        f = open('pynes/examples/movingsprite.py')
        code = f.read()
        f.close()
        (
            self.assert_asm_from(code)
                .has('.bank 0')
                .and_then('WAITVBLANK:')
                .and_then('RESET:')
                .and_then('JSR WAITVBLANK')
                .and_then('CLEARMEM:')
                .and_then('JSR WAITVBLANK')
                .and_then('LoadPalettes:')
                .and_then('NMI:')
                .and_then('JoyPad1A:')
                .and_then('JoyPad1B:')
                .and_then('JoyPad1Select:')
                .and_then('JoyPad1Start:')
                .and_then('JoyPad1Up:')
                .and_then('JoyPad1Down:')
                .and_then('JoyPad1Left:')
                .and_then('JoyPad1Right:')
                .and_then('sprite:')
        )