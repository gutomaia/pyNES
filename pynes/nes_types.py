# -*- coding: utf-8 -*-

class NesType:

    def __init__(self):
        pass

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
        for i in range(len(hexes) / 16):
            asm += '  .db ' + ','.join(hexes[i*16:i*16+16]) + '\n'
        if len(asm) > 0:
            return asm
        return False
