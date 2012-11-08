#TODO: coding

import unittest

from pynes.composer import *

from pynes.bitbag import *


class JoypadTest(unittest.TestCase):


    def test_joypad1(self):
        cart = Cartridge()
        joypad_1 = Joypad(1, Cartridge())
        self.assertFalse(joypad_1.is_used)
        self.assertEquals('', joypad_1.to_asm())

    def test_joypad2(self):
        cart = Cartridge()
        joypad_2 = Joypad(2, Cartridge())
        self.assertFalse(joypad_2.is_used)
        self.assertEquals('', joypad_2.to_asm())

    def test_joypad1_with_up_event(self):
        cart = Cartridge()
        joypad_1 = Joypad(1, cart)
        cart._asm_chunks['joypad1_up'] = '  LDA $0200\n'
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
        self.assertTrue('JoyPad2' not in asm )
