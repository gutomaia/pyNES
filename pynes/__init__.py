# -*- coding: utf-8 -*-

def nes_id():
    #NES 
    return [0x4e, 0x45, 0x53, 0xa1]

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

def linker(header,prg, chr):
    return a

def write_bin_code(code, file):
    target = open(file, 'wb')
    for opcode in code:
        target.write(chr(opcode))
    target.close()
    pass