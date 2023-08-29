class SlyLogger(object):
    def __init__(self, f):
        self.f = f

    def debug(self, msg, *args, **kwargs):
        self.f.write((msg % args) + '\n')

    info = debug

    def warning(self, msg, *args, **kwargs):
        self.f.write('WARNING: ' + (msg % args) + '\n')

    def error(self, msg, *args, **kwargs):
        self.f.write('ERROR: ' + (msg % args) + '\n')

    critical = debug