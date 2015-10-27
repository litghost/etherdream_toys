import liblo
import time
from liblo import make_method

target = liblo.Address(12002)

class SerialOsc(liblo.Server):
    def __init__(self, *args, **kwargs):
        liblo.Server.__init__(self, *args, **kwargs)
        self.devices = []

    @make_method('/serialosc/device', 'ssi')
    def list_device(self, path, args):
        print path, args

        id_, type_, port = args
        print port
   
        device = liblo.Address(port)

        liblo.send(device, '/sys/prefix', 'monome')
        liblo.send(device, '/sys/host', 'localhost')
        liblo.send(device, '/sys/port', self.port)
        self.devices.append(device)

    @make_method('/monome/grid/key', 'iii')
    def button(self, path, args):
        (x, y, b) = args
        print x, y
    
        for d in self.devices:
            liblo.send(d, '/monome/grid/led/set', x, y, b)

    @make_method(None, None)
    def fallback(self, path, args):
        print path, args

s = SerialOsc()

liblo.send(target, '/serialosc/list', 'localhost', s.port)
while True:
    s.recv(100)
