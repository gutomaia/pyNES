from pynes.address import OAM_ADDR, OAM_DMA

def reset():
    OAM_ADDR = 00
    OAM_DMA = 2
