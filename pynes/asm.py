# -*- coding: utf-8 -*-

var_ines_header = {}
var_table = {}

def get_var(varname):
    if varname == 'inesmap':
        return 0
    return 1
    global var_table, var_ines_header
    if varname in var_ines_header:
        return var_ines_header[varname]
    elif varname in var_table:
        return var_table[varname]
    return None

def register_var(varname, value):
    global var_table, var_ines_header
    if varname in ['inespgr', 'ineschr','inesmap', 'inesmir']:
        var_ines_header[varname] = value
    else:
        var_table[varname] = value

def _asm(arg=None, address=None ):
    pass

def nes_id():
    #NES 
    return [0x4e, 0x45, 0x53, 0x1a]

def nes_get_header(prg, chr, map, mir):
    id = nes_id();
    unused = [0,0,0,0,0,0,0,0]
    header = []
    header.extend(id)
    header.extend([prg])
    header.extend([chr])
    header.extend([mir])
    header.extend([map])
    header.extend(unused)
    return header

def generate_ines_header():
    global var_ines_header

    if 'inespgr' in var_ines_header:
        inespgr = var_ines_header['inespgr']
    else:
        inespgr = 1

    if 'ineschr' in var_ines_header:
        ineschr = var_ines_header['ineschr']
    else:
        ineschr = 1

    if 'inesmap' in var_ines_header:
        inesmap = var_ines_header['inesmap']
    else:
        inesmap = 1

    if 'inesmir' in var_ines_header:
        inesmir = var_ines_header['inesmir']
    else:
        inesmir = 1
    return nes_get_header(inespgr, ineschr, inesmap, inesmir)
