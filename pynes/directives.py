# -*- coding: utf-8 -*-


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


def d_org(arg, cart):
    cart.set_org(arg)


def d_db(arg, cart):
    l = []
    for token in arg:
        if token['type'] == 'T_ADDRESS':
            l.append(int(token['value'][1:], 16))
    cart.append_code(l)


def d_dw(arg, cart):
    arg1 = (arg & 0x00ff)
    arg2 = (arg & 0xff00) >> 8
    cart.append_code([arg1, arg2])


def d_incbin(arg, cart):
    f = open(cart.path + arg, 'rw')
    content = f.read()
    for c in content:
        cart.append_code([ord(c)])


def d_rsset(arg, cart):
    pass


def d_rs(arg, cart):
    pass

directive_list = {}
directive_list['.inesprg'] = d_inesprg
directive_list['.ineschr'] = d_ineschr
directive_list['.inesmap'] = d_inesmap
directive_list['.inesmir'] = d_inesmir
directive_list['.bank'] = d_bank
directive_list['.org'] = d_org
directive_list['.db'] = d_db
directive_list['.dw'] = d_dw
directive_list['.incbin'] = d_incbin
directive_list['.rsset'] = d_rsset
directive_list['.rs'] = d_rs
