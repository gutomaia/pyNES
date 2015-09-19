pyNES
=====


The Legend
----------

There was a time when game cartridges were forged in the fire of mount doom itself. That great power was then
trapped into a regular plastic shelf. Most of the secrets were sealed by fellowship of hardcore game programmers.
Their names were concealed in end-game credits from games that were never supposed to be finished. Countless
game lives were wasted in the first level, in fruitless attempts of unveiling their evil[1] spell.

That was what my curious and inventive mind believed for years, and still do so. As a kid, I used to play those
games and always asked myself how they were done. I really wanted to experience some of the game design problems
the pioneers once faced. Back then, they had to wage their own tools, hack the specs for game effects and layout
the memory mapper circuits. I figure out, that to reach mount doom as equal, foremost, I had to forge my own
hammer. I've decided trail their footmarks therefore I build PyNES: A Python ASM compiler for Nintendo 8 bits.

However as I strum steps progresses, the anvil didn't sound the same. Knowledge weight has changed. Internet
made it all available and communities are helpful. Also, computer power had grown and programming languages
evolved. I must go a further in each step of their challenges. PyNES is turning into a high-level compiler
which will allow Nintendo games to be written mostly in Python. This lecture will explain the several hacks and
drawbacks of such approach. And I must say, trying to compile a such evolved language to a such limited
processor as the c6502 it's MADNESS. It's pyNES!


The Untold Story
----------------

`pyNES <http://gutomaia.net/pyNES>` started as a regular 6502 assembler. However, writing games in ASM wasn't fun enough. There with some AST hacks, I took a step further into figuring out a way to writing then in Python. First approach looks more like a macro languange.


Release notes
-------------

The original pyNES project was splitted in 4 projects.
 * `lexical <http://github.com/gutomaia/lexical>` - just a simple and generic lexical analyser.
 * `nesasm_py <http://github.com/gutomaia/nesasm_py>` - an 6502 assembler based on NESASM
 * `pyNES <http://github.com/gutomaia/pyNES>` - a python to 6502 compiler restricted to basic operations rewriten from scratch
 * `pyNES Standard Libraray <http://github.com/gutomaia/pyNES_StdLib>` - Useful game functions implemented using pyNES witch your game can import or you can use it as a reference guide to implement your own missing features.

I believe that would easier to maintain, and some projects tend to get stable faster. Meaning more focus on the parts that matter. Less gaps for newcomers that want to contribute or just use it.

