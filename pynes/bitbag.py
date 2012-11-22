# -*- coding: utf-8 -*-

from re import match

from pynes.nes_types import NesRs, NesArray, NesSprite, NesString, NesChrFile

from pynes.game import PPUSprite

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

    def __call__(self, sprite):
        return PPUSprite(sprite, self.game)


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

class show(BitPak):

    def __init__(self, game):
        BitPak.__init__(self, game)

    def  __call__(self, string, x, y):
        string.is_used = True

    def asm(self):
        asmcode = (
            "  LDA #LOW(gutomaia)\n"
            "  STA addressLow\n"
            "  LDA #HIGH(gutomaia)\n"
            "  STA addressHigh\n"
            "  LDA #$20\n"
            "  STA posHigh\n"
            "  LDA #$40\n"
            "  STA posLow\n"
            "  JSR Print\n"
          )
        return asmcode

    def procedure(self):
        asmcode = (
          "Print:\n"
          "  LDA $2002\n"
          "  LDA posHigh\n"
          "  STA $2006\n"
          "  LDA posLow\n"
          "  STA $2006\n"
          "  LDY #$00\n"
          "PrintLoop:\n"
          "  LDA (addressLow), y\n"
          "  CMP #$25\n"
          "  BEQ PrintEnd\n"
          "  STA $2007\n"
          "  INY\n"
          "  JMP PrintLoop\n"
          "PrintEnd:\n"
          "  RTS\n"
          )
        return asmcode


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
        assert ppu_pos < 64
        self.sprite = sprite
        self.start_address = 0x0200 + (ppu_pos * 4)
        self.sprite.ppu_address = ppu_pos
        return None

    def  asm(self):
        size = len(self.sprite)
        load_sprites = self.game.get_label_for('LoadSprites')
        load_sprites_into_PPU = self.game.get_label_for('LoadSpritesIntoPPU')
        '''
        Proposal
        with asm(self.game) as a:
            a.label('LoadSprites')
            a.ldx = 0
            a.lda = ('LoadSpritesIntoPPU', a.x)
            a.sta = (self.start_address, a.x)
            a.inx()
            a.cpx(size * 4)
            bne('LoadSpritesIntoPPU')
        '''
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
