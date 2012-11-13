# -*- coding: utf-8 -*-

from re import match

from nes_types import NesRs, NesArray, NesSprite, NesString, NesChrFile

class PPU():

    ctrl = 0x0000
    mask = 0x0000

    _sprite_enabled = False

    def nmi_enable(self, value):
        if value:
            self.ctrl = self.ctrl | 0b10000000
        else:
            self.ctrl = self.ctrl & 0b01111111

    def sprite_enable(self, value):
        if value:
            self.mask = self.mask | 0b00010000
        else:
            self.mask = self.mask & 0b11101111

    def init(self):
        asm = ('  LDA #%d\n' #TODO format binary
          '  STA $2000\n'    #TODO also put comments about bits
          '  LDA #%d\n'
          '  STA $2001\n') % (self.ctrl, self.mask)
        return asm

class Joypad():

    def __init__(self, player_num, game):
        assert player_num == 1 or player_num == 2
        self.num = player_num
        if player_num == 1:
            self.port = '$4016'
        else:
            self.port = '$4017'
        self.game = game
        self.actions = ['a', 'b', 'select', 'start', 
          'up', 'down', 'left', 'right']

    def __iter__(self):
        for action in self.actions:
            tag = action.capitalize()
            asm_code = (
                "JoyPad" + str(self.num) + tag + ":\n"
                "  LDA " + self.port + "\n"
                "  AND #%00000001\n"
                "  BEQ End" + tag +"\n"
            )
            index = 'joypad' + str(self.num) + '_' + action
            if index in self.game._asm_chunks:
                asm_code += self.game._asm_chunks[index]
            asm_code += "End" + tag + ":\n"
            yield asm_code

    def init(self):
        return ('StartInput:\n' 
            '  LDA #$01\n'
            '  STA $4016\n'
            '  LDA #$00\n'
            '  STA $4016\n')

    @property
    def is_used(self):
        for status in self.game._asm_chunks:
            if match('^joypad[12]_(a|b|select|start|up|down|left|right)', status):
                return True
        return False

    def to_asm(self):
        if self.is_used:
            return '\n'.join(self)
        return ''

class BitPak:

    def __init__(self, game):
        self.game = game
        self.assigned = None


    def __call__(self):
        return None

    def asm(self):
        return ''

    def procedure(self):
        return None

    def attribute(self):
        return ''

    def assigned_to(self, assigned):
        self.assigned = assigned

class rs(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def __call__(self, size):
        return NesRs(size)

#Change to PPUSprite
class HardSprite:

    def __init__(self, pos):
      address = 0x0200 + (4 * pos)
      self.y = address
      self.x = address + 3


class get_sprite(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def __call__(self, position):
        return HardSprite(position)


class wait_vblank(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def __call__(self):
        return None

    def asm(self):
        return '  JSR WAITVBLANK\n'

    def procedure(self):
        return ('WAITVBLANK:\n'
          '  BIT $2002\n'
          '  BPL WAITVBLANK\n'
          '  RTS\n')

class clearmem(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def asm(self):
        return (
          'CLEARMEM:\n'
          '  LDA #$00\n'
          '  STA $0000, x\n'
          '  STA $0100, x\n'
          '  STA $0200, x\n'
          '  STA $0400, x\n'
          '  STA $0500, x\n'
          '  STA $0600, x\n'
          '  STA $0700, x\n'
          '  LDA #$FE\n'
          '  STA $0300, x\n'
          '  INX\n'
          '  BNE CLEARMEM\n'
        )


class import_chr(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def __call__(self, string):
        assert isinstance(string, NesString)
        return NesChrFile(string.value)

class define_sprite(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def  __call__(self, x, y, tile, attrib=0x80):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(tile, int) or isinstance(tile, NesArray)
        return NesSprite(x, y, tile, attrib)


class load_palette(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def  __call__(self, palette):
        assert isinstance(palette, NesArray)
        self.palette = palette
        return None

    def asm(self):

        asmcode = (
          'LoadPalettes:\n'
          '  LDA $2002             ; Reset PPU, start writing\n'
          '  LDA #$3F\n'
          '  STA $2006             ; High byte = $3F00\n'
          '  LDA #$00\n'
          '  STA $2006             ; Low byte = $3F00\n'
          '  LDX #$00\n'
          'LoadPalettesIntoPPU:\n'
          '  LDA %s, x\n'
          '  STA $2007\n'
          '  INX\n' ) % self.palette.instance_name
        asmcode += '  CPX #$%02x\n' % len(self.palette.list())
        asmcode += '  BNE LoadPalettesIntoPPU\n'
        return asmcode


class load_sprite(BitPak):

    def __init__(self, cart):
        BitPak.__init__(self, cart)
        self.game.has_nmi = True
        self.game.ppu.sprite_enable(True)
        self.game.ppu.nmi_enable(True)

    def  __call__(self, sprite, ppu_pos):
        assert isinstance(sprite, NesSprite)
        self.sprite = sprite
        self.pos = ppu_pos
        #TODO return an HardwareSprite
        return None

    def  asm(self):
        size = len(self.sprite)

        asmcode = (
          'LoadSprites:\n'
          '  LDX #$00\n'
          'LoadSpritesIntoPPU:\n'
          '  LDA %s, x\n'
          '  STA $0200, x\n'
          '  INX\n'
          '  CPX #%d\n'
          '  BNE LoadSpritesIntoPPU\n'
        ) % (self.sprite.instance_name, size * 4)
        return asmcode
