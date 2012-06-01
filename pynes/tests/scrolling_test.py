# -*- coding: utf-8 -*-

import unittest

import pynes
from pynes.compiler import lexical, syntax, semantic

class ScrollingTest(unittest.TestCase):

    def test_partial_block(self):
        example = '''
                SEI          ; disable IRQs
                CLD          ; disable decimal mode
                LDX #$40
                STX $4017    ; disable APU frame IRQ
                LDX #$FF
                TXS          ; Set up stack
                INX          ; now X = 0
                STX $2000    ; disable NMI
                STX $2001    ; disable rendering
                STX $4010    ; disable DMC IRQs'''
        tokens = lexical(example)
        ast = syntax(tokens)
        opcodes = semantic(ast)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        f = open('fixtures/nesasm/scrolling/scrolling5.nes', 'rb')
        content = f.read()
        self.assertTrue(bin in content)

    def test_ines_functions(self):
        example = '''
            .inesprg 1   ; 1x 16KB PRG code
            .ineschr 1   ; 1x  8KB CHR data
            .inesmap 0   ; mapper 0 = NROM, no bank swapping
            .inesmir 1   ; VERT mirroring for HORIZ scrolling
            '''
        tokens = lexical(example)

    def test_bank_functions(self):
        example = '''
            .bank 1
            .org $E000
            palette:
            .db $22,$29,$1A,$0F,  $22,$36,$17,$0F,  $22,$30,$21,$0F,  $22,$27,$17,$0F   ;;background palette
            .db $22,$16,$27,$18,  $22,$1A,$30,$27,  $22,$16,$30,$27,  $22,$0F,$36,$17   ;;sprite palette
            '''