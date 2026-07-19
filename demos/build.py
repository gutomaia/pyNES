"""Build all demos into .nes ROMs: python demos/build.py

Demos live in category subfolders (hello/, math/, sorters/,
graphics/); every .py found is built into a .nes next to it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neslib.font import font_chr  # noqa: E402
from neslib.library import lib as neslib  # noqa: E402
from pynes.cart import Cart  # noqa: E402

DEMOS_DIR = os.path.dirname(os.path.abspath(__file__))

# demos for features that do not exist yet: skipped until the
# compiler catches up
WIP = {
}


def find_demos():
    for root, _, files in sorted(os.walk(DEMOS_DIR)):
        if '__pycache__' in root:
            continue
        for name in sorted(files):
            if name.endswith('.py') and name != 'build.py':
                yield os.path.join(root, name)


def build(path):
    with open(path) as f:
        source = f.read()
    cart = Cart(libraries=[neslib], chr_banks=1, chr_data=font_chr())
    rom = cart.to_nes(source)
    rom_path = path[: -len('.py')] + '.nes'
    with open(rom_path, 'wb') as f:
        f.write(rom)
    relative = os.path.relpath(rom_path, DEMOS_DIR)
    print(f'{relative} ({len(rom)} bytes)')


if __name__ == '__main__':
    for demo in find_demos():
        relative = os.path.relpath(demo, DEMOS_DIR)
        if relative in WIP:
            print(f'{relative} skipped: {WIP[relative]}')
            continue
        build(demo)
