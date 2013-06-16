import pynes

from pynes.game import Game
from pynes.bitbag import *
from pynes.nes_types import *

game = Game()

palette = game.assign('palette',
            NesArray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,15,
                    0x0F, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59, 60, 61,
                    62, 63])
            )

sprite = game.assign('sprite', game.call('define_sprite', [128, 128, 0, 3]))

game.assign('chr_asset', NesChrFile('player.chr'))

game.asmFunction("reset")
game.call('wait_vblank')
game.call('clearmem')
game.call('wait_vblank')

game.call('load_palette', [palette])
game.call('load_sprite', [sprite, 0])

game.asmFunction("joypad1_up")

game.minusAssign(game.call('get_sprite', [0]).y, 1)

#game.asmFunction("joypad1_up")

#game.call(load_sprite(sprite, 0))

#game.asmFunction("reset")
#game.call(wait_vblank())
#game.call(clearmem())
#game.call(wait_vblank())
#game.call(load_palette(palette))


game.press_start()



'''
def waitvblank()
    asm.bit(0x2002)
    asm.bpl(waitvblank)


sprite = define_sprite(128, 128, 0, 3)

def reset():
    global palette, sprite
    wait_vblank()
    clearmem()
    wait_vblank()
    load_palette(palette)
    load_sprite(sprite, 0)

def joypad1_up():
    get_sprite(0).y -= 1

def joypad1_down():
    get_sprite(0).y += 1

def joypad1_left():
    get_sprite(0).x -=1

def joypad1_right():
    get_sprite(0).x +=1
'''