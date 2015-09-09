from pynes.block import MemoryAddress

PPU_CTRL = MemoryAddress('$2000')
PPU_MASK = MemoryAddress('$2001')
PPU_STATUS = MemoryAddress('$2002')

OAM_ADDR = MemoryAddress('$2003')
OAM_DATA = MemoryAddress('$2004')

PPU_SCROLL = MemoryAddress('$2005')
PPU_ADDR = MemoryAddress('$2006')
PPU_DATA = MemoryAddress('$2007')

OAM_DMA = MemoryAddress('$4014')

GAMEPAD_1 = MemoryAddress('$4016')
GAMEPAD_2 = MemoryAddress('$4017')
