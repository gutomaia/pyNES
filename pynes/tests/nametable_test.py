# -*- coding: utf-8 -*-

import unittest

from pynes import nametable


class NametableTest(unittest.TestCase):

    def setUp(self):
        self.nt = nametable.load_nametable(
            'fixtures/nerdynights/scrolling/SMBlevel.bin')
        self.assertIsNotNone(self.nt)

    def test_length_nametable(self):
        length = nametable.length(self.nt)
        self.assertEquals(4, length)

    def test_get_nametable(self):
        return
        # length = nametable.get_nametable(1, self.nt)
        # self.assertEquals(4, length)
