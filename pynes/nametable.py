# -*- coding: utf-8 -*-


def load_nametable(nt_file):
    f = open(nt_file)
    nt_content = f.read()
    nt_bin = []
    for nt in nt_content:
        nt_bin.append(ord(nt))
    return nt_bin


def get_nametable(index, nt):
    tile_index = index * 1024
    nametable = []
    for y in range(32):
        line = []
        for x in range(32):
            # dx = tile_index / 32
            # dy = tile_index % 32
            spr_index = nt[tile_index]
            line.append(spr_index)
            tile_index += 1
        nametable.append(line)
    return nametable


def length(nt):
    return len(nt) / 1024
