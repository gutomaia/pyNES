# -*- coding: utf-8 -*-

from asm import register_var

def d_inesprg(arg, cart):
    cart.set_iNES_prg(arg)

def d_ineschr(arg, cart):
    cart.set_iNES_chr(arg)

def d_inesmap(arg, cart):
    cart.set_iNES_map(arg)

def d_inesmir(arg, cart):
    cart.set_iNES_mir(arg)

def d_bank(arg, cart):
    cart.set_bank_id(arg)

pc_counter = 0

def d_org(arg, cart):
    cart.set_org(arg)

def d_db(arg, cart):
    l = []
    for token in arg:
        if token['type'] == 'T_ADDRESS':
            l.append(int(token['value'][1:], 16))
    cart.append_code(l)

directive_list = {}
directive_list['.inesprg'] = d_inesprg
directive_list['.ineschr'] = d_ineschr
directive_list['.inesmap'] = d_inesmap
directive_list['.inesmir'] = d_inesmir
directive_list['.bank'] = d_bank
directive_list['.org'] = d_org
directive_list['.db'] = d_db