# -*- coding: utf-8 -*-

from re import match

from nes_types import NesRs, NesArray, NesSprite, NesString, NesChrFile

from game import PPUSprite

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

class get_sprite(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def __call__(self, position):
        return PPUSprite(position)


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
        return NesChrFile(string)

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
        asmcode += '  CPX #$%02x\n' % len(self.palette)
        asmcode += '  BNE LoadPalettesIntoPPU\n'
        return asmcode


class load_sprite(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)
        self.game.has_nmi = True
        self.game.ppu.sprite_enable(True)
        self.game.ppu.nmi_enable(True)

    def  __call__(self, sprite, ppu_pos):
        assert isinstance(sprite, NesSprite)
        self.sprite = sprite
        self.start_address = 0x0200 + (ppu_pos * 4)
        return None

    def  asm(self):
        size = len(self.sprite)
        load_sprites = self.game.get_label_for('LoadSprites')
        load_sprites_into_PPU = self.game.get_label_for('LoadSpritesIntoPPU')
        asmcode = (
          '%s:\n'
          '  LDX #$00\n'
          '%s:\n'
          '  LDA %s, x\n'
          '  STA $%04X, x\n'
          '  INX\n'
          '  CPX #%d\n'
          '  BNE %s\n'
        ) % (load_sprites,
            load_sprites_into_PPU,
            self.sprite.instance_name,
            self.start_address,
            size * 4,
            load_sprites_into_PPU)
        return asmcode
