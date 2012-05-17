import unittest

from pynes.compiler import t_zeropage, t_address, t_separator

class CompilerTest(unittest.TestCase):

    def setUp(self):
        self.zeropage = dict(
            type = 'T_ADDRESS',
            value = '$00'
        )
        self.address10 = dict(
            type = 'T_ADDRESS',
            value = '$1234'
        )
        self.separator = dict(
            type = 'T_SEPARATOR',
            value = ','
        )

    def test_t_zeropage(self):
        self.assertTrue(t_zeropage([self.zeropage],0))

    def test_t_address(self):
        self.assertTrue(t_address([self.address10],0))

    def test_t_separator(self):
        self.assertTrue(t_separator([self.separator],0))