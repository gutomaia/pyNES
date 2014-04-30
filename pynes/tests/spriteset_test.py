import unittest


from pynes.sprite import SpriteSet


class SpriteTest(unittest.TestCase):

    def __init__(self, testcase_name):
        unittest.TestCase.__init__(self, testcase_name)
        f = open('fixtures/nerdynights/scrolling/mario.chr', 'rb')
        content = f.read()
        self.bin = [ord(c) for c in content]

        self.mario1 = [
            [0, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 3, 3, 3, 2, 2],
            [0, 0, 3, 2, 2, 3, 2, 2],
            [0, 0, 3, 2, 2, 3, 3, 2],
            [0, 3, 3, 2, 2, 3, 3, 2]
        ]

        self.mario2 = [
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 2, 0, 0, 0, 0, 0],
            [1, 2, 2, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0, 0],
            [3, 2, 2, 2, 0, 0, 0, 0],
            [3, 3, 2, 2, 2, 2, 0, 0],
            [2, 2, 2, 2, 2, 2, 2, 0],
            [2, 2, 3, 2, 2, 2, 2, 0]
        ]

    def test_spriteset(self):
        sprites = SpriteSet('fixtures/nerdynights/scrolling/mario.chr')
        self.assertEquals(self.bin, sprites.sprs)
        self.assertEquals(self.mario1, sprites.get(0))
        self.assertEquals(self.mario2, sprites.get(1))

        self.assertEquals(0, sprites.has_sprite(self.mario1))
        self.assertEquals(1, sprites.has_sprite(self.mario2))
