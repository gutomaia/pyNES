# -*- coding: utf-8 -*-
import unittest
from pynes.game import Game, NESPacking
from collections import OrderedDict

class NESPackingTest(unittest.TestCase):

    def test_bank_0(self):
        packing = NESPacking()
        actual = packing.banks[0].asm()
        expected = ['.org $C000']
        self.assertEquals(actual, expected)

    def test_bank_1(self):
        packing = NESPacking()
        actual = packing.banks[1].asm()
        expected = ['.org $E000']
        self.assertEquals(actual, expected)

    def test_bank_2(self):
        packing = NESPacking()
        actual = packing.banks[2].asm()
        expected = ['.org $0000']
        self.assertEquals(actual, expected)


    def test_game(self):
        packing = NESPacking()

        actual = packing.asm()

        expected = """; Build with pyNES
.inesprg 1
.ineschr 1
.inesmap 0
.inesmir 1
.bank 0
.org $C000
.bank 1
.org $E000
.bank 2
.org $0000"""

        self.assertEquals(actual, expected)

    def test_game_with_int_a_variable(self):
        symbol_table = {
            'a': {
                'type': 'int',
                'assigns': 2
            }
        }
        packing = NESPacking(game=Game(symbol_table=symbol_table))
        actual = packing.rsset()

        expected = ['.rsset $0000', 'a .rs 1']
        self.assertEquals(actual, expected)

        for e in expected:
            self.assertIn(e, packing.asm())


    def test_game_with_int_scroll_variable(self):
        symbol_table = OrderedDict()
        integer = {'type': 'int', 'assigns': 2}
        symbol_table['scroll'] = integer
        symbol_table['nametable'] = integer
        symbol_table['columnLow'] = integer
        symbol_table['columnHigh'] = integer
        symbol_table['sourceLow'] = integer
        symbol_table['sourceHigh'] = integer
        symbol_table['columnNumber'] = integer

        packing = NESPacking(game=Game(symbol_table=symbol_table))
        actual = packing.rsset()

        expected = ['.rsset $0000',
            'scroll .rs 1',
            'nametable .rs 1',
            'columnLow .rs 1',
            'columnHigh .rs 1',
            'sourceLow .rs 1',
            'sourceHigh .rs 1',
            'columnNumber .rs 1']

        self.assertEquals(actual, expected)

        for e in expected:
            self.assertIn(e, packing.asm())
