# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from collections import Counter, OrderedDict

from pynes import write_bin_code
import sprite, nametable

from sprite import SpriteSet

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
    while len(palette) < (256 * 3):
        palette.extend(pps[3])
    return palette

def convert_chr(image, nes_palette=palette, optimize_repeated = False):
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

    sprite_keys = OrderedDict()

    sprs = []
    index = 0
    for y in range(image.size[1] / 8 ):
        for x in range(image.size[0] / 8 ):
            spr = fetch_chr(pixels, x, y, nes_palette)
            encoded = sprite.encode_sprite(spr)
            key = ''.join([chr(e) for e in encoded])
            if not optimize_repeated or key not in sprite_keys:
                sprite_keys[key] = index
                sprs.extend(encoded)
                index += 1
            else:
                pass
                #print index
    return sprs, sprite_keys

def fetch_chr(pixels, x, y, palette = palette):
    dx = x * 8
    dy = y * 8
    spr = []
    for j in range(dy, dy + 8):
        line = []
        for i in range(dx, dx + 8):
            if isinstance(pixels[i,j], int):
                color = pixels[i,j]
            else:
                color = palette.index(pixels[i,j])
            assert color >= 0 and color <= 3
            line.append(color)
        spr.append(line)
    return spr

def import_chr(img_file, chr_file):
    img = Image.open(img_file)
    sprs, indexes = convert_chr(img)
    write_bin_code(sprs, chr_file)

def export_chr(chr_file, png_file, palette=palette, width=8, show=False):
    sprs = SpriteSet(chr_file)
    spr_len = len(sprs)
    height = spr_len / width
    size = (width * 8, height * 8)

    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    for s_index in range(spr_len):
        spr = sprs.get(s_index)
        dx = s_index % width
        dy = s_index / width
        for y in range(8):
            for x in range(8):
                color = spr[y][x]
                draw.point((x+(8*dx),y+(8*dy)), palette[color])
    img.save(png_file, 'PNG')

def draw_sprite(spr, dx, dy, draw, palette):
    for y in range(8):
        for x in range(8):
            color = spr[y][x]
            draw.point((x+(8*dx),y+(8*dy)), palette[color])

def export_nametable(nametable_file, chr_file, png_file, palette=palette):
    nts = nametable.load_nametable(nametable_file)
    sprs = SpriteSet(chr_file)

    nt = nametable.get_nametable(0, nts)
    size = (256, 256)
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    nt_index = 0

    num_nt = nametable.length(nts)

    if len(sprs) == 512:
        start = 256
    else:
        start = 0

    for y in range(32):
        for x in range(32):
            dx = nt_index / 32
            dy = nt_index % 32
            spr_index = nt[y][x] + start #TODO something strange with X and Y
            spr = sprs.get(spr_index)
            draw_sprite(spr, dx, dy, draw, palette)
            nt_index += 1

    img.save(png_file, 'PNG')


def convert_nametable(image, sprs, palette = palette):
    pixels = image.load()
    colors = []
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if pixels[i,j] not in colors:
                colors.append(pixels[i,j])
    assert len(colors) == 4, "Image has %i colors, it can only have 4" % len(colors)
    assert image.size[0] % 8 == 0
    assert image.size[1] % 8 == 0

    default =  (
        (0,0,0) in colors and
        (255,0,0) in colors and
        (0,255,0) in colors and
        (0,0,255) in colors
    )
    if default:
        nes_palette = palette
    #todo
    nes_palette = palette

    nametable = []
    if sprite.length(sprs) == 512:
        start = 256
    else:
        start = 0

    for y in range(image.size[0] / 8 ):
        for x in range(image.size[1] / 8 ):
            spr = fetch_chr(pixels, y, x, nes_palette)
            #print sprs
            #index = sprite.find_sprite(sprs, spr, start)
            #nametable.append(index)
            #TODO: 
            encoded = sprite.encode_sprite(spr)
            key = ''.join([chr(e) for e in encoded])
            if key in sprs:
                print sprs[key]
                nametable.append(sprs[key])
            #else:
            #    raise Exception('Sprite not found')
    return nametable

def import_nametable(png_file, chr_file, nametable_file, palette=palette):
    image = Image.open(png_file)
    sprs = sprite.load_sprites(chr_file)
    nametable = convert_nametable(image, sprs, palette)
    write_bin_code(nametable, nametable_file)

def convert_to_nametable(image_file):
    colors = []
    original = Image.open(image_file)
    original = original.convert('RGB')
    
    template = Image.new('P', original.size)
    template.putpalette(create_pil_palette())

    converted = original.quantize(palette=template, colors=4)
    pixels = converted.load()

    assert converted.size[0] == 256
    assert converted.size[1] == 256

    cnt = Counter()
    for i in range(converted.size[0]):
        for j in range(converted.size[1]):
            if pixels[i,j] not in colors:
                colors.append(pixels[i,j])
            cnt[pixels[i,j]] += 1
        break

    #cnt.most_common(4) 

    sprs, indexes = convert_chr(converted, optimize_repeated=True)
    nametable = convert_nametable(converted, indexes)

    write_bin_code(sprs, 'sprite.chr')
    write_bin_code(nametable, 'nametable.bin')

    return nametable, sprs

