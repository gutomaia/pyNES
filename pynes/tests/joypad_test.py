# TODO: coding

import unittest

from re import match

from pynes.game import Game, Joypad


class JoypadTest(unittest.TestCase):

    def test_joypad1(self):
        joypad_1 = Joypad(1, Game())
        self.assertFalse(joypad_1.is_used)
        self.assertEquals('', joypad_1.to_asm())

    def test_joypad2(self):
        joypad_2 = Joypad(2, Game())
        self.assertFalse(joypad_2.is_used)
        self.assertEquals('', joypad_2.to_asm())

    def test_joypad1_with_up_event(self):
        game = Game()
        joypad_1 = Joypad(1, game)
        game._asm_chunks['joypad1_up'] = '  LDA $0200\n'
        self.assertTrue(joypad_1.is_used)
        asm = joypad_1.to_asm()
        self.assertTrue('LDA $0200' in asm)
        self.assertTrue('JoyPad1A:' in asm)
        self.assertTrue('JoyPad1B:' in asm)
        self.assertTrue('JoyPad1Select:' in asm)
        self.assertTrue('JoyPad1Start:' in asm)
        self.assertTrue('JoyPad1Up:' in asm)
        self.assertTrue('JoyPad1Down:' in asm)
        self.assertTrue('JoyPad1Left:' in asm)
        self.assertTrue('JoyPad1Right:' in asm)
        self.assertTrue('JoyPad2' not in asm)
