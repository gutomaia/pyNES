# -*- coding: utf-8 -*-

class NesType:

    def __init__(self):
        self.instance_name = None


class NesRs(NesType):

    def __init__(self, size):
        NesType.__init__(self)
        self.size = size

class NesSprite(NesType):

    def __init__(self, x, y, tile, attrib, width = 2):
        NesType.__init__(self)
        self.x = x
        self.y = y
        self.tile = tile
        self.attrib = attrib
        self.width = width

    def __len__(self):
        if isinstance(self.tile, int):
            return 1
        else:
            return len(self.tile)

    def to_asm(self):
        if isinstance(self.tile, int):
            return (
                '  .db $%02X, $%02X, $%02X, $%02X' %
                (
                    self.y,
                    self.tile,
                    self.attrib,
                    self.x
                ))
        else:
            asmcode = ''
            x = 0
            #TODO: assert list mod width == 0
            for t in self.tile:
                i = x % self.width
                j = x / self.width
                asmcode += ('  .db $%02X, $%02X, $%02X, $%02X\n' %
                (
                    self.y + (j*8),
                    t,
                    self.attrib,
                    self.x + (i*8)
                ))
                x += 1
            return asmcode


class NesArray(NesType, list):

    def __init__(self, lst):
        list.__init__(self, [l.n for l in lst])
        self.locked = False

    def to_asm(self):
        hexes = ["$%02X" % v for v in self]
        asm = ''
        length = (len(hexes) / 16)
        if len(hexes) % 16:
            length += 1
        for i in range(length):
            asm += '  .db ' + ','.join(hexes[i*16:i*16+16]) + '\n'
        if len(asm) > 0:
            return asm
        return False

class NesString(NesType): #Make it extends Array

    def __init__(self, string):
        self.value = string


class NesChrFile(NesType):

    def __init__(self, filename):
        self.filename = filename