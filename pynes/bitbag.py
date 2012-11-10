# -*- coding: utf-8 -*-

from re import match

from nes_types import NesRs, NesArray

class Joypad():

    def __init__(self, player_num, cart):
        assert player_num == 1 or player_num == 2
        self.num = player_num
        if player_num == 1:
            self.port = '$4016'
        else:
            self.port = '$4017'
        self.cart = cart
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
            if index in self.cart._asm_chunks:
                asm_code += self.cart._asm_chunks[index]
            asm_code += "End" + tag + ":\n"
            yield asm_code

    @property
    def is_used(self):
        for status in self.cart._asm_chunks:
            if match('^joypad[12]_(a|b|select|start|up|down|left|right)', status):
                return True
        return False

    def to_asm(self):
        if self.is_used:
            return '\n'.join(self)
        return ''

class BitPak:

    def __init__(self, cart):
        self.cart = cart
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

    def __init__(self, cart):
        BitPak.__init__(self, cart)

    def __call__(self, size):
        return NesRs(size)

class HardSprite:

    def __init__(self, pos):
      address = 0x0200 + (4 * pos)
      self.y = address
      self.x = address + 3


class get_sprite(BitPak):

    def __init__(self, cart):
        BitPak.__init__(self, cart)

    def __call__(self, position):
        return HardSprite(position)


class wait_vblank(BitPak):

    def __init__(self, cart):
        BitPak.__init__(self, cart)

    def __call__(self):
        return None

    def asm(self):
        return '  JSR WAITVBLANK\n'

    def procedure(self):
        return ('WAITVBLANK:\n'
          '  BIT $2002\n'
          '  BPL WAITVBLANK\n'
          '  RTS\n')

class clearmen(BitPak):

    def __init__(self, cart):
        BitPak.__init__(self, cart)

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

    def __init__(self, cart):
        BitPak.__init__(self, cart)

    def __call__(self, filename="a"):
      return ""

class define_sprite(BitPak):
    pass
    #(y, tile, $03, x)
    #sprite:
    #.db $80, $00, $03, $80; Y pos, tile id, attributes, X pos

class load_palette(BitPak):

    def __init__(self, cart):
        BitPak.__init__(self, cart)

    def  __call__(self, palette):
        print palette
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