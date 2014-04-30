# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from collections import Counter, OrderedDict

from pynes import write_bin_code
import sprite
import nametable

from sprite import SpriteSet

from pynes.tests import show_sprite

palette = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
]

'''create a whole palette based on RGB colos'''


def create_palette():
    palette = []
    for p in sprite.palette:
        r = (p >> 16) & 0xff
        g = (p >> 8) & 0xff
        b = p & 0xff
        palette.append((r, g, b))
    return palette

'''Create a palette to be used in pil'''


def create_pil_palette():
    pps = create_palette()
    pps = [pps[15], pps[2], pps[32], pps[41]]  # TODO hack
    palette = []
    for p in pps:
        palette.extend(p)
    while len(palette) < (256 * 3):
        palette.extend(pps[3])
    return palette


def get_colors(image):
    assert image.size[0] % 8 == 0
    assert image.size[1] % 8 == 0
    colors = []
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if pixels[i, j] not in colors:
                colors.append(pixels[i, j])
    assert len(colors) <= 4, ("Image has {} colors, it can only have at most "
                              "4").format(len(colors))
    return colors

'''
Acquire a regular image to a CHR file,
That could be used to import a whole sprite table,
or also to create a tile set for a nametable
if optimize is False
'''


def acquire_chr(image, nes_palette=palette, optimize_repeated=False):
    assert image.size[0] % 8 == 0
    assert image.size[1] % 8 == 0
    colors = get_colors(image)
    assert len(colors) <= 4, ("Image has {} colors, it can only have at most "
                              "4").format(len(colors))
    default = (
        (0, 0, 0) in colors and
        (255, 0, 0) in colors and
        (0, 255, 0) in colors and
        (0, 0, 255) in colors
    )
    if default:
        nes_palette = palette
    else:
        nes_palette = colors

    sprite_keys = OrderedDict()

    sprs = []
    index = 0
    pixels = image.load()
    for y in range(image.size[1] / 8):
        for x in range(image.size[0] / 8):
            spr = fetch_chr(pixels, x, y, nes_palette)
            encoded = sprite.encode_sprite(spr)
            key = ''.join([chr(e) for e in encoded])
            if not optimize_repeated or key not in sprite_keys:
                sprite_keys[key] = index
                sprs.extend(encoded)
                index += 1
            else:
                pass
                # print index
    return sprs, sprite_keys

'''
fetch part of the image
'''


def fetch_chr(pixels, x, y, palette=palette):
    dx = x * 8
    dy = y * 8
    spr = []
    for j in range(dy, dy + 8):
        line = []
        for i in range(dx, dx + 8):
            if isinstance(pixels[i, j], int):
                color = pixels[i, j]
            else:
                color = palette.index(pixels[i, j])
            assert color >= 0 and color <= 3
            line.append(color)
        spr.append(line)
    return spr

''' function that wrap the acquisition(acquire_chr),
with the input and output file'''


def import_chr(img_file, chr_file):
    img = Image.open(img_file)
    sprs, indexes = acquire_chr(img)
    write_bin_code(sprs, chr_file)

'''
Transform a chr file into a image file
'''


def export_chr(chr_data, image_file, palette=palette, width=8):
    if isinstance(chr_data, str):
        sprs = SpriteSet(chr_data)
    else:
        sprs = SpriteSet(chr_data)
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
                draw.point((x + (8 * dx), y + (8 * dy)), palette[color])
    img.save(image_file, 'PNG')

'''
Thats the oposite of fetch_chr,
it draws a sprite into a PIL image.
'''


def draw_sprite(spr, dx, dy, draw, palette):
    for y in range(8):
        for x in range(8):
            color = spr[y][x]
            draw.point((x + (8 * dx), y + (8 * dy)), palette[color])

'''
Export a nametable to a image
using a chr_file
'''


def export_nametable(nametable_data, chr_data, png_file, palette=palette):
    if isinstance(nametable_data, str):
        nts = nametable.load_nametable(nametable_data)
    else:
        nts = nametable_data

    if isinstance(chr_data, str):
        sprs = SpriteSet(chr_data)
    else:
        sprs = SpriteSet(chr_data)

    nt = nametable.get_nametable(0, nts)
    size = (256, 256)
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    nt_index = 0

    # num_nt = nametable.length(nts)

    if len(sprs) == 512:
        start = 256
    else:
        start = 0

    for y in range(32):
        for x in range(32):
            dx = nt_index / 32
            dy = nt_index % 32
            spr_index = nt[y][x] + start  # TODO something strange with X and Y
            spr = sprs.get(spr_index)
            draw_sprite(spr, dx, dy, draw, palette)
            nt_index += 1

    img.save(png_file, 'PNG')

'''
The function call is read, 'cause the processe is like reading
a text with 64 cols x 64 lines on witch, caracter is a sprite
'''


def read_nametable(image, sprs, palette=palette):
    pixels = image.load()
    colors = get_colors(image)

    default = (
        (0, 0, 0) in colors and
        (255, 0, 0) in colors and
        (0, 255, 0) in colors and
        (0, 0, 255) in colors
    )
    if default:
        nes_palette = palette
    else:
        nes_palette = colors

    nametable = []

    # TODO huge stealing here
    if sprite.length(sprs) == 512:
        start = 256
    else:
        start = 0

    if isinstance(sprs, tuple):
        sprs = sprs[0]

    for y in range(image.size[0] / 8):
        for x in range(image.size[1] / 8):
            spr = fetch_chr(pixels, y, x, nes_palette)
            index = sprite.find_sprite(sprs, spr, start)
            if index != -1:
                nametable.append(index)
            else:
                show_sprite(spr)
                raise Exception('Sprite not found')

            # TODO:
            # encoded = sprite.encode_sprite(spr)
            # key = ''.join([chr(e) for e in encoded])
            # if key in sprs:
            #    if key > 256:
            #        show_sprite(spr)
            #        pass
            # print sprs[key]
            # print sprs[key]
            #    nametable.append(sprs[key])
            # else:
            #   show_sprite(spr)
            #   print x
            #   print y
            #   print '===' + key + '===='
            #   raise Exception('Sprite not found')
    return nametable


def acquire_nametable(image_file, palette=palette):
    image = Image.open(image_file)
    sprs = acquire_chr(image, optimize_repeated=True)
    nametable = read_nametable(image, sprs, palette)
    return nametable, sprs


def import_nametable(png_file, chr_file, nametable_file, palette=palette):
    image = Image.open(png_file)
    sprs = sprite.load_sprites(chr_file)
    nametable = read_nametable(image, sprs, palette)
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
            if pixels[i, j] not in colors:
                colors.append(pixels[i, j])
            cnt[pixels[i, j]] += 1
        break

    return
    # cnt.most_common(4)

    # TODO: implement convert_chr and convert_nametable or delete these lines
    # sprs, indexes = convert_chr(converted, optimize_repeated=True)
    # nametable = convert_nametable(converted, indexes)

    # write_bin_code(sprs, 'sprite.chr')
    # write_bin_code(nametable, 'nametable.bin')

    # return nametable, sprs
