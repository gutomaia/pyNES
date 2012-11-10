# -*- coding: utf-8 -*-

class NesType:

    def __init__(self):
        self.instance_name = None


class NesRs(NesType):

    def __init__(self, size):
        NesType.__init__(self)
        self.size = size

class NesSprite(NesType):

    def __init__(self, x, y, tile, attrib):
        NesType.__init__(self)
        self.x = x
        self.y = y
        self.tile = tile
        self.attrib = attrib

    def to_asm(self):

        return (
            '  .db $%02x, $%02x, $%02x, $%02x' % 
            (
                self.y,
                self.tile,
                self.attrib,
                self.x
            ))


class NesArray(NesType):

    def __init__(self, lst):
        self.value = []
        for l in lst:
            self.value.append(l.n)

    def list(self):
        return self.value

    def to_asm(self):
        hexes = ["$%02X" % v for v in self.value]
        asm = ''
        length = (len(hexes) / 16)
        if len(hexes) % 16:
            length += 1
        for i in range(length):
            asm += '  .db ' + ','.join(hexes[i*16:i*16+16]) + '\n'
        if len(asm) > 0:
            return asm
        return False

class NesChrFile(NesType):

    def __init__(self, filename):
        self.filename = filename