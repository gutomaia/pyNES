# -*- coding: utf-8 -*-
class AsmBlock(object):

    def __init__(self, *args):
        self.instructions = []
        for i in list(args):
            if type(i).__name__ == 'InstructionProxy' and i.is_single():
                self.instructions.append(i())
            elif isinstance(i, int):
                self.instructions[-1] += i
            else:
                self.instructions.append(i)

    def is_Instruction(self, obj):
        return type(obj).__name__ == 'Instruction'

    def is_InstructionProxy(self, obj):
        return type(obj).__name__ == 'InstructionProxy'

    def __add__(self, other):
        if isinstance(other, AsmBlock):
            return AsmBlock(self, other)
        elif self.is_InstructionProxy(self.last()) and self.last().is_valid_address_mode_argument(other):
            self.instructions[-1] = self.instructions[-1](other)
        elif self.is_InstructionProxy(other) and other.is_single():
            self.instructions.append(other())
        elif self.is_InstructionProxy(other) or self.is_Instruction(other):
            self.instructions.append(other)
        return self

    def last(self):
        return self.get(-1)

    def __len__(self):
        return len(self.instructions)

    def size(self):
        return 0

    def get(self, index):
        return self.instructions[index]

    def __str__(self):
        code = ''
        for i in self.instructions:
            if isinstance(i, AsmBlock):
                code += str(i)
            else:
                code += str(i)+'\n'
        return code


class MemoryAddress(object):

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol
