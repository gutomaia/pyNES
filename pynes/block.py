# -*- coding: utf-8 -*-

class AsmBlock(object):


    def __init__ (self, *args):
        # if len(args) > 1:
        #     instructions = list(args);
        #     for a in list(args):
        #         if type(a).__name__ == 'InstructionProxy':
        #             print a

        #     a = instructions[0]

        self.instructions = list(args)

    def is_Instruction(self, obj):
        return type(obj).__name__ == 'Instruction'

    def is_InstructionProxy(self, obj):
        return type(obj).__name__ == 'InstructionProxy'


    def __add__(self, other):

        if self.is_InstructionProxy(self.instructions[-1]) and isinstance(other, int):
            other = self.instructions[-1](other)
            self.instructions[-1] = other
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
        code = [str(a)+'\n' for a in self.instructions ]
        return ''.join(code)
