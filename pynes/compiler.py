# -*- coding: utf-8 -*-

from analyzer import analyse
from opcodes import opcodes
from re import match

import inspect
from binascii import hexlify

from asm import generate_ines_header

from directives import directive_list
from directives import *

asm65_tokens = [
    dict(type='T_INSTRUCTION', regex=r'^(ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)', store=True),
    dict(type='T_ADDRESS', regex=r'\$([\dA-F]{2,4})', store=True),
    dict(type='T_NUMBER', regex=r'\#\$?([\dA-F]{2})', store=True),
    dict(type='T_BINARY', regex=r'\#%([01]{8})', store=True),
    dict(type='T_STRING', regex=r'^"[^"]*"', store=True),
    dict(type='T_SEPARATOR', regex=r'^,', store=True),
    dict(type='T_REGISTER', regex=r'^(X|Y)', store=True),
    dict(type='T_OPEN', regex=r'^\(', store=True),
    dict(type='T_CLOSE', regex=r'^\)', store=True),
    dict(type='T_LABEL', regex=r'^[a-zA-Z][a-zA-Z\d]*\:?', store=True),
    dict(type='T_DIRECTIVE', regex=r'^\.[a-z]+', store=True),
    dict(type='T_NUM', regex=r'^[\d]+', store=True), #TODO
    dict(type='T_ENDLINE', regex=r'^\n', store=True),
    dict(type='T_WHITESPACE', regex=r'^[ \t\r]+', store=False),
    dict(type='T_COMMENT', regex=r'^;[^\n]*', store=False)
]

def look_ahead(tokens, index, type, value = None):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == type:
        if value == None or token['value'] == value:
            return True
    return False

def t_endline (tokens, index):
    return look_ahead(tokens, index, 'T_ENDLINE', '\n')

def t_directive (tokens, index):
    return look_ahead(tokens, index, 'T_DIRECTIVE')

def t_num(tokens, index):
    return look_ahead(tokens, index, 'T_NUM')

def t_relative (tokens, index):
    if (look_ahead(tokens, index, 'T_INSTRUCTION') and 
        tokens[index]['value'] in ['BPL']):
        return True
    return False

def t_instruction (tokens, index):
    return look_ahead(tokens, index, 'T_INSTRUCTION')

def t_zeropage (tokens,index):
    lh = look_ahead(tokens, index, 'T_ADDRESS')
    if lh and len(tokens[index]['value']) == 3:
        return True
    return False

def t_label(tokens, index):
    return look_ahead(tokens, index, 'T_LABEL')

def t_address(tokens, index):
    return look_ahead(tokens, index, 'T_ADDRESS')

def t_number(tokens, index):
    return look_ahead(tokens, index, 'T_NUMBER')

def t_separator(tokens , index):
    return look_ahead(tokens, index, 'T_SEPARATOR')

def t_register_x(tokens, index):
    return look_ahead(tokens, index, 'T_REGISTER', 'X')

def t_register_y(tokens, index):
    return look_ahead(tokens, index, 'T_REGISTER', 'Y')

def t_open(tokens, index):
    return look_ahead(tokens, index, 'T_OPEN', '(')

def t_close(tokens, index):
    return look_ahead(tokens, index, 'T_CLOSE', ')')

asm65_bnf = [
    dict(type='S_RELATIVE', short='rel', bnf=[t_relative, t_address]),
    dict(type='S_IMMEDIATE', short='imm', bnf=[t_instruction, t_number]),
    dict(type='S_ZEROPAGE_X', short='zpx', bnf=[t_instruction, t_zeropage, t_separator, t_register_x]),
    dict(type='S_ZEROPAGE_Y', short='zpy', bnf=[t_instruction, t_zeropage, t_separator, t_register_y]),
    dict(type='S_ZEROPAGE', short='zp', bnf=[t_instruction, t_zeropage]),
    dict(type='S_ABSOLUTE_X', short='absx', bnf=[t_instruction, t_address, t_separator, t_register_x]),
    dict(type='S_ABSOLUTE_Y', short='absy', bnf=[t_instruction, t_address, t_separator, t_register_y]),
    dict(type='S_ABSOLUTE', short='abs', bnf=[t_instruction, t_address]),
    dict(type='S_INDIRECT_X', short='indx', bnf=[t_instruction, t_open, t_address, t_separator, t_register_x, t_close]),
    dict(type='S_INDIRECT_Y', short='indy', bnf=[t_instruction, t_open, t_address, t_close, t_separator, t_register_y]),
    dict(type='S_IMPLIED', short='sngl', bnf=[t_instruction]),
]

def lexical(code):
    return analyse(code, asm65_tokens)

def get_value(number_token):
    m = match(asm65_tokens[1]['regex'], number_token)
    if m:
        return m.group(1)
    else:
        m = match(asm65_tokens[2]['regex'], number_token)
        return m.group(1)

def syntax(t):
    ast = []
    x = 0
    debug = 0
    while (x < len(t)):
        if t_directive(t,x) and t_num(t, x+1):
            leaf = {}
            leaf['type'] = 'S_DIRECTIVE'
            leaf['directive'] = t[x]
            leaf['args'] = t[x+1]
            ast.append(leaf)
            x += 2
        elif t_directive(t,x) and t_address(t, x+1):
            leaf = {}
            leaf['type'] = 'S_DIRECTIVE'
            leaf['directive'] = t[x]
            leaf['args'] = t[x+1]
            ast.append(leaf)
            x += 2
        elif t_label(t,x):
            x += 1
        elif t_endline(t,x):
            x += 1
        else: 
            for leaf in asm65_bnf:
                look_ahead = 0
                move = True
                for i in leaf['bnf']:
                    move = i(t,x + look_ahead)
                    if not move:
                        break;
                    look_ahead += 1
                if move:
                    leaf['instruction'] = t[x]
                    if leaf['short'] == 'sngl':
                        pass
                    elif leaf['short'] == 'indx' or leaf['short'] == 'indy':
                        leaf['arg'] = t[x+2]
                    else:
                        leaf['arg'] = t[x+1]
                    ast.append(leaf)
                    x += look_ahead
        debug += 1
        if debug > 10000:
            print x
            print t[x]
            raise Exception('Infinity Loop')
            break #just to avoid infinity loops for now
    return ast

def semantic(ast, ines=False):
    bank = []
    code = []
    for leaf in ast:
        if leaf['type'] == 'S_DIRECTIVE':
            directive = leaf['directive']['value']
            if 'T_NUM' == leaf['args']['type']:
                args = leaf['args']['value']
                num = int(args)
                directive_list[directive](num)
        else:
            instruction = leaf['instruction']['value']
            address_mode = leaf['short']
            opcode = opcodes[instruction][address_mode]
            if address_mode != 'sngl':
                address = get_value(leaf['arg']['value'])
                arg1 = int(address[0:2], 16)
                if len(address) == 4:
                    arg2 = int(address[2:4], 16)
                    code = [opcode, arg2, arg1]
                else:
                    code = [opcode, arg1]
            else:
                code = [opcode]
    nes_code = []
    if ines:
        nes_header = generate_ines_header()
        nes_code.extend(nes_header)
        nes_code.extend(code)
        return nes_code
    else:
        return code