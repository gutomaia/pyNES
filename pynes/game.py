from re import match

from pynes.nes_types import NesType, NesRs, NesArray, NesString, NesSprite, NesChrFile

class PPU():

    ctrl = 0x0000
    mask = 0x0000

    _sprite_enabled = False

    def nmi_enable(self, value):
        if value:
            self.ctrl = self.ctrl | 0b10000000
        else:
            self.ctrl = self.ctrl & 0b01111111

    def sprite_enable(self, value):
        if value:
            self.mask = self.mask | 0b00010000
        else:
            self.mask = self.mask & 0b11101111

    def init(self):
        asm = ('  LDA #%d\n' #TODO format binary
          '  STA $2000\n'    #TODO also put comments about bits
          '  LDA #%d\n'
          '  STA $2001\n') % (self.ctrl, self.mask)
        return asm

class PPUSprite:

    def __init__(self, pos, game):
        address = 0x0200 + (4 * pos)
        self.y = address
        self.attrib = address + 2
        self.x = address + 3
        self.game = game



    def flip_vertical(self):
        asm = (
            '  LDA $%04X\n'
            '  EOR #%d\n'
            '  STA $%04X\n'
        ) % (
            self.attrib,
            128,
            self.attrib
        )
        self.game += asm

    def flip_horizontal(self):
        asm = (
            '  LDA $%04X\n'
            '  EOR #%d\n'
            '  STA $%04X\n'
        ) % (
            self.attrib,
            64,
            self.attrib
        )
        self.game += asm

class Joypad():

    def __init__(self, player_num, game):
        assert player_num == 1 or player_num == 2
        self.num = player_num
        if player_num == 1:
            self.port = '$4016'
        else:
            self.port = '$4017'
        self.game = game
        self.actions = ['a', 'b', 'select', 'start', 
          'up', 'down', 'left', 'right']

    def __iter__(self):
        for action in self.actions:
            tag = action.capitalize()
            asm_code = (
                "JoyPad" + str(self.num) + tag + ":\n"
                "  LDA " + self.port + "\n"
                "  AND #%00000001\n"
                "  BEQ End" + tag +"\n"
            )
            index = 'joypad' + str(self.num) + '_' + action
            if index in self.game._asm_chunks:
                asm_code += self.game._asm_chunks[index]
            asm_code += "End" + tag + ":\n"
            yield asm_code

    def init(self):
        return ('StartInput:\n' 
            '  LDA #$01\n'
            '  STA $4016\n'
            '  LDA #$00\n'
            '  STA $4016\n')

    @property
    def is_used(self):
        for status in self.game._asm_chunks:
            if match('^joypad[12]_(a|b|select|start|up|down|left|right)', status):
                return True
        return False

    def to_asm(self):
        if self.is_used:
            return '\n'.join(self)
        return ''


class Game:

    ppu = PPU()

    def __init__(self):
        self._state = 'prog'
        self._asm_chunks = {}
        self.has_nmi = False

        self._header = {'.inesprg':1, '.ineschr':1,
            '.inesmap':0, '.inesmir':1}
        self._vars = {}
        self.bitpaks = {}
        self.labels = []

    def __add__(self, other):
        if other and isinstance(other, str):
            if self._state not in self._asm_chunks:
                self._asm_chunks[self._state] = other
            else:
                self._asm_chunks[self._state] += other
        return self

    def get_label_for(self, label):
        while label in self.labels:
            label = label + '1'
        self.labels.append(label)
        return label

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.prog = value + ':\n' 

    def headers(self):
        return '\n'.join(['%s %d' % (h, self._header[h])
            for h in ['.inesprg', '.ineschr', '.inesmap', '.inesmir']]) + '\n\n'

    def boot(self):
        asm_code =("  .org $FFFA\n"
             "  .dw %s\n"
             "  .dw %s\n"
             "  .dw 0\n"
            ) % (
            'NMI' if self.has_nmi else '0',
            'RESET' if 'reset' in self._asm_chunks else '0'
            )
        return asm_code

    def init(self):
        return (
          '  SEI          ; disable IRQs\n' +
          '  CLD          ; disable decimal mode\n' +
          '  LDX #$40\n' +
          '  STX $4017    ; disable APU frame IRQ\n' +
          '  LDX #$FF\n' +
          '  TXS          ; Set up stack\n' +
          '  INX          ; now X = 0\n' +
          '  STX $2000    ; disable NMI\n' +
          '  STX $2001    ; disable rendering\n' +
          '  STX $4010    ; disable DMC IRQs\n'
        )

    def rsset(self):
        asm_code = '\n'.join([
                '%s .rs %d' % (varname, var.size)
                for varname, var in self._vars.items()
                if isinstance(var, NesRs)
            ])
        if asm_code:
            return ("  .rsset $0000\n%s\n\n" % asm_code)
        return ""

    def infinity_loop(self):
        return (
          "InfiniteLoop:\n"
          "  JMP InfiniteLoop\n"
        )

    def prog(self):
        asm_code = ""
        if 'prog' in self._asm_chunks:
            asm_code += self._asm_chunks['prog'] 
        for bp in self.bitpaks:
            procedure = self.bitpaks[bp].procedure()
            if isinstance(procedure, str):
                asm_code += procedure + '\n'
        if 'reset' in self._asm_chunks:
            asm_code += self._asm_chunks['reset']
            asm_code += self.ppu.init()
            asm_code += self.infinity_loop()
        if len(asm_code) > 0:
            return ( "  .bank 0\n  .org $C000\n\n" + asm_code +'\n\n')
        return ""

    def bank1(self):
        asm_code = ''. join(
            ['%s:\n%s' % (varname, var.to_asm())
            for varname, var in self._vars.items()
            if (isinstance (var,NesArray) or isinstance(var, NesSprite))])
        if asm_code:
            return ("  .bank 1\n  .org $E000\n\n" + asm_code + '\n\n')
        return "  .bank 1\n"

    def bank2(self):
        asm_code = '\n'.join(
            ['  .incbin "%s"' % var.filename
            for varname, var in self._vars.items()
            if isinstance(var, NesChrFile)
            ])

        if asm_code:
            return ("  .bank 2\n  .org $0000\n\n" + asm_code + '\n\n')
        return ""

    def nmi(self):
        joypad_1 = Joypad(1, self)
        joypad_2 = Joypad(2, self)
        joypad_code = ''
        if joypad_1.is_used:
            joypad_code += joypad_1.init()
            joypad_code += joypad_1.to_asm()
        if len(joypad_code) > 0 or self.has_nmi:
            self.has_nmi = True
            nmi_code = (
                "NMI:\n"
                "  LDA #$00\n"
                "  STA $2003 ; Write Only: Sets the offset in sprite ram.\n"
                "  LDA #$02\n"
                "  STA $4014 ; Write Only; DMA\n"
            )
            return nmi_code + joypad_code + "\n\n" + "  RTI   ;Return NMI\n"
        return ""

    def set_var(self, varname, value):
        self._vars[varname] = value

    def get_var(self, varname):
        return self._vars[varname]

    def to_asm(self):
        asm_code = (';Generated by PyNES\n\n' +
            self.headers() +
            self.rsset() +
            self.prog() +
            self.nmi() +
            self.bank1() +
            self.boot() +
            self.bank2()
            )
        return asm_code