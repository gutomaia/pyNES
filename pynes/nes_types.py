# -*- coding: utf-8 -*-

class NesType:

    def __init__(self):
        self.instance_name = None


class NesRs(NesType):

    def __init__(self, size):
        self.size = size

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
        print asm
        if len(asm) > 0:
            return asm
        return False
