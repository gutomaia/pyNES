# -*- coding: utf-8 -*-

from analyzer import analyse
from opcodes import opcodes, address_mode_def
from re import match

import inspect
from binascii import hexlify

from asm import generate_ines_header

from directives import directive_list, reset_pc, get_pc, increment_pc

asm65_tokens = [
    dict(type='T_INSTRUCTION', regex=r'^(ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA)', store=True),
    dict(type='T_ADDRESS', regex=r'\$([\dA-F]{2,4})', store=True),
    dict(type='T_HEX_NUMBER', regex=r'\#\$?([\dA-F]{2})', store=True), #TODO: change to HEX_NUMBER
    dict(type='T_BINARY_NUMBER', regex=r'\#%([01]{8})', store=True), #TODO: change to BINARY_NUMBER
    dict(type='T_STRING', regex=r'^"[^"]*"', store=True),
    dict(type='T_SEPARATOR', regex=r'^,', store=True),
    dict(type='T_REGISTER', regex=r'^(X|x|Y|y)', store=True),
    dict(type='T_OPEN', regex=r'^\(', store=True),
    dict(type='T_CLOSE', regex=r'^\)', store=True),
    dict(type='T_LABEL', regex=r'^([a-zA-Z][a-zA-Z\d]*)\:', store=True),
    dict(type='T_MARKER', regex=r'^[a-zA-Z][a-zA-Z\d]*', store=True),
    dict(type='T_DIRECTIVE', regex=r'^\.[a-z]+', store=True),
    dict(type='T_NUM', regex=r'^[\d]+', store=True), #TODO change to DECIMAL ARGUMENT
    dict(type='T_ENDLINE', regex=r'^\n', store=True),
    dict(type='T_WHITESPACE', regex=r'^[ \t\r]+', store=False),
    dict(type='T_COMMENT', regex=r'^;[^\n]*', store=False)
]

def look_ahead(tokens, index, type, value = None):
    if index > len(tokens) - 1:
        return False
    token = tokens[index]
    if token['type'] == type:
        if value == None or token['value'].upper() == value.upper():
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
        tokens[index]['value'] in [
            'BCC', 'BCS', 'BEQ', 'BNE',
            'BMI', 'BPL', 'BVC', 'BVS'
        ]):
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

def t_marker(tokens, index):
    return look_ahead(tokens, index, 'T_MARKER')

def t_address(tokens, index):
    return look_ahead(tokens, index, 'T_ADDRESS')

def t_address_or_t_marker(tokens, index):
    return OR([t_address, t_marker], tokens, index)

def t_number(tokens, index):
    return look_ahead(tokens, index, 'T_HEX_NUMBER')

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

def OR(args, tokens, index):
    for t in args:
        if t(tokens, index):
            return True
    return False

asm65_bnf = [
    dict(type='S_RELATIVE', short='rel', bnf=[t_relative, t_address_or_t_marker]),
    dict(type='S_IMMEDIATE', short='imm', bnf=[t_instruction, t_number]),
    dict(type='S_ZEROPAGE_X', short='zpx', bnf=[t_instruction, t_zeropage, t_separator, t_register_x]),
    dict(type='S_ZEROPAGE_Y', short='zpy', bnf=[t_instruction, t_zeropage, t_separator, t_register_y]),
    dict(type='S_ZEROPAGE', short='zp', bnf=[t_instruction, t_zeropage]),
    dict(type='S_ABSOLUTE_X', short='absx', bnf=[t_instruction, t_address_or_t_marker, t_separator, t_register_x]),
    dict(type='S_ABSOLUTE_Y', short='absy', bnf=[t_instruction, t_address_or_t_marker, t_separator, t_register_y]),
    dict(type='S_ABSOLUTE', short='abs', bnf=[t_instruction, t_address_or_t_marker]),
    dict(type='S_INDIRECT_X', short='indx', bnf=[t_instruction, t_open, t_address_or_t_marker, t_separator, t_register_x, t_close]),
    dict(type='S_INDIRECT_Y', short='indy', bnf=[t_instruction, t_open, t_address_or_t_marker, t_close, t_separator, t_register_y]),
    dict(type='S_IMPLIED', short='sngl', bnf=[t_instruction]),
    #TODO dict(type='S_DIRECTIVE', short='sngl', bnf=[t_directive, [OR, t_num, t_address]]),
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

def get_label(number_token):
    m = match(asm65_tokens[9]['regex'], number_token)
    if m:
        return m.group(1)
    raise Exception('Invalid Label')

def syntax(t):
    ast = []
    x = 0 # consumed
    debug = 0
    labels = []
    while (x < len(t)):
        if t_directive(t,x) and OR([t_num, t_address], t, x+1):
            leaf = {}
            leaf['type'] = 'S_DIRECTIVE'
            leaf['directive'] = t[x]
            leaf['args'] = t[x+1]
            ast.append(leaf)
            x += 2
        elif t_label(t,x):
            labels.append(get_label(t[x]['value']))
            x += 1
        elif t_endline(t,x):
            x += 1
        else:
            for bnf in asm65_bnf:
                leaf = {}
                look_ahead = 0
                move = False
                for i in bnf['bnf']:
                    move = i(t,x + look_ahead)
                    if not move:
                        break;
                    look_ahead += 1
                if move:
                    if len(labels) > 0:
                        leaf['labels'] = labels
                        labels = []
                    leaf['instruction'] = t[x]
                    leaf['type'] = bnf['type']
                    leaf['short'] = bnf['short']
                    if bnf['short'] == 'sngl':
                        pass
                    elif bnf['short'] == 'indx' or bnf['short'] == 'indy':
                        leaf['arg'] = t[x+2]
                    else:
                        leaf['arg'] = t[x+1]
                    ast.append(leaf)
                    x += look_ahead
                    break;
        debug += 1
        if debug > 10000:
            print x
            print t[x]
            raise Exception('Infinity Loop')
    return ast

def semantic(ast, iNES=False):
    bank = []
    code = []
    labels = {}
    #find all labels o the symbol table
    reset_pc()
    labels['palette'] = 0xE000
    labels['sprites'] = 0xE000 + 32
    for leaf in ast:
        if leaf['type'] == 'S_DIRECTIVE':
            directive = leaf['directive']['value']
            if '.org' == directive:
                address = int(leaf['args']['value'][1:], 16)
                directive_list[directive](address)

        if 'labels' in leaf:
            pc = get_pc()
            for label in leaf['labels']:
                labels[label] = pc

        if leaf['type'] != 'S_DIRECTIVE':
            size =  address_mode_def[leaf['short']]['size']
            increment_pc(size)

    #translate statments to opcode
    reset_pc()
    for leaf in ast:
        if leaf['type'] == 'S_DIRECTIVE':
            directive = leaf['directive']['value']
            if 'T_NUM' == leaf['args']['type']:
                args = leaf['args']['value']
                num = int(args)
                directive_list[directive](num)
            elif 'T_ADDRESS' == leaf['args']['type']:
                address = int(leaf['args']['value'][1:], 16)
                directive_list[directive](address)
        else:
            instruction = leaf['instruction']['value']
            address_mode = leaf['short']
            opcode = opcodes[instruction][address_mode]
            if address_mode != 'sngl':
                if 'T_MARKER' == leaf['arg']['type']:
                    address = hex(labels[leaf['arg']['value']])[2:]
                else:
                    address = get_value(leaf['arg']['value'])
                if 'rel' == address_mode:
                    address = int(address, 16)
                    address = 126 + (address - get_pc())
                    address = address | 0b10000000
                    address = hex(address)[2:]

                if len(address) == 4:
                    arg1 = int(address[0:2], 16)
                    arg2 = int(address[2:4], 16)
                    code.extend([opcode, arg2, arg1])
                    increment_pc(3)
                else:
                    arg1 = int(address[0:2], 16)
                    code.extend([opcode, arg1])
                    increment_pc(2)
            else:
                code.append(opcode)
                increment_pc(1)
    nes_code = []
    if iNES:
        nes_header = generate_ines_header()
        nes_code.extend(nes_header)
        nes_code.extend(code)
        return nes_code
    else:
        return code