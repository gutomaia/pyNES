class Context(object):
    __shared_context = {}


    def __init__(self):
        self.__dict__ = self.__shared_context

    def __eq__(self, other):
        if isinstance(other, str):
            return self.asm == other

    def start(self):
        self.asm = ''

    def stop(self):
        self.asm = None

    def __add__(self, other):
        if isinstance(other, str):
            self.asm += other
        return self


class asm_context(object):

    def __init__(self, func=None):
        if func:
            self.func = func
        self.context = Context()

    def __call__(self):
        with self as f:
            self.func()
            a = f.asm
        return a

    def __enter__(self):
        self.context.start()
        return self.context

    def __exit__(self, type, value, traceback):
        pass
