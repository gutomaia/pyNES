
from asm import generate_ines_header

class Cartridge:

    def __init__(self):
        self.banks = {}
        self.bank_id = 0
        self.pc = 0

    def set_iNES_prg(self, inespgr):
        self.inespgr = inespgr

    def set_iNES_chr(self, ineschr):
        self.ineschr = ineschr

    def set_iNES_map(self, inesmap):
        self.inesmap = inesmap

    def set_iNES_mir(self, inesmir):
        self.inesmir = inesmir

    def set_bank_id(self, id):
        if id not in self.banks:
            self.banks[id] = dict(code=[], start=None, size=(1024*8))
        self.bank_id = id

    def set_org(self, org):
        if self.bank_id not in self.banks:
            self.set_bank_id(self.bank_id)
        if not self.banks[self.bank_id]['start']:
            self.banks[self.bank_id]['start'] = org
            self.pc = org
        else:
            while self.pc < org:
                self.append_code([0xff])

    def append_code(self, code):
        if self.bank_id not in self.banks:
            self.set_bank_id(self.bank_id)
        self.banks[self.bank_id]['code'].extend(code)
        self.pc += len(code)

    def get_code(self):
        if self.bank_id not in self.banks:
            self.set_bank_id(self.bank_id)
        return self.banks[self.bank_id]['code']

    def get_ines_code(self):
        if self.bank_id not in self.banks:
            self.set_bank_id(self.bank_id)
        bin = []
        nes_header = generate_ines_header()
        for i in range(len(self.banks[0]['code']), self.banks[0]['size']):
            self.banks[0]['code'].append(0xff)
        bin.extend(nes_header)
        bin.extend(self.banks[0]['code'])
        if 1 in self.banks:
            bin.extend(self.banks[1]['code'])
        return bin
