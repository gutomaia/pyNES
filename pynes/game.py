from re import match

from collections import OrderedDict
from pynes.nes_types import NesType, NesRs, NesArray, NesString, NesSprite, NesChrFile

# TODO remove this
from pynes.bitbag import *

import pynes


class Bit(object):

    def __init__(self, varname, bit, options=False):
        assert bit >= 0 and bit < 8
        self.varname = varname
        self.bit = bit

    def __get__(self, instance, owner):
        assert hasattr(instance, self.varname)
        flag = pow(2, self.bit)
        return getattr(instance, self.varname) & flag == flag

    def __set__(self, instance, value):
        assert isinstance(value, (bool, int))
        assert value == 0 or value == 1
        assert hasattr(instance, self.varname)
        flag = pow(2, self.bit)
        if not value:
            flag = (~flag & 0xFF)
            byte = getattr(instance, self.varname) & flag
        else:
            byte = getattr(instance, self.varname) | flag
        setattr(instance, self.varname, byte)


class PPU(object):

    # TODO base_nametable = Bit('ctrl', 1, options=[0,1,2,3]) #suports 0-3
    sprite_pattern_table = Bit('ctrl', 3)
    background_pattern_table = Bit('ctrl', 4)
    # TODO sprite_size = Bit('ctrl', 5, options=['8x8', '8x16'])
    nmi_enable = Bit('ctrl', 7)

    grayscale_enable = Bit('mask', 0)
    background_enable = Bit('mask', 3)
    sprite_enable = Bit('mask', 4)

    def __init__(self):
        self.ctrl = 0
        self.mask = 0
        self.scrolling = True

    def on_reset(self):
        asm = ('  LDA #%{ctrl:08b}\n'
               '  STA $2000\n'
               '  LDA #%{mask:08b}\n'
               '  STA $2001\n').format(
            ctrl=self.ctrl,
            mask=self.mask)
        return asm

    def on_nmi(self):
        if self.nmi_enable and self.scrolling:
            asm = (
                '  LDA #00\n'
                '  STA $2005\n'
                '  STA $2005\n')
            return asm
        return ''

# change to SpriteSwarmOperation


class NesAddressSet(NesType):

    def __init__(self, addresses, width):
        NesType.__init__(self)
        self.addresses = addresses
        self.width = width
        self.stk = ''
        self.total_addresses = len(addresses)

    def __add__(self, operand):
        self.stk += (
            '  LDA $%04X\n'
            '  CLC\n'
            '  ADC #%d\n') % (self.addresses[0], operand)
        # cols = this.total_addresses / 2  # width
        # lines = this.total_addresses / cols
        for i in range(self.total_addresses):
            self.stk += '  STA $%04X\n' % self.addresses[i]
            if ((i + 1) % self.width) == 0 and i < self.total_addresses - 1:
                self.stk += '  CLC\n  ADC #8\n'
        return self

    def __sub__(self, operand):
        self.addresses.reverse()
        self.stk += (
            '  LDA $%04X\n'
            '  SEC\n'
            '  SBC #%d\n') % (self.addresses[self.width - 1], operand)
        # cols = this.total_addresses / self.width
        # lines = this.total_addresses / cols
        for i in range(self.total_addresses):
            self.stk += '  STA $%04X\n' % self.addresses[i]
            if ((i + 1) % self.width) == 0 and i < self.total_addresses - 1:
                self.stk += '  SEC\n  SBC #8\n'
        self.addresses.reverse()
        return self

    def to_asm(self):
        return self.stk

# change to SpriteOperation


class NesAddress(int, NesType):

    def __new__(cls, val, **kwargs):
        inst = super(NesAddress, cls).__new__(cls, val)
        return inst

    def __init__(self, number):
        NesType.__init__(self)
        int.__init__(self, number)
        self.game = ''

    def __add__(self, operand):
        if isinstance(operand, int):
            self.game += '  LDA $%04x\n' % self
            self.game += '  CLC\n'
            self.game += '  ADC #%d\n' % operand
            self.game += '  STA $%04x\n' % self
        return self

    def __sub__(self, operand):
        if isinstance(operand, int):
            self.game += '  LDA $%04x\n' % self
            self.game += '  SEC\n'
            self.game += '  SBC #%d\n' % operand
            self.game += '  STA $%04x\n' % self
        return self

    def to_asm(self):
        return self.game


# TODO: very ugly, make it better


class Byte(object):

    def __init__(self, address=0):
        self.set_name(self.__class__.__name__, id(self))

    def set_name(self, prefix, key):
        self.target = '%s_%s' % (prefix, key)

    def __get__(self, instance, owner):
        if hasattr(instance, 'base_address'):
            base_address = getattr(instance, 'base_address')
            pos = getattr(instance, self.target)
            address = base_address + pos
            if hasattr(instance, 'sprite'):
                sprite = getattr(instance, 'sprite')
                addresses = []
                if self.target == '__PPUSprite_y':
                    for i in range(len(sprite.tile)):
                        addresses.append(address + i * 4)
                    width = sprite.width
                elif self.target == '__PPUSprite_x':
                    cols = len(sprite.tile) / sprite.width
                    lines = len(sprite.tile) / cols
                    swap = {}
                    for c in range(cols):
                        for l in range(lines):
                            i = (2 * c) + l
                            if l not in swap:
                                swap[l] = []
                            swap[l].append(address + i * 4)
                    for v in swap.values():
                        addresses += v
                    width = cols
                return NesAddressSet(addresses, width)
            else:
                return NesAddress(address)
        return NesAddress(getattr(instance, self.target))

    def __set__(self, instance, value):
        setattr(instance, self.target, value)


class PPUSprite(object):
    y = Byte()  # TODO: should be be Byte(0)
    tile = Byte()
    attrib = Byte()
    x = Byte()

    def __new__(cls, *args, **kwargs):
        for key, atr in cls.__dict__.items():
            if hasattr(atr, 'set_name'):
                atr.set_name('__' + cls.__name__, key)
        return super(PPUSprite, cls).__new__(cls, *args, **kwargs)

    def __init__(self, sprite, game):
        assert isinstance(sprite, (int, NesSprite))

        if isinstance(sprite, int):
            pos = sprite
        elif isinstance(sprite, NesSprite):
            pos = sprite.ppu_address
            self.sprite = sprite

        self.base_address = 0x0200 + (4 * pos)
        self.y = 0
        self.tile = 1
        self.attrib = 2
        self.x = 3
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
                "  BEQ End" + tag + "\n"
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


class Game(object):

    def __init__(self, optimized=True):
        self.ppu = PPU()

        self._asm_chunks = {}
        self.has_nmi = False
        self.state = 'prog'

        self._header = {'.inesprg': 1, '.ineschr': 1,
                        '.inesmap': 0, '.inesmir': 1}
        self._vars = OrderedDict()  # game nes vars
        self.bitpaks = {}
        self.labels = []

        # TODO: self.local_scope = {}
        # TODO: self.global_scope = {}

    def define(self, varname, value, size=1):
        if isinstance(value, NesRs):
            self._vars[varname] = value

    def assign(self, varname, value):
        if isinstance(value, NesType):
            value.instance_name = varname
        self._vars[varname] = value
        return value

    def minusAssign(self, varname, value):
        return
        self += (
            '  SEC\n'
            '  SBC #%02d\n') % value
        # self += '  STA %s\n' % value.instance_name
        return value

    def asmFunction(self, functionname):
        self.state = functionname

    # used just for bitpacks
    def call(self, bitpak_name, args=[]):
        if bitpak_name not in self.bitpaks:
            obj = getattr(pynes.bitbag, bitpak_name, None)
            bp = obj(self)
            self.bitpaks[bitpak_name] = bp
        returnValue = self.bitpaks[bitpak_name](*args)
        self.add_asm_chunk(self.bitpaks[bitpak_name].asm())
        return returnValue
        if (obj):
            try:
                # self.stack(bp(*args))
                bp(*args)
                self += bp.asm()
            except TypeError as ex:
                msg = ex.message.replace('__call__', bitpak_name, 1)
                raise(TypeError(msg))
        else:
            raise(NameError("name '%s' is not defined" % bitpak_name))

    def add_asm_chunk(self, asm_chunk):
        if asm_chunk and isinstance(asm_chunk, str):
            if self.state not in self._asm_chunks:
                self._asm_chunks[self.state] = asm_chunk
            else:
                self._asm_chunks[self.state] += asm_chunk

    def press_start(self):
        return self.to_asm()

    def __add__(self, other):
        if other and isinstance(other, str):
            if self.state not in self._asm_chunks:
                self._asm_chunks[self.state] = other
            else:
                self._asm_chunks[self.state] += other
        return self

    def get_param(self, name, size):
        while name in self._vars:
            name = name + '1'
        self._vars[name] = NesRs(size)
        return name

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
        # if self._state not in self._asm_chunks:
        #    self._asm_chunks[self.state] = ''
        if value == 'reset':
            self._state = value.upper()
            self += self.init()
        else:
            self._state = value

    def headers(self):
        return '\n'.join(['%s %d' % (h, self._header[h])
                          for h in ['.inesprg', '.ineschr', '.inesmap',
                                    '.inesmir']]) + '\n\n'

    def boot(self):
        asm_code = ("  .org $FFFA\n"
                    "  .dw %s\n"
                    "  .dw %s\n"
                    "  .dw 0\n"
                    ) % (
            'NMI' if self.has_nmi else '0',
            'RESET' if 'RESET' in self._asm_chunks else '0'
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
        if 'RESET' in self._asm_chunks:
            asm_code += 'RESET:\n'
            asm_code += self._asm_chunks['RESET']
            asm_code += self.ppu.on_reset()
            asm_code += self.infinity_loop()
        if len(asm_code) > 0:
            return ("  .bank 0\n  .org $C000\n\n" + asm_code + '\n\n')
        return ""

    def bank1(self):
        asm_code = ''. join(
            ['%s:\n%s' % (varname, var.to_asm())
             for varname, var in self._vars.items()
             if isinstance(var, (NesArray, NesSprite, NesString)) and
                var.is_used])
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
        # joypad_2 = Joypad(2, self)
        joypad_code = ''
        if joypad_1.is_used:
            joypad_code += joypad_1.init()
            joypad_code += joypad_1.to_asm()
        if len(joypad_code) > 0 or self.has_nmi:
            self.has_nmi = True  # TODO remove this, use ppu.enable_nmi insted
            nmi_code = (
                "NMI:\n"
                "  LDA #$00\n"
                "  STA $2003 ; Write Only: Sets the offset in sprite ram.\n"
                "  LDA #$02\n"
                "  STA $4014 ; Write Only; DMA\n"
            )
            nmi_code += self.ppu.on_nmi()
            nmi_code += joypad_code
            if 'NMI' in self._asm_chunks:
                nmi_code += self._asm_chunks['NMI']
            return nmi_code + "\n\n" + "  RTI   ;Return NMI\n"
        return ""

    def set_var(self, varname, value):
        self._vars[varname] = value

    def get_var(self, varname):
        return self._vars[varname]

    def to_asm(self):
        asm_code = (
            ';Generated by PyNES\n\n' +
            self.headers() +
            self.rsset() +
            self.prog() +
            self.nmi() +
            self.bank1() +
            self.boot() +
            self.bank2()
        )
        return asm_code
