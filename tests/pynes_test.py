# -*- coding: utf-8 -*-

import unittest
from binascii import a2b_hex, hexlify

from pynes.asm import nes_id
from pynes.asm import nes_get_header

import pynes.c6502

from os import remove
from os.path import exists

class PyNESTest(unittest.TestCase):

    def nes_header_test(self):
        self.assertEquals(
                nes_id(), 
                [0x4e, 0x45, 0x53, 0x1a]
            )

    def test_nes_get_header(self):
        header = nes_get_header(1,1,0,1)
        #first 4 bytes are the file id
        self.assertEquals(ord('N'), header[0])
        self.assertEquals(ord('E'), header[1])
        self.assertEquals(ord('S'), header[2])
        self.assertEquals(0x1a, header[3])
        #second 4 bites are the prg,chr and mapper definitions
        self.assertEquals(1, header[4]) #pgr
        self.assertEquals(1, header[5]) #chr
        self.assertEquals(1, header[6]) #mir
        self.assertEquals(0, header[7]) #map
        #now there is 8 bytes with 0
        for i in range(8):
            self.assertEquals(0, header[8+i])

    def test_write_bin_code(self):
        if exists('/tmp/target.nes'):
            remove('/tmp/target.nes')
        opcodes = nes_id()
        pynes.write_bin_code(opcodes, '/tmp/target.nes')
        f = open('/tmp/target.nes', 'rw')
        bin = f.read()
        f.close()
        expected = ''.join([chr(opcode) for opcode in opcodes])
        self.assertEquals(expected, bin)

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
