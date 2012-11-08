import pynes

from pynes.bitbag import *  

if __name__ == "__main__":
    pynes.press_start()
    exit()

palette = [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
        0x0F, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59,
        60, 61, 62, 63 ]

chr_asset = import_chr('player.chr')

player_sprite = create_sprite(chr_asset, 128, 128, [0])

def reset():
    global palette, player_sprite
    wait_vblank()
    clearmen()
    load_palette(palette)
    load_sprite(player_sprite, 0)
    infinity_loop()

def joypad1_up():
    sprite(0).y += 1

def joypad1_down():
    sprite(0).y -= 1

def joypad1_left():
    sprite(0).x -=1

def joypad1_right():
    sprite(0).y +=1
