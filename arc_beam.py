import liblo
from liblo import make_method
import socket
import time
import math
from math import pi

target = liblo.Address(12002)

RINGS = 2

MK = 'm0000042'
ARC = 'm0000577'

class SerialOsc(liblo.Server):
    def __init__(self, *args, **kwargs):
        liblo.Server.__init__(self, *args, **kwargs)
        self.freq = [6]*4
        self.ring_map = [0, 1]
        self.devices = []
        self.spiro = liblo.Address(8989)
        self.update_spiro(0)
        self.update_spiro(1)

    @make_method('/serialosc/device', 'ssi')
    def list_device(self, path, args):
        print 'Found %s/%s at %s' % (args[0], args[1], args[2],)

        device = liblo.Address(args[2])
        self.devices.append(device)

        if args[0] == MK:
            liblo.send(device, '/sys/prefix', 'mk')
            liblo.send(device, '/mk/grid/led/all', 0)
        elif args[0] == ARC:
            liblo.send(device, '/sys/prefix', 'arc')
            liblo.send(device, '/arc/ring/map', 0, *(xrange(64)))
            liblo.send(device, '/arc/ring/map', 1, *(xrange(64)))
        
        liblo.send(device, '/sys/port', self.port)
        liblo.send(device, '/sys/host', 'localhost')

    def update_setting(self, setting, perc):
        if setting == 0:
            v = -.1*(perc-.5)
            print v
            liblo.send(self.spiro, '/beam/freq', v)
        elif setting == 1:
            liblo.send(self.spiro, '/beam/rot', -2*pi*(perc-.5))
        elif setting == 2:
            v = -.2*(perc-.5)
            print v
            liblo.send(self.spiro, '/beam/freq2', v)
        elif setting == 3:
            liblo.send(self.spiro, '/beam/offset', -2*pi*(perc-.5))
        else:
            pass
    
    def update_spiro(self, ring):
        idx = self.ring_map[ring]
        self.update_setting(idx, (self.freq[idx]+50)/100)
        
    @make_method('/mk/grid/key', 'iii')
    def button(self, path, args):
        (x, y, b) = args
        
        if y in (0, 1) and x < len(s.freq):
            self.ring_map[y] = x
        else:
            self.broadcast('/mk/grid/led/set', x, y, b)


    @make_method('/arc/enc/delta', 'ii')
    def enc_delta(self, path, args):
        ring, delta = args
        idx = self.ring_map[ring]
        self.freq[idx] += float(delta)/50
        self.freq[idx] = min(50, max(-50, self.freq[idx]))

        self.update_spiro(ring)

    @make_method(None, None)
    def fallback(self, path, args):
        print path, args

    def broadcast(self, path, *args):
        for d in self.devices:
            liblo.send(d, path, *args)

s = SerialOsc()

liblo.send(target, '/serialosc/list', 'localhost', s.port)
t0 = time.time()
phase = [0]*len(s.freq)

while True:
    s.recv(10)
    if len(s.devices) > 0:
        if time.time() - t0 < 1./120.:
            continue

        tnow = time.time()
        dt = tnow - t0
        t0 = tnow

        grid_map = [0]*8

        for idx in xrange(len(s.freq)):
            phase[idx] -= dt*s.freq[idx]

        for idx in xrange(RINGS):
            level_map = [max(0, min(15, int((math.sin(2*math.pi*i/64+phase[s.ring_map[idx]])-.9)*10*15))) for i in xrange(64)]
            s.broadcast('/arc/ring/map', idx, *level_map)

            grid_map[idx] = 1 << s.ring_map[idx]

        s.broadcast('/mk/grid/led/map', 0, 0, *grid_map)
