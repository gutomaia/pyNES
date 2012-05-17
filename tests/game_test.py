# -*- coding: utf-8 -*-

import unittest
from binascii import a2b_hex, hexlify

import pynes
import pynes.opcodes

class GameTest(unittest.TestCase):

    def nes_header_test(self):
        return
        self.assertEquals(
                pynes.nes_header(), 
                [0x4e, 0x45, 0x53, 0xa1]
            )

    def pgr_chr_mappers_test(self):
        return
        self.assertEquals(
                pynes.pgr_chr_mappers(), 
                [0x01, 0x01, 0x01, 0x00]
            )

    def game_test(self):
        return
        game = pynes.Game()
        game.compile()
