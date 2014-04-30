# -*- coding: utf-8 -*-
from pynes.tests import ComposerTestCase

from pynes.game import Game, PPUSprite

from pynes.composer import compose

from pynes.nes_types import NesString


class ComposerTest(ComposerTestCase):

    def test_sprite_assigned_128_to_x(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).x = 128'
        )
            .has('LDA #128')
            .and_then('STA $0203'))

    def test_sprite_assigned_126_plus_2_optimized(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).x = 126 + 2')
         .has('LDA #128')
         .and_then('STA $0203'))

    def test_sprite_zero_assigned_127_plus_1_optimized(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).x = 127 + 1')
         .has('LDA #128')
         .and_then('STA $0203'))

    def test_sprite_zero_assigned_129_to_y(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).y = 129')
         .has('LDA #129')
         .and_then('STA $0200'))

    def test_sprite_zero_augassign_y_plus_five(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).y += 5')
         .has('LDA $0200')
         .and_then('CLC')
         .and_then('ADC #5')
         .and_then('STA $0200'))

    def test_sprite_zero_augassign_x_plus_five(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'get_sprite(0).x += 5')
         .has('LDA $0203')
         .and_then('CLC')
         .and_then('ADC #5')
         .and_then('STA $0203'))

    def test_sprite_zero_augassign_y_minus_five(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).y -= 5')
         .has('LDA $0200')
         .and_then('SEC')
         .and_then('SBC #5')
         .and_then('STA $0200'))

    def test_sprite_zero_augassign_x_minus_five(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).x -= 5')
         .has('LDA $0203')
         .and_then('SEC')
         .and_then('SBC #5')
         .and_then('STA $0203'))

    def test_sprite_zero_augassign_plus_two_inside_a_joystick_up(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'def joypad1_up():'
            '   get_sprite(0).y += 5')
         .has('NMI:')
         .and_then('BEQ EndUp')
         .and_then('LDA $0200')
         .and_then('CLC')
         .and_then('ADC #5')
         .and_then('STA $0200')
         .and_then('EndUp:')
         .and_then('.dw NMI')
         )

    def test_ppusprite_with_0(self):
        s = PPUSprite(0, Game())
        self.assertEquals(0x0200, s.y)
        self.assertEquals(0x0203, s.x)

    def test_ppusprite_with_1(self):
        s = PPUSprite(1, Game())
        self.assertEquals(0x0204, s.y)
        self.assertEquals(0x0207, s.x)

    def test_sprite_one_assign_100(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(1).y += 100')
         .has('LDA $0204')
         .and_then('CLC')
         .and_then('ADC #100')
         .and_then('STA $0204'))

    def test_show_gutomaia(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'gutomaia = "Guto Maia"\n'

            'def reset():'
            '  show(gutomaia, 0, 0)\n'
        )
            .has('.rsset $0000')
            .and_then('addressLow .rs 1')
            .and_then('addressHigh .rs 1')
            .and_then('posLow .rs 1')
            .and_then('posHigh .rs 1')
            .and_then('Show:')
            .and_then('LDA $2002')
            .and_then('LDA posHigh')
            .and_then('STA $2006')
            .and_then('LDA posLow')
            .and_then('STA $2006')
            .and_then('LDY #$00')
            .and_then('PrintLoop:')
            .and_then('LDA (addressLow), y')
            .and_then('CMP #$25')
            .and_then('BEQ PrintEnd')
            .and_then('STA $2007')
            .and_then('INY')
            .and_then('JMP PrintLoop')
            .and_then('PrintEnd:')
            .and_then('RTS')

            .and_then('RESET:')
            .and_then('LDA #LOW(gutomaia)')
            .and_then('STA addressLow')
            .and_then('LDA #HIGH(gutomaia)')
            .and_then('STA addressHigh')

            .and_then('LDA #$20')
            .and_then('STA posHigh')
            .and_then('LDA #$00')
            .and_then('STA posLow')
            .and_then('JSR Show')

            .and_then('LDA #%10010000')
            .and_then('STA $2000')
            .and_then('LDA #%00001000')
            .and_then('STA $2001')

            .and_then('NMI:')

            .and_then('LDA #00')
            .and_then('STA $2005')
            .and_then('STA $2005')

            .and_then('.bank 1')
            .and_then('gutomaia:')
            .and_then('.db $10,$1E,$1D,$18,$24,$16,$0A,$12,$0A,$25')
        )

    def test_show_guto(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'guto = "Guto"\n'

            'def reset():'
            '  show(guto, 0, 2)\n'
        )
            .has('.rsset $0000')
            .and_then('addressLow .rs 1')
            .and_then('addressHigh .rs 1')
            .and_then('posLow .rs 1')
            .and_then('posHigh .rs 1')
            .and_then('Show:')
            .and_then('LDA $2002')
            .and_then('LDA posHigh')
            .and_then('STA $2006')
            .and_then('LDA posLow')
            .and_then('STA $2006')
            .and_then('LDY #$00')
            .and_then('PrintLoop:')
            .and_then('LDA (addressLow), y')
            .and_then('CMP #$25')
            .and_then('BEQ PrintEnd')
            .and_then('STA $2007')
            .and_then('INY')
            .and_then('JMP PrintLoop')
            .and_then('PrintEnd:')
            .and_then('RTS')

            .and_then('RESET:')
            .and_then('LDA #LOW(guto)')
            .and_then('STA addressLow')
            .and_then('LDA #HIGH(guto)')
            .and_then('STA addressHigh')

            .and_then('LDA #$20')
            .and_then('STA posHigh')
            .and_then('LDA #$02')
            .and_then('STA posLow')
            .and_then('JSR Show')

            .and_then('guto:')
            .and_then('.db $10,$1E,$1D,$18,$25')
        )

    def test_show_guto_at_line_1_col_0(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'guto = "Guto"\n'

            'def reset():'
            '  show(guto, 1, 0)\n'
        )
            .and_then('RESET:')
            .and_then('LDA #LOW(guto)')
            .and_then('STA addressLow')
            .and_then('LDA #HIGH(guto)')
            .and_then('STA addressHigh')

            .and_then('LDA #$20')
            .and_then('STA posHigh')
            .and_then('LDA #$20')
            .and_then('STA posLow')
            .and_then('JSR Show')

            .and_then('guto:')
            .and_then('.db $10,$1E,$1D,$18,$25')
        )

    def test_show_guto_at_line_1_col_1(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'guto = "Guto"\n'

            'def reset():'
            '  show(guto, 1, 1)\n'
        )
            .and_then('RESET:')
            .and_then('LDA #LOW(guto)')
            .and_then('STA addressLow')
            .and_then('LDA #HIGH(guto)')
            .and_then('STA addressHigh')

            .and_then('LDA #$20')
            .and_then('STA posHigh')
            .and_then('LDA #$21')
            .and_then('STA posLow')
            .and_then('JSR Show')

            .and_then('guto:')
            .and_then('.db $10,$1E,$1D,$18,$25')
        )

    def test_load_palette_with_nes_array(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'palette = [0,1,2,3,4,5,6,7]\n'

            'load_palette(palette)\n'
        )
            .has('.bank 0')
            .and_then('LoadPalettes:')
            .and_then('LoadPalettesIntoPPU:')
            .and_then('LDA palette, x')
            .and_then('STA $2007')
            .and_then('INX')
            .and_then('CPX #$08')
            .and_then('palette:')

        )

    def test_load_palette_with_nes_array_2(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'
            'mypalette = [0,1,2,3,4,5,6,7]\n'

            'load_palette(mypalette)\n'
        )
            .has('.bank 0')
            .and_then('LoadPalettes:')
            .and_then('LoadPalettesIntoPPU:')
            .and_then('LDA mypalette, x')
            .and_then('STA $2007')
            .and_then('INX')
            .and_then('CPX #$08')
            .and_then('mypalette:')
        )

    def test_import_chr_player(self):
        self.path = 'fixtures/movingsprite/'
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'chrfile = import_chr("player.chr")\n'
        )
            .has('.bank 2')
            .and_then('.org $0000')
            .and_then('.incbin "player.chr"')
        )

    def test_string_hellow(self):
        (self.assert_asm_from(
            'hello = "world"'
        )
        )
        self.assertEquals(1, len(self.game._vars))
        self.assertTrue(isinstance(self.game._vars['hello'], NesString))
        self.assertEquals("world", self.game._vars['hello'])

    def test_import_chr_mario(self):
        self.path = 'fixtures/nerdynights/scrolling/'
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'chrfile = import_chr("mario.chr")\n'
        )
            .has('.bank 2')
            .and_then('.org $0000')
            .and_then('.incbin "mario.chr"')
        )

    def test_movingsprite(self):
        code = (
            'from pynes.bitbag import *\n'

            # 'import_chr("player.chr")\n'
            'palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,\n'
            '    0x0F, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59,\n'
            '    60, 61, 62, 63 ]\n'
            # 'sprite = define_sprite()\n'
            'px = rs(1)\n'
            'py = rs(1)\n'

            'def reset():\n'
            '    wait_vblank()\n'
            # '    clearmen()\n'
            '    wait_vblank()\n'
            # '    load_palette(palette)\n'
            # '    load_sprite(sprite)\n'

            'def joypad1_up():\n'
            '    global y\n'
            '    py += 1\n'

            'def joypad1_down():\n'
            '    global y\n'
            '    py -= 1\n'

            'def joypad1_left():\n'
            '     get_sprite(0).x += 1'
            # '    global x\n'
            # '    px -= 1\n'

            # 'def joypad1_right():\n'
            # '    global x\n'
            # '    px += 1\n'
        )

        game = compose(code)
        asm = game.to_asm()
        # self.assertEquals(1, len(game.bitpaks))
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
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'def reset():\n'
            '    wait_vblank()')
         .has('.bank 0')
         .and_then('.org $C000')
         .and_then('WAITVBLANK:')
         .and_then('RTS')
         .and_then('RESET:')
         .and_then('.bank 1')
         .and_then('.dw 0')
         .and_then('.dw RESET')
         .and_then('.dw 0')
         )
        self.assertTrue('.org $E000' not in self.asm)
        self.assertTrue('NMI:' not in self.asm)
        self.assertEquals(1, len(self.game.bitpaks))

    def test_wait_vblank_called_twice(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'def reset():\n'
            '    wait_vblank()\n'
            '    wait_vblank()')
         .has('.bank 0')
         .and_then('.org $C000'))

        self.assertEquals(1, len(self.game.bitpaks))
        # self.assertTrue('.bank 1' not in self.asm)
        self.assertTrue('.org $E000' not in self.asm)

    def test_palette_list_definition_from_00_to_04(self):
        (self.assert_asm_from(
            'palette = [0,1,2,3]')

         .has('.bank 1')
         .and_then('.org $E000')
         .and_then(
             'palette:\n'
             '  .db $00,$01,$02,$03')
         )

        self.assertEquals(1, len(self.game._vars))
        self.assertEquals([0, 1, 2, 3],
                          self.game.get_var('palette'))
        # self.assertTrue('.bank 0' not in self.asm)
        # self.assertTrue('.org $C000' not in self.asm)

    def test_palette_list_definition_from_00_to_0F(self):
        (self.assert_asm_from(
            'palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]')

         .has('.bank 1')
         .and_then('.org $E000')
         .and_then(
             'palette:\n'
             '  .db $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,'
             '$0E,$0F')
         )
        self.assertEquals(1, len(self.game._vars))
        self.assertEquals(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            self.game.get_var('palette'))
        self.assertTrue('.bank 0' not in self.asm)
        self.assertTrue('.org $C000' not in self.asm)

    def test_palette_list_definition_from_0F_to_00(self):
        (self.assert_asm_from(
            'palette = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]')
         .has('.bank 1')
         .and_then('.org $E000')
         .and_then(
             'palette:\n'
             '  .db $0F,$0E,$0D,$0C,$0B,$0A,$09,$08,$07,$06,$05,$04,$03,$02,'
             '$01,$00')
         )
        self.assertEquals(1, len(self.game._vars))
        self.assertEquals(
            [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
            self.game.get_var('palette'))
        self.assertTrue('.bank 0' not in self.asm)
        self.assertTrue('.org $C000' not in self.asm)

    def test_palette_list_definition_from_00_to_1F(self):
        (self.assert_asm_from('palette = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,'
                              '15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,'
                              '30,31]')
         .has('.bank 1')
         .and_then('.org $E000')
         .and_then(
             'palette:\n'
             '  .db $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,'
             '$0E,$0F\n'
             '  .db $10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$1A,$1B,$1C,$1D,'
             '$1E,$1F')
         )
        self.assertEquals(1, len(self.game._vars))
        self.assertEquals(range(32), self.game.get_var('palette'))
        # self.assertTrue('.bank 0' not in self.asm)
        self.assertTrue('.org $C000' not in self.asm)

    def test_define_sprite_with_x_128_y_64_and_tile_0(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'sprite = define_sprite(128, 64 ,0, 3)\n'
        )
            .has('.bank 1')
            .and_then(
                'sprite:\n'
                '  .db $40, $00, $03, $80')
        )

    def test_define_sprite_with_x_64_and_y_128_and_tile_1(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'sprite = define_sprite(64, 128, 1, 3)\n'
        )
            .has('.bank 1')
            .and_then(
                'sprite:\n'
                '  .db $80, $01, $03, $40')
        )

    def test_define_sprite_using_an_array(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
        )
            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_load_sprite_using_an_array(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 0)'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_plus_five_on_x_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 0)\n'

            'get_sprite(mario).x += 5'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0203')
            .and_then('CLC')
            .and_then('ADC #5')
            .and_then('STA $0203')
            .and_then('STA $020B')
            .and_then('CLC')
            .and_then('ADC #8')
            .and_then('STA $0207')
            .and_then('STA $020F')
            # TODO has not (CLC)
            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_plus_ten_on_x_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 1)\n'

            'get_sprite(mario).x += 10'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0204, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0207')
            .and_then('CLC')
            .and_then('ADC #10')
            .and_then('STA $0207')
            .and_then('STA $020F')
            .and_then('CLC')
            .and_then('ADC #8')
            .and_then('STA $020B')
            .and_then('STA $0213')

            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_plus_five_on_y_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 0)\n'

            'get_sprite(mario).y += 5'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0200')
            .and_then('CLC')
            .and_then('ADC #5')
            .and_then('STA $0200')
            .and_then('STA $0204')
            .and_then('CLC')
            .and_then('ADC #8')
            .and_then('STA $0208')
            .and_then('STA $020C')

            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_plus_10_on_y_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 1)\n'

            'get_sprite(mario).y += 10'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0204, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0204')
            .and_then('CLC')
            .and_then('ADC #10')
            .and_then('STA $0204')
            .and_then('STA $0208')
            .and_then('CLC')
            .and_then('ADC #8')
            .and_then('STA $020C')
            .and_then('STA $0210')

            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_minus_five_on_x_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 0)\n'

            'get_sprite(mario).x -= 5'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')
            .and_then('LDA $0207')
            .and_then('SEC')
            .and_then('SBC #5')
            .and_then('STA $020F')
            .and_then('STA $0207')
            .and_then('SEC')
            .and_then('SBC #8')
            .and_then('STA $020B')
            .and_then('STA $0203')
            # TODO has not (CLC)
            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_minus_ten_on_x_with_four_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 1)\n'

            'get_sprite(mario).x -= 10'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0204, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')
            .and_then('LDA $020B')
            .and_then('SEC')
            .and_then('SBC #10')
            .and_then('STA $0213')
            .and_then('STA $020B')
            .and_then('SEC')
            .and_then('SBC #8')
            .and_then('STA $020F')
            .and_then('STA $0207')
            # TODO has not (CLC)
            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_move_sprite_minus_five_on_x_with_eight_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [0,1,2,3,4,5,6,7], 0)\n'
            'load_sprite(mario, 0)\n'

            'get_sprite(mario).x -= 5'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #32')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0207')
            .and_then('SEC')
            .and_then('SBC #5')
            .and_then('STA $021F')
            .and_then('STA $0217')
            .and_then('STA $020F')
            .and_then('STA $0207')
            .and_then('SEC')
            .and_then('SBC #8')
            .and_then('STA $021B')
            .and_then('STA $0213')
            .and_then('STA $020B')
            .and_then('STA $0203')
            # TODO has not (CLC)
            .has('.bank 1')
            .and_then('mario:')
        )

    def test_move_sprite_minus_five_on_y_with_eight_tiles(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [0,1,2,3,4,5,6,7], 0)\n'
            'load_sprite(mario, 0)\n'

            'get_sprite(mario).x += 5'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #32')
            .and_then('BNE LoadSpritesIntoPPU')

            .and_then('LDA $0203')  # TODO $0207
            .and_then('CLC')
            .and_then('ADC #5')
            .and_then('STA $0203')
            .and_then('STA $020B')
            .and_then('STA $0213')
            .and_then('STA $021B')
            .and_then('CLC')
            .and_then('ADC #8')
            .and_then('STA $0207')
            .and_then('STA $020F')
            .and_then('STA $0217')
            .and_then('STA $021F')
            # TODO has not (CLC)
            .has('.bank 1')
            .and_then('mario:')
        )

    def test_load_sprite_using_an_array_in_slot_1(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'mario = define_sprite(128, 128, [50,51,52,53], 0)\n'
            'load_sprite(mario, 1)'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA mario, x')
            .and_then('STA $0204, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')

            .has('.bank 1')
            .and_then('mario:')
            .and_then('.db $80, $32, $00, $80')
            .and_then('.db $80, $33, $00, $88')
            .and_then('.db $88, $34, $00, $80')
            .and_then('.db $88, $35, $00, $88')
        )

    def test_load_sprite_twice_in_the_sequence(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'tinymario = define_sprite(108, 144, [50,51,52,53], 0)\n'
            'mario = define_sprite(128,128, [0, 1, 2, 3, 4, 5, 6, 7], 0)\n'

            'def reset():\n'
            '  load_sprite(tinymario, 0)\n'
            '  load_sprite(mario, 4)\n'
        )
            .has('.bank 0')
            .and_then('RESET:')
            .and_then('LoadSprites:')  # change to LoadMarioSprite
            .and_not_from_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA tinymario, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #16')
            .and_then('BNE LoadSpritesIntoPPU')
            .and_then('LoadSprites1:')  # change to #LoadTinyMarioSprite
            .and_then('LoadSpritesIntoPPU1:')
            .and_then('BNE LoadSpritesIntoPPU1')
            .and_then('InfiniteLoop:')

            .and_then('.bank 1')
            .and_then('.org $E000')
            .and_then('tinymario:')
            .and_then('mario:')
            .and_then('.org $FFFA')
            .and_then('.dw NMI')
            .and_then('.dw RESET')
        )

    def test_load_sprite(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'sprite = define_sprite(128, 64 ,0, 3)\n'

            'load_sprite(sprite, 0)'
        )
            .has('.bank 0')
            .and_then('LoadSprites:')
            .and_then('LDX #$00')
            .and_then('LoadSpritesIntoPPU:')
            .and_then('LDA sprite, x')
            .and_then('STA $0200, x')
            .and_then('INX')
            .and_then('CPX #4')  # TODO it should be 4
            .and_then('BNE LoadSpritesIntoPPU')
            .and_then('.bank 1')
            .and_then(
                'sprite:\n'
                '  .db $40, $00, $03, $80')
        )

    def test_flip_horizontal_sprite_zero(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).flip_horizontal()\n'
        )
            .has('.bank 0')
            .and_then('LDA $0202')
            .and_then('EOR #64')
            .and_then('STA $0202')
        )

    def test_flip_vertical_sprite_zero(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(0).flip_vertical()\n'
        )
            .has('.bank 0')
            .and_then('LDA $0202')
            .and_then('EOR #128')
            .and_then('STA $0202')
        )

    def test_flip_horizontal_sprite_one(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(1).flip_horizontal()\n'
        )
            .has('.bank 0')
            .and_then('LDA $0206')
            .and_then('EOR #64')
            .and_then('STA $0206')
        )

    def test_flip_vertical_sprite_one(self):
        (self.assert_asm_from(
            'from pynes.bitbag import *\n'

            'get_sprite(1).flip_vertical()\n'
        )
            .has('.bank 0')
            .and_then('LDA $0206')
            .and_then('EOR #128')
            .and_then('STA $0206')
        )

    def test_rs_with_x_and_y_with_size_1(self):
        code = (
            'from pynes.bitbag import *\n'
            'x = rs(1)\n'
            'y = rs(1)')
        game = compose(code)
        asm = game.to_asm()
        self.assertEquals(2, len(game._vars))
        self.assertEquals(1, game._vars['x'].size)
        self.assertEquals(1, game._vars['y'].size)
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        # self.assertTrue('.bank 1' not in asm)
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
        game = compose(code)
        asm = game.to_asm()
        self.assertEquals(7, len(game._vars))
        self.assertEquals(1, game._vars['scroll'].size)
        self.assertEquals(1, game._vars['nametable'].size)
        self.assertEquals(1, game._vars['columnLow'].size)
        self.assertEquals(1, game._vars['columnHigh'].size)
        self.assertEquals(1, game._vars['sourceLow'].size)
        self.assertEquals(1, game._vars['sourceHigh'].size)
        self.assertEquals(1, game._vars['columnNumber'].size)
        self.assertTrue('.bank 0' not in asm)
        self.assertTrue('.org $C000' not in asm)
        # self.assertTrue('.bank 1' not in asm)
        self.assertTrue('.org $E000' not in asm)
        self.assertTrue('.rsset $0000' in asm)
        self.assertTrue('scroll .rs 1' in asm)
        self.assertTrue('nametable .rs 1' in asm)
        self.assertTrue('columnLow .rs 1' in asm)
        self.assertTrue('columnHigh .rs 1' in asm)
        self.assertTrue('sourceLow .rs 1' in asm)
        self.assertTrue('sourceHigh .rs 1' in asm)
        self.assertTrue('columnNumber .rs 1' in asm)

    def test_undefined_def_raises_nameerror(self):
        code = (
            'from pynes.bitbag import *\n'

            'undefined_def()\n'
        )

        with self.assertRaises(NameError) as nm:
            compose(code)

        self.assertEquals("name 'undefined_def' is not defined",
                          nm.exception.message)

    def test_wait_vblank_raises_typeerror_when_called_with_args(self):
        code = (
            'from pynes.bitbag import *\n'

            'wait_vblank(1)'
        )

        with self.assertRaises(TypeError) as te:
            compose(code)

        self.assertEquals(
            'wait_vblank() takes exactly 1 argument (2 given)',
            te.exception.message)

    def test_load_palette_raises_typeerror_when_called_without_args(self):
        code = (
            'from pynes.bitbag import *\n'

            'load_palette()'
        )

        with self.assertRaises(TypeError) as te:
            compose(code)

        self.assertEquals(
            'load_palette() takes exactly 2 arguments (1 given)',
            te.exception.message)
