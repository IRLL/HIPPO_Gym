from importlib import import_module
PIPE = None

class EntryPoint:

    def __int__(self, pipe):
        global PIPE = pipe

    @staticmethod
    def start(entry):
        import_module(entry)
        entry.main()