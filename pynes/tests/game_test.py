# -*- coding: utf-8 -*-
import unittest
from pynes.game import Game

class GameTest(unittest.TestCase):

    def test_bank_0(self):
        game = Game()
        actual = game.banks[0].asm()
        expected = ['.org $C000']
        self.assertEquals(actual, expected)

    def test_bank_1(self):
        game = Game()
        actual = game.banks[1].asm()
        expected = ['.org $E000']
        self.assertEquals(actual, expected)

    def test_bank_2(self):
        game = Game()
        actual = game.banks[2].asm()
        expected = ['.org $0000']
        self.assertEquals(actual, expected)


    def test_game(self):
        game = Game()

        actual = game.asm()

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

