# -*- coding: utf-8 -*-

class BitPak:

    def __call__(self):
        return None

    def procedure(self):
        return None

    def attribute(self):
        return None

class rs(BitPak):

    def __call__(self, size):
        return None

    def attribute(self):
        return None


class wait_vblank(BitPak):

    def __call__(self):
        return '  JSR WAITVBLANK\n'

    def procedure(self):
        return ('WAITVBLANK:\n'
          '  BIT $2002\n'
          '  BPL WAITVBLANK\n'
          '  RTS\n')

class import_sprite(BitPak):

    def __call__(self):
      return None

    def procedure(self):
      return None


class load_palette(BitPak):

    def  __call__(self, palette):
        return (
          'LoadPalettes:\n'
          '  LDA $2002             ; Reset PPU, start writing\n'
          '  LDA #$3F\n'
          '  STA $2006             ; High byte = $3F00\n'
          '  LDA #$00\n'
          '  STA $2006             ; Low byte = $3F00\n'
          '  LDX #$00\n'
          'LoadPalettesIntoPPU:\n'
          '  LDA palette, x\n'
          '  STA $2007\n'
          '  INX\n'
          '  CPX #$20                  ; Hex 20 = 32 decimal\n'
          '  BNE LoadPalettesIntoPPU\n'
        )

    def procedure(self):
        return None