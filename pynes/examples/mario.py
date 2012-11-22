import pynes

from pynes.bitbag import *  

if __name__ == "__main__":
    pynes.press_start()
    exit()


palette = [
    0x22,0x29, 0x1A,0x0F, 0x22,0x36,0x17,0x0F,  0x22,0x30,0x21,0x0F,  0x22,0x27,0x17,0x0F,
    0x22,0x16,0x27,0x18,  0x22,0x1A,0x30,0x27,  0x22,0x16,0x30,0x27,  0x22,0x0F,0x36,0x17]

chr_asset = import_chr('mario.chr')

tinymario = define_sprite(108,144, [50,51,52,53], 0)

mario = define_sprite(128, 128, [0, 1, 2, 3, 4, 5, 6, 7], 0)

firemario = define_sprite(164,128, [0, 1, 2, 3, 4, 5, 6, 7], 0)

def reset():
    wait_vblank()
    clearmem()
    wait_vblank()
    load_palette(palette)
    load_sprite(tinymario, 0)
    load_sprite(mario, 4)
    load_sprite(firemario, 12)

def joypad1_up():
    get_sprite(mario).y -= 1

def joypad1_down():
    get_sprite(mario).y += 1

def joypad1_left():
    get_sprite(mario).x -= 1

def joypad1_right():
    get_sprite(mario).x += 1

