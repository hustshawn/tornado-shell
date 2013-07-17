import functools
import tornado
import sys
from tornado.iostream import PipeIOStream
import pprint

__author__ = 'vukasin'


class Shell(object):
    def __init__( self, stdin=sys.stdin, stdout=sys.stdout, context={}):
        self.stdin = PipeIOStream(stdin.fileno())
        self.stdout = PipeIOStream(stdout.fileno())
        self.input_buffer = []
        self.running = False
        self.context = context

    def start(self):
        self.running = True
        self.stdin.read_until(b'\n', self.on_line)

    def on_line(self, chunk_bytes: bytes):
        chunk = chunk_bytes.decode('utf-8', errors='ignore').rstrip('\n')
        if not chunk.endswith('\\'):
            self.input_buffer.append(chunk.strip())
            line = " ".join(self.input_buffer)
            self.input_buffer.clear()
            tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self.on_command, line))
        else:
            self.input_buffer.append(chunk[:-1].strip())
            self.stdout.write(b"\r  ")
        if self.running:
            self.start()

    def on_command(self, command):
        if command:
            code = compile(command + '\n', '<shell>', 'eval')
            res = eval(code, self.context)
            if res is not None:
                r = pprint.pformat(res).encode('utf-8')
                self.stdout.write(r + b'\n')
        self.stdout.write(b"\r$>")


