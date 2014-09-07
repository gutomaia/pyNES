import unittest

from pynes.game import PPU


class PPUTest(unittest.TestCase):

    def setUp(self):
        self.ppu = PPU()

    def tearDown(self):
        self.ppu = None

    def test_ppu_toogle_nmi(self):
        self.assertEquals(0b00000000, self.ppu.ctrl)
        self.ppu.nmi_enable = True
        self.assertEquals(0b10000000, self.ppu.ctrl)
        self.assertEquals(True, self.ppu.nmi_enable)
        self.ppu.nmi_enable = False
        self.assertEquals(0b00000000, self.ppu.ctrl)
        self.assertEquals(False, self.ppu.nmi_enable)

    def test_ppu_toogle_sprite_table(self):
        self.assertEquals(0b00000000, self.ppu.ctrl)
        self.ppu.sprite_pattern_table = 1
        self.assertEquals(0b00001000, self.ppu.ctrl)
        self.ppu.sprite_pattern_table = 0
        self.assertEquals(0b00000000, self.ppu.ctrl)

    def test_ppu_toogle_background_table(self):
        self.assertEquals(0b00000000, self.ppu.ctrl)
        self.ppu.background_pattern_table = 1
        self.assertEquals(0b00010000, self.ppu.ctrl)
        self.ppu.background_pattern_table = 0
        self.assertEquals(0b00000000, self.ppu.ctrl)

    def test_ppu_toogle_sprite(self):
        self.assertEquals(0b00000000, self.ppu.mask)
        self.ppu.sprite_enable = True
        self.assertEquals(0b00010000, self.ppu.mask)
        self.assertEquals(True, self.ppu.sprite_enable)
        self.ppu.sprite_enable = False
        self.assertEquals(0b00000000, self.ppu.mask)
        self.assertEquals(False, self.ppu.sprite_enable)

    def test_ppu_toogle_background(self):
        self.assertEquals(0b00000000, self.ppu.mask)
        self.ppu.background_enable = True
        self.assertEquals(0b00001000, self.ppu.mask)
        self.assertEquals(True, self.ppu.background_enable)
        self.ppu.background_enable = False
        self.assertEquals(0b00000000, self.ppu.mask)
        self.assertEquals(False, self.ppu.background_enable)

    def test_ppu_toogle_background2(self):
        self.assertEquals(0b00000000, self.ppu.ctrl)
        self.assertEquals(0b00000000, self.ppu.mask)
        self.ppu.nmi_enable = True
        self.ppu.sprite_enable = True
        self.assertEquals(0b10000000, self.ppu.ctrl)
        self.assertEquals(True, self.ppu.nmi_enable)
        self.assertEquals(0b00010000, self.ppu.mask)
        self.assertEquals(True, self.ppu.sprite_enable)
