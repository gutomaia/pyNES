# -*- coding: utf-8 -*-

from ast import Num, List


class NesType(object):

    def __init__(self, *args, **kw):
        self.instance_name = None
        self.is_used = False  # define if a var is used
        self.is_attrib = False  # define is assigned more than once
        if 'size' in kw:
            self.size = kw['size']
        else:
            self.size = 1
        self.lineno = 0


class NesRs(NesType):

    def __init__(self, size=1):
        super(NesRs, self).__init__(size=size)


class NesSprite(NesType):

    def __init__(self, x, y, tile, attrib, width=2):
        super(NesSprite, self).__init__()
        self.is_used = True
        self.x = x
        self.y = y
        self.tile = tile
        self.attrib = attrib
        self.width = width

    def __len__(self):
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


class NesArray(NesType, List):

    def __init__(self, elts):
        super(NesArray, self).__init__(elts=elts)
        self.lst = [l.n if isinstance(l, Num) else l for l in elts]
        # list.__init__(self, lst)
        self.is_used = True
        self.locked = False

    def __eq__(self, other):
        if isinstance(other, list):
            return other == self.lst

    def __len__(self):
        return len(self.lst)

    def __iter__(self):
        return iter(self.lst)

    def to_asm(self):
        self.locked = True
        hexes = ["$%02X" % v for v in self.lst]
        asm = ''
        length = (len(hexes) / 16)
        if len(hexes) % 16:
            length += 1
        for i in range(length):
            asm += '  .db ' + ','.join(hexes[i * 16:i * 16 + 16]) + '\n'
        if len(asm) > 0:
            return asm
        return False


class NesInt(int, NesType):

    def __init__(self, number):
        super(NesInt, self).__init__(number)


class NesString(str, NesType):

    def __init__(self, string):
        super(NesString, self).__init__()
        str.__init__(self, string)
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
        super(NesChrFile, self).__init__()
        self.filename = filename
