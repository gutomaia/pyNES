# -*- coding: utf-8 -*-

from ast import Num, List


class NesType:

    def __init__(self, size=1):
        self.instance_name = None
        self.is_used = False  # define if a var is used
        self.is_attrib = False  # define is assigned more than once
        self.size = size
        self.lineno = 0


class NesRs(NesType):

    def __init__(self, size=1):
        NesType.__init__(self, size)


class NesSprite(NesType):

    def __init__(self, x, y, tile, attrib, width=2):
        NesType.__init__(self)
        self.is_used = True
        self.x = x
        self.y = y
        self.tile = tile
        self.attrib = attrib
        self.width = width

    def __len__(self):
        print self.tile
        print dir(self.tile)
        print self.tile
        print self.tile.__class__
        print isinstance(self.tile, list)
        if isinstance(self.tile, List):
            return len(self.tile)
        return 1

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
            # TODO: assert list mod width == 0
            for t in self.tile:
                i = x % self.width
                j = x / self.width
                asmcode += ('  .db $%02X, $%02X, $%02X, $%02X\n' %
                            (
                                self.y + (j * 8),
                                t,
                                self.attrib,
                                self.x + (i * 8)
                            ))
                x += 1
            return asmcode


class NesArray(NesType, list, List):

    def __init__(self, elts):
        NesType.__init__(self)
        List.__init__(self, elts=elts)
        lst = [l.n if isinstance(l, Num) else l for l in elts]
        list.__init__(self, lst)
        self.is_used = True
        self.locked = False

    def to_asm(self):
        self.locked = True
        hexes = ["$%02X" % v for v in self]
        asm = ''
        length = (len(hexes) / 16)
        if len(hexes) % 16:
            length += 1
        for i in range(length):
            asm += '  .db ' + ','.join(hexes[i * 16:i * 16 + 16]) + '\n'
        if len(asm) > 0:
            return asm
        return False


class NesInt(int, Num, NesType):

    def __init__(self, number):
        int.__init__(self, number)
        Num.__init__(self, n=number)
        NesType.__init__(self)


class NesString(str, NesType):

    def __init__(self, string):
        str.__init__(self, string)
        NesType.__init__(self)
        self.locked = False

    def to_asm(self):
        s = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        start = 0
        bytes = [(s.index(c) + start) for c in self.upper()]
        bytes.append(0x25)  # TODO: EndString
        hexes = ["$%02X" % v for v in bytes]
        asm = ''
        length = (len(hexes) / 16)
        if len(hexes) % 16:
            length += 1
        for i in range(length):
            asm += '  .db ' + ','.join(hexes[i * 16:i * 16 + 16]) + '\n'
        if len(asm) > 0:
            return asm
        return False


class NesChrFile(NesType):

    def __init__(self, filename):
        self.filename = filename
