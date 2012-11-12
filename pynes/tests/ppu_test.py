import unittest

from pynes.bitbag import PPU

class PPUTest(unittest.TestCase):

    def setUp(self):
        self.ppu = PPU()

    def tearDown(self):
        self.ppu = None

    def test_ppu_init_with_nmi_disabled(self):
        #self.assertEquals(False, self.ppu.nmi_enable)
        self.assertEquals(0x0000, self.ppu.ctrl)
        self.ppu.nmi_enable(True)
        #self.assertEquals(True, self.ppu.nmi_enable)
        self.assertEquals(128, self.ppu.ctrl)
