# -*- coding: utf-8 -*-

class AsmBlock(object):


    def __init__ (self, *args):
        self.instructions = []
        for i in list(args):
            print type(i)
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
        if self.is_InstructionProxy(self.instructions[-1]) and self.instructions[-1].is_valid_address_mode_argument(other):
            other = self.instructions[-1](other)
            self.instructions[-1] = other
        elif self.is_InstructionProxy(other) and other.is_single():
            self.instructions.append(other())
        elif self.is_InstructionProxy(other):
            self.instructions.append(other)
        elif self.is_Instruction(other):
            self.instructions.append(other)
        return self

    def last_is_proxy(self):
        pass

    def __len__(self):
        return len(self.instructions)

    def get(self, index):
        return self.instructions[index]

    def last(self):
        return self.get(-1)

    def __str__(self):
        code = [str(a)+'\n' for a in self.instructions]
        return ''.join(code)
