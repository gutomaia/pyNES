# -*- coding: utf-8 -*-

class AsmBlock(object):


    def __init__ (self, *args):
        if len(args) > 1:
            instructions = list(args);
            for a in list(args):
                if type(a).__name__ == 'InstructionProxy':
                    print a

            a = instructions[0]

        self.instructions = list(args)


    def __add__(self, other):
        if isinstance(other, int):
            self.instructions[-1] += other
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
