import liblo
from liblo import make_method
import socket
import time
import math

target = liblo.Address(12002)

class SerialOsc(liblo.Server):
    def __init__(self, *args, **kwargs):
        liblo.Server.__init__(self, *args, **kwargs)
        self.freq = [6, 6]
        self.device = None
        self.spiro = liblo.Address(8989)
        self.update_spiro(0)
        self.update_spiro(1)

    @make_method('/serialosc/device', 'ssi')
    def list_device(self, path, args):
        print 'Found %s/%s at %s' % (args[0], args[1], args[2],)

        if self.device is not None:
            raise RuntimeError('More than 1 monome device?')

        self.device = liblo.Address(args[2])
        liblo.send(self.device, '/sys/port', self.port)
        liblo.send(self.device, '/sys/host', 'localhost')
        liblo.send(self.device, '/monome/ring/all', 0, 15)
        liblo.send(self.device, '/monome/ring/map', 0, *(xrange(64)))
    
    def update_spiro(self, ring):
        if ring == 0:
            liblo.send(self.spiro, '/spiro/l', (self.freq[ring]+50)/100)
        elif ring == 1:
            liblo.send(self.spiro, '/spiro/k', (self.freq[ring]+50)/100)
        

    @make_method('/monome/enc/delta', 'ii')
    def enc_delta(self, path, args):
        ring, delta = args
        self.freq[ring] += float(delta)/50
        self.freq[ring] = min(50, max(-50, self.freq[ring]))

        self.update_spiro(ring)


s = SerialOsc()

liblo.send(target, '/serialosc/list', 'localhost', s.port)
t0 = time.time()
phase = [0, 0]
while True:
    s.recv(10)
    if s.device is not None:
        if time.time() - t0 < 1./120.:
            continue

        tnow = time.time()
        dt = tnow - t0
        t0 = tnow

        for idx in xrange(2):
            phase[idx] -= dt*s.freq[idx]
            level_map = [max(0, min(15, int((math.sin(2*math.pi*i/64+phase[idx])-.9)*10*15))) for i in xrange(64)]
            liblo.send(s.device, '/monome/ring/map', idx, *level_map)
