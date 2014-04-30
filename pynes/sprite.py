# -*- coding: utf-8 -*-

from collections import OrderedDict

palette = [
    0x788084, 0x0000fc, 0x0000c4, 0x4028c4,
    0x94008c, 0xac0028, 0xac1000, 0x8c1800,
    0x503000, 0x007800, 0x006800, 0x005800,
    0x004058, 0x000000, 0x000000, 0x000008,

    0xbcc0c4, 0x0078fc, 0x0088fc, 0x6848fc,
    0xdc00d4, 0xe40060, 0xfc3800, 0xe46918,
    0xac8000, 0x00b800, 0x00a800, 0x00a848,
    0x008894, 0x2c2c2c, 0x000000, 0x000000,

    0xfcf8fc, 0x38c0fc, 0x6888fc, 0x9c78fc,
    0xfc78fc, 0xfc589c, 0xfc7858, 0xfca048,
    0xfcb800, 0xbcf818, 0x58d858, 0x58f89c,
    0x00e8e4, 0x606060, 0x000000, 0x000000,

    0xfcf8fc, 0xa4e8fc, 0xbcb8fc, 0xdcb8fc,
    0xfcb8fc, 0xf4c0e0, 0xf4d0b4, 0xfce0b4,
    0xfcd884, 0xdcf878, 0xb8f878, 0xb0f0d8,
    0x00f8fc, 0xc8c0c0, 0x000000, 0x000000
]


def load_sprites(src):
    f = open(src, 'rb')
    content = f.read()
    f.close()
    assert len(content) % 16 == 0
    bin = [ord(c) for c in content]
    return bin


def load_indexed_sprites(src):
    f = open(src, 'rb')
    content = f.read()
    assert len(content) % 16 == 0
    bin = [ord(c) for c in content]
    assert len(bin) % 16 == 0
    indexes = OrderedDict()
    for i in range(len(content) / 16):
        indexes[content[i * 16: i * 16 + 16]] = i
    return bin, indexes


def decode_sprite(channelA, channelB):
    s = []
    y = 0
    for y in range(0, 8):
        a = channelA[y]
        b = channelB[y]
        line = []
        for x in range(0, 8):
            bit = pow(2, 7 - x)
            pixel = -1
            if (not (a & bit) and not (b & bit)):
                pixel = 0
            elif ((a & bit) and not (b & bit)):
                pixel = 1
            elif (not (a & bit) and (b & bit)):
                pixel = 2
            elif ((a & bit) and (b & bit)):
                pixel = 3
            line.append(pixel)
        s.append(line)
    return s


def get_sprite(index, sprites):
    assert len(sprites) > index
    iA = index * 16
    iB = iA + 8
    iC = iB + 8
    channelA = sprites[iA:iB]
    channelB = sprites[iB:iC]
    return decode_sprite(channelA, channelB)


def encode_sprite(sprite):
    channelA = []
    channelB = []
    for y in range(8):
        a = 0
        b = 0
        for x in range(8):
            pixel = sprite[y][x]
            bit = pow(2, 7 - x)
            if pixel == 1:
                a = a | bit
            elif pixel == 2:
                b = b | bit
            elif pixel == 3:
                a = a | bit
                b = b | bit
        channelA.append(a)
        channelB.append(b)
    return channelA + channelB


def put_sprite(index, sprites, spr):
    start = index * 16
    encoded = encode_sprite(spr)
    j = 0
    for i in range(start, start + 16):
        sprites[i] = encoded[j]
        j += 1
    return sprites


def length(sprites):
    return len(sprites) / 16


def find_sprite(sprites, spr, start=0):
    for index in range(start, length(sprites)):
        if spr == get_sprite(index, sprites):
            return index - start
    return -1


class SpriteSet():

    def __init__(self, sprite_data=None):
        if isinstance(sprite_data, str):
            self.sprs, self.indexes = load_indexed_sprites(sprite_data)
        else:
            (self.sprs, self.indexes) = sprite_data

    def __len__(self):
        return length(self.sprs)

    def get(self, index):
        return get_sprite(index, self.sprs)

    def put(self, index, spr):
        return put_sprite(index, spr, self.sprs)

    def has_sprite(self, spr):
        if isinstance(spr, list):
            spr = encode_sprite(spr)
            spr = ''.join(chr(c) for c in spr)
        if spr in self.indexes:
            return self.indexes[spr]
        return False
