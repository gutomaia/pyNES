class Bank(object):
    def __init__(self, org):
        self.org = org

    def asm(self):
        line = '.org $%04X' % self.org
        return [line]


class Game(object):

    def __init__(self, symbol_table=None):
        mapper = 1
        self.header = '; Build with pyNES'

        self._inesprg = 1
        self._ineschr = 1
        self._inesmap = 0
        self._inesmir = 1

        self.banks = {}
        self.banks[0] = Bank(0xC000)
        self.banks[1] = Bank(0xE000)
        self.banks[2] = Bank(0x0000)

        if not symbol_table:
            self.symbol_table = {}
        else:
            self.symbol_table = symbol_table

    def directive(self, d, arg):
        return '.%s %s' % (d, arg)

    def __getattr__(self, a):
        attr = '_%s' % a
        if hasattr(self, attr):
            value = getattr(self, attr)
            return self.directive(a, value)

    def rsset(self):
        output = []
        for k, v in self.symbol_table.iteritems():
            if v['type'] == 'int':
                output.append('%s .rs 1' % k)
        if output:
            output.insert(0, '.rsset $0000')

        return output

    def ines_header(self):
        return [
            self.inesprg,
            self.ineschr,
            self.inesmap,
            self.inesmir,
        ]

    def asm(self):
        lines = []
        lines.append(self.header)
        lines.extend(self.ines_header())
        lines.extend(self.rsset())

        for i, b in self.banks.iteritems():
            lines.append(self.directive('bank', i))
            lines.extend(b.asm())
        return '\n'.join(lines)
