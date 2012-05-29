# -*- coding: utf-8 -*-

from asm import register_var

def d_inesprg(arg):
    register_var('inesprg', arg)

def d_ineschr(arg):
    register_var('ineschr', arg)

def d_inesmap(arg):
    register_var('inesmap', arg)

def d_inesmir(arg):
    register_var('inesmir', arg)

bank = 0

def d_bank(arg):
    global bank
    bank = int(arg)

def get_bank():
    global bank
    return bank

pc_counter = 0

def d_org(arg):
    global pc_counter
    pc_counter = arg

def d_db(arg):
    l = []
    for token in arg:
        if token['type'] == 'T_ADDRESS':
            l.append(int(token['value'][1:], 16))
    return l

def reset_pc():
    global pc_counter
    pc_counter = 0

def get_pc():
    global pc_counter
    return pc_counter

def increment_pc(arg):
    global pc_counter
    pc_counter += arg

directive_list = {}
directive_list['.inesprg'] = d_inesprg
directive_list['.ineschr'] = d_ineschr
directive_list['.inesmap'] = d_inesmap
directive_list['.inesmir'] = d_inesmir
directive_list['.bank'] = d_bank
directive_list['.org'] = d_org
directive_list['.db'] = d_db