# -*- coding: utf-8 -*-

from analyzer import analyse
from opcodes import opcodes
from re import match

import inspect
from binascii import hexlify

asm65_tokens = [
    dict(type='T_INSTRUCTION', regex=r'^(ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)', store=True),
    dict(type='T_ADDRESS', regex=r'\$([\dA-F]{2,4})', store=True),
    dict(type='T_NUMBER', regex=r'\#\$?([\dA-F]{2})', store=True),
    dict(type='T_SEPARATOR', regex=r'^,', store=True),
    dict(type='T_REGISTER', regex=r'^(X|Y)', store=True),
    dict(type='T_OPEN', regex=r'^\(', store=True),
    dict(type='T_CLOSE', regex=r'^\)', store=True),
    dict(type='T_LABEL', regex=r'^[a-z][a-z\d]*', store=True),
    dict(type='T_FUNCTION', regex=r'^\.[a-z]+', store=True),
    dict(type='T_NUM', regex=r'^[\d]+', store=True), #TODO
    dict(type='T_ENDLINE', regex=r'^\n', store=True),
    dict(type='T_WHITESPACE', regex=r'^[ \t]+', store=False),
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
    return look_ahead(tokens, index, 'T_ENDLINE')

def t_instruction (tokens, index):
    return look_ahead(tokens, index, 'T_INSTRUCTION')

def t_zeropage (tokens,index):
    lh = look_ahead(tokens, index, 'T_ADDRESS')
    if lh and len(tokens[index]['value']) == 3:
        return True
    return False

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

def syntax(t):
    ast = []
    x = 0
    while (x < len(t)):
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
        if t_endline(t,x):
            x += 1
    return ast

def semantic(ast):
    code = [];
    for leaf in ast:
        instruction = leaf['instruction']['value']
        address_mode = leaf['short']
        opcode = opcodes[instruction][address_mode]
        if address_mode != 'sngl':
            arg1 = int(leaf['arg']['value'][1:3], 16)
            if len(leaf['arg']['value']) == 5:
                arg2 = int(leaf['arg']['value'][3:5], 16)
                code = [opcode, arg2, arg1]
            else:
                code = [opcode, arg1]
        else:
            code = [opcode]
    return code