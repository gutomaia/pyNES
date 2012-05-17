# -*- coding: utf-8 -*-

from analyzer import analyse
from opcodes import opcodes
from re import match

import inspect
from binascii import hexlify

asm65_tokens = [
    dict(type='T_INSTRUCTION', regex=ur'^(ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)', store=True),
    dict(type='T_ADDRESS', regex=ur'\$(\d{2,4})', store=True),
    dict(type='T_NUMBER', regex=ur'\#(\d{2})', store=True),
    dict(type='T_SEPARATOR', regex=ur'^,', store=True),
    dict(type='T_REGISTER', regex=ur'^(X|Y)', store=True),
    dict(type='T_OPEN', regex=ur'^\(', store=True),
    dict(type='T_CLOSE', regex=ur'^\)', store=True),
    dict(type='T_WHITESPACE', regex=ur'^\s+', store=False),
]

def t_instruction (tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_INSTRUCTION':
        return True
    return False

def t_zeropage (tokens,index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_ADDRESS' and len(token['value']) == 3:
        return True
    return False

def t_address(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_ADDRESS': #and len(token['value']) == 5:
        return True
    return False

def t_number(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_NUMBER': #and len(token['value']) == 5:
        return True
    return False

def t_separator(tokens , index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_SEPARATOR' and token['value'] == ',':
        return True
    return False

def t_register_x(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_REGISTER' and token['value'] == 'X':
        return True
    return False

def t_register_y(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_REGISTER' and token['value'] == 'Y':
        return True
    return False

def t_open(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_OPEN' and token['value'] == '(':
        return True
    return False

def t_close(tokens, index):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == 'T_CLOSE' and token['value'] == ')':
        return True
    return False

asm65_bnf = [
    dict(type='T_IMMEDIATE', short='imm', bnf=[t_instruction, t_number]),
    dict(type='S_ZEROPAGE_X', short='zpx', bnf=[t_instruction, t_zeropage, t_separator, t_register_x]),
    dict(type='S_ZEROPAGE', short='zp', bnf=[t_instruction, t_zeropage]),
    dict(type='S_ABSOLUTE_X', short='absx', bnf=[t_instruction, t_address, t_separator, t_register_x]),
    dict(type='S_ABSOLUTE_Y', short='absx', bnf=[t_instruction, t_address, t_separator, t_register_y]),
    dict(type='S_ABSOLUTE', short='absx', bnf=[t_instruction, t_address]),

]

def lexical(code):
    return analyse(code, asm65_tokens)

def syntax(t):
    p = 0;
    x = 0;
    ast = []
    if t_instruction(t,0) and t_number(t,1):
        return [
            dict(type='S_IMMEDIATE', short='imm', instruction=t[0], arg=t[1])
        ]
    elif t_instruction(t,0) and t_zeropage(t,1) and t_separator(t,2) and t_register_x(t,3):
        return [
            dict(type='S_ZEROPAGE_X', short='zpx', instruction=t[0], arg=t[1])
        ]
    elif t_instruction(t,0) and t_zeropage(t,1):
        return [
            dict(type='S_ZEROPAGE', short='zp', instruction=t[0], arg=t[1])
        ] 
    elif t_instruction(t,0) and t_address(t,1) and t_separator(t,2) and t_register_x(t,3):
        return [
            dict(type='S_ABSOLUTE_X', short='absx', instruction=t[0], arg=t[1])
        ]
    elif t_instruction(t,0) and t_address(t,1) and t_separator(t,2) and t_register_y(t,3):
        return [
            dict(type='S_ABSOLUTE_Y', short='absy', instruction=t[0], arg=t[1])
        ]
    elif t_instruction(t,0) and t_address(t,1):
        return [
            dict(type='S_ABSOLUTE', short='abs', instruction=t[0], arg=t[1])
        ]
    elif t_instruction(t,0) and t_open(t,1) and t_address(t,2) and t_separator(t,3) and t_register_x(t,4) and t_close(t,5):
        return [
            dict(type='S_INDIRECT_X', short='indx', instruction=t[0], arg=t[2])
        ]
    elif t_instruction(t,0) and t_open(t,1) and t_address(t,2) and t_close(t,3) and t_separator(t,4) and t_register_y(t,5):
        return [
            dict(type='S_INDIRECT_Y', short='indy', instruction=t[0], arg=t[2])
        ]

def semantic(ast):
    code = [];
    for leaf in ast:
        instruction = leaf['instruction']['value']
        address_mode = leaf['short']
        opcode = opcodes[instruction][address_mode]
        arg1 = int(leaf['arg']['value'][1:3], 16)
        if len(leaf['arg']['value']) == 5:
            arg2 = int(leaf['arg']['value'][3:5], 16)
            code = [opcode, arg2, arg1]
        else:
            code = [opcode, arg1]
    return code