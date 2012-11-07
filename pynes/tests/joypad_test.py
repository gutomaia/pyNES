#TODO: coding

import unittest

from pynes.python import *

from pynes.bitbag import *

class JoypadTest(unittest.TestCase):


    def test_joypad1(self):
        cart = Cartridge()
        asm = Joypad(1, Cartridge()).to_asm()
        self.assertTrue('JoyPad1A:' in asm)
        self.assertTrue('JoyPad1B:' in asm)
        self.assertTrue('JoyPad1Select:' in asm)
        self.assertTrue('JoyPad1Start:' in asm)
        self.assertTrue('JoyPad1Up:' in asm)
        self.assertTrue('JoyPad1Down:' in asm)
        self.assertTrue('JoyPad1Left:' in asm)
        self.assertTrue('JoyPad1Right:' in asm)
        self.assertTrue('JoyPad2' not in asm )

    def test_joypad2(self):
        asm = Joypad(2, Cartridge()).to_asm()
        self.assertTrue('JoyPad2A:' in asm)
        self.assertTrue('JoyPad2B:' in asm)
        self.assertTrue('JoyPad2Select:' in asm)
        self.assertTrue('JoyPad2Start:' in asm)
        self.assertTrue('JoyPad2Up:' in asm)
        self.assertTrue('JoyPad2Down:' in asm)
        self.assertTrue('JoyPad2Left:' in asm)
        self.assertTrue('JoyPad2Right:' in asm)
        self.assertTrue('JoyPad1' not in asm )

    def test_joypad1_with_up_event(self):
        cart = Cartridge()
        j1 = Joypad(1, cart)
        cart._asm_chunks['joypad1_up'] = '  LDA $0200\n'
        asm = j1.to_asm()
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
