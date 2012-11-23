import pynes

from pynes.bitbag import *  

palette = [
    0x22,0x29, 0x1A,0x0F, 0x22,0x36,0x17,0x0F,  0x22,0x30,0x21,0x0F,  0x22,0x27,0x17,0x0F,
    0x22,0x16,0x27,0x18,  0x22,0x1A,0x30,0x27,  0x22,0x16,0x30,0x27,  0x22,0x0F,0x36,0x17]

chr_asset = import_chr('mario.chr')

title = "pyNES"
subtitle = "Python Programming for NES"

gutomaia = "Guto Maia gutomaia"

slide1 = "slide 1111"
slide2 = "slide 2  2222"

slide = rs(1)
block = rs(1)
wait = rs(1)

def reset():
    wait_vblank()
    clearmem()
    wait_vblank()
    load_palette(palette)
    slide = 0
    block = 0
    wait = 0

def joypad1_a():
    if block == 0:
        slide += 1
        block = 1

def joypad1_b():
    if block == 0:
        slide -= 1
        block = 1

def nmi():
    if slide == 0:
        show(title, 5)
    elif slide == 1:
        show(subtitle, 8)
    elif slide == 2:
        show(slide2, 9,10)
    if block == 1:
        wait += 1

    if wait == 100:
        wait = 0
        block = 0
