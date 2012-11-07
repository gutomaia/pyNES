# -*- coding: utf-8 -*-

import unittest

from pynes.python import pynes_compiler, Cartridge

class PyNesCompilerTest(unittest.TestCase):

    def test_1_plus_1(self):
        code = '1 + 1'

        cart = pynes_compiler(code)
        asm = cart.to_asm()
        #self.assertEquals(1, len(cart.bitpaks))

    def test_movingsprite(self):
        code = (
            'from pynes.bitbag import *\n'

            #'import_chr("player.chr")\n'
            'palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,\n'
            '    0x0F, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59,\n'
            '    60, 61, 62, 63 ]\n'
            #'sprite = define_sprite()\n'
            'px = rs(1)\n'
            'py = rs(1)\n'

            'def reset():\n'
            '    wait_vblank()\n'
            #'    clearmen()\n'
            '    wait_vblank()\n'
            #'    load_palette(palette)\n'
            #'    load_sprite(sprite)\n'

            'def joypad1_up():\n'
            '    global y\n'
            '    py += 1\n'

            #'def joypad1_down():\n'
            #'    global y\n'
            #'    py -= 1\n'

            #'def joypad1_left():\n'
            #'    global x\n'
            #'    px -= 1\n'

            #'def joypad1_right():\n'
            #'    global x\n'
            #'    px += 1\n'
            )

        cart = pynes_compiler(code)
        asm = cart.to_asm()
        #self.assertEquals(1, len(cart.bitpaks))
        self.assertTrue('.bank 0' in asm)
        self.assertTrue('.org $C000' in asm)
        self.assertTrue('.bank 1' in asm)
        self.assertTrue('.org $E000' in asm)
        self.assertTrue('NMI:' in asm)
        self.assertTrue('JoyPad1Select:' in asm)
        self.assertTrue('JoyPad1Start:' in asm)
        self.assertTrue('JoyPad1A:' in asm)
        self.assertTrue('JoyPad1B:' in asm)
        self.assertTrue('JoyPad1Up:' in asm)
        self.assertTrue('JoyPad1Down:' in asm)
        self.assertTrue('JoyPad1Left:' in asm)
        self.assertTrue('JoyPad1Right:' in asm)

    def test_wait_vblank(self):
        code = (
            'from pynes.bitbag import *\n'

            'def reset():\n'
            '    wait_vblank()')
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(1, len(cart.bitpaks))
        self.assertTrue('.bank 0' in asm)
        self.assertTrue('.org $C000' in asm)
        self.assertTrue('.bank 1' not in asm)
        self.assertTrue('.org $E000' not in asm)

    def test_wait_vblank_called_twice(self):
        code = (
            'from pynes.bitbag import *\n'

            'def reset():\n'
            '    wait_vblank()\n'
            '    wait_vblank()')
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(1, len(cart.bitpaks))
        self.assertTrue('.bank 0' in asm)
        self.assertTrue('.org $C000' in asm)
        self.assertTrue('.bank 1' not in asm)
        self.assertTrue('.org $E000' not in asm)

    def test_palette_list_definition_from_00_to_0F(self):
        code = 'palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]'
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(1, len(cart._vars))
        self.assertEquals([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], cart.get_var('palette').list())
        src = (
            'palette:\n'
            '  .db $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,$0E,$0F')
        self.assertTrue(src in asm)
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        self.assertTrue('.bank 1' in asm)
        self.assertTrue('.org $E000' in asm)


    def test_palette_list_definition_from_0F_to_00(self):
        code = 'palette = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]'
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(1, len(cart._vars))
        self.assertEquals([15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0], cart.get_var('palette').list())
        src = (
            'palette:\n'
            '  .db $0F,$0E,$0D,$0C,$0B,$0A,$09,$08,$07,$06,$05,$04,$03,$02,$01,$00')
        self.assertTrue(src in asm)
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        self.assertTrue('.bank 1' in asm)
        self.assertTrue('.org $E000' in asm)

    def test_palette_list_definition_from_00_to_1F(self):
        code = ('palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,'
            '16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]')
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(1, len(cart._vars))
        self.assertEquals(range(32), cart.get_var('palette').list())
        src = (
            'palette:\n'
            '  .db $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,$0E,$0F\n'
            '  .db $10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$1A,$1B,$1C,$1D,$1E,$1F')
        self.assertTrue(src in asm)
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        self.assertTrue('.bank 1' in asm)
        self.assertTrue('.org $E000' in asm)

    def test_rs_with_x_and_y_with_size_1(self):
        code = (
            'from pynes.bitbag import *\n'
            'x = rs(1)\n'
            'y = rs(1)')
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(2, len(cart._vars))
        self.assertEquals(1, cart._vars['x'])
        self.assertEquals(1, cart._vars['y'])
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        self.assertTrue('.bank 1' not in asm)
        self.assertTrue('.org $E000' not in asm)

        self.assertTrue('.rsset $0000' in asm)
        self.assertTrue('x .rs 1' in asm)
        self.assertTrue('y .rs 1' in asm)

    def test_rs_with_scroll(self):
        code = (
            'from pynes.bitbag import *\n'
            'scroll = rs(1)\n'
            'nametable = rs(1)\n'
            'columnLow = rs(1)\n'
            'columnHigh = rs(1)\n'
            'sourceLow = rs(1)\n'
            'sourceHigh = rs(1)\n'
            'columnNumber = rs(1)\n')
        cart = pynes_compiler(code)
        asm = cart.to_asm()
        self.assertEquals(7, len(cart._vars))
        self.assertEquals(1, cart._vars['scroll'])
        self.assertEquals(1, cart._vars['nametable'])
        self.assertEquals(1, cart._vars['columnLow'])
        self.assertEquals(1, cart._vars['columnHigh'])
        self.assertEquals(1, cart._vars['sourceLow'])
        self.assertEquals(1, cart._vars['sourceHigh'])
        self.assertEquals(1, cart._vars['columnNumber'])
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        self.assertTrue('.bank 1' not in asm)
        self.assertTrue('.org $E000' not in asm)
        self.assertTrue('.rsset $0000' in asm)
        self.assertTrue('scroll .rs 1' in asm)
        self.assertTrue('nametable .rs 1' in asm)
        self.assertTrue('columnLow .rs 1' in asm)
        self.assertTrue('columnHigh .rs 1' in asm)
        self.assertTrue('sourceLow .rs 1' in asm)
        self.assertTrue('sourceHigh .rs 1' in asm)
        self.assertTrue('columnNumber .rs 1' in asm)
