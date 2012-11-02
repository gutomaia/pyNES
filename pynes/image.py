# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from pynes import write_bin_code
import sprite

palette = [
    (0,0,0),
    (255,0,0),
    (0,255,0),
    (0,0,255)
]

def create_palette():
    palette = []
    for p in sprite.palette:
        r = (p >> 16) & 0xff
        g = (p >> 8) & 0xff
        b = p & 0xff
        palette.append((r,g,b))
    return palette

def create_pil_palette():
    pps = create_palette()
    pps = [pps[15], pps[2], pps[32], pps[41]]
    palette = []
    for p in pps:
        palette.extend(p)
    return palette + [0, ] * (256 - len(pps)) * 3

def fetch_image(img_file):
    pass

def convert_chr(image, nes_palette=None):
    global palette
    assert image.size[0] % 8 == 0
    assert image.size[1] % 8 == 0
    pixels = image.load()
    colors = []
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if pixels[i,j] not in colors:
                colors.append(pixels[i,j])
    assert len(colors) == 4, "Image has %i colors, it can only have 4" % len(colors)
    default =  (
        (0,0,0) in colors and
        (255,0,0) in colors and
        (0,255,0) in colors and
        (0,0,255) in colors
    )
    if default:
        nes_palette = palette
    print image.size[0] / 8
    print image.size[1] / 8

    sprs = []
    for y in range(image.size[1] / 8 ):
        for x in range(image.size[0] / 8 ):
            spr = fetch_chr(pixels, x, y, nes_palette)
            enc = sprite.encode_sprite(spr)
            sprs.extend(enc)
    return sprs

def fetch_chr(pixels, x, y, palette = palette):
    dx = x * 8
    dy = y * 8
    spr = []
    for j in range(dy, dy + 8):
        line = []
        for i in range(dx, dx + 8):
            color = palette.index(pixels[i,j])
            line.append(color)
        spr.append(line)
    return spr

def import_chr(img_file, chr_file):
    img = Image.open(img_file)
    sprs = convert_chr(img)
    write_bin_code(sprs, chr_file)

def export_chr(chr_file, png_file, palette=palette, width=8):
    sprs = sprite.load_sprites(chr_file)
    spr_len = sprite.length(sprs)
    height = spr_len / width
    size = (width * 8, height * 8)

    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    for s_index in range(spr_len):
        spr = sprite.get_sprite(s_index, sprs)
        dx = s_index % width
        dy = s_index / width
        for y in range(8):
            for x in range(8):
                color = spr[y][x]
                draw.point((x+(8*dx),y+(8*dy)), palette[color])
    img.save(png_file, 'PNG')

def export_nametable(nametable_file, chr_file, png_file, palette=palette):
    pass