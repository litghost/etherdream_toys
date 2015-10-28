import dac
import itertools
from ILDA import readFrames, readFirstFrame
import liblo
import argparse
from liblo import make_method
import math
from math import sin, cos, pi

COORD_MAX = 32767
COORD_MIN = -32768
COORD_RANGE = COORD_MAX - COORD_MIN

class BeamToy(liblo.Server):
    def __init__(self, port, freq):
        liblo.Server.__init__(self, port)

        self.freq = freq
        self.freq2 = freq*2
        self.rot = 0
        self.offset = 0

    def playshow(self, scale, pps):
        a, bp = dac.find_first_dac()
        d = dac.DAC(a)

        target = liblo.Address(a, 60000)
        liblo.send(target, "/geom/tl", int(-1), int(1))
        liblo.send(target, "/geom/tr", int(1), int(1))
        liblo.send(target, "/geom/bl", int(-1), int(-1))
        liblo.send(target, "/geom/br", int(1), int(-1))
        liblo.send(target, "/geom/pps", pps)
        liblo.send(target, "/geom/size", scale)

        phase = [0, 0]

        def fun():
            phase[0] += self.freq
            phase[1] += self.freq2
            x = COORD_MAX*(sin(phase[0])+sin(phase[1]+self.offset))/2
            y = 0

            x_rot = x*cos(self.rot)-y*sin(self.rot)
            y_rot = x*sin(self.rot)+y*cos(self.rot)

            return x_rot, y_rot


        def stream_points():
            last_dwell = 0
            while True:
                x, y = fun()
                yield (x, y, 0, 0, COORD_MAX)

                self.recv(0)

        itr = iter(stream_points())

        d.play_iter(pps, bp.buffer_capacity, itr)

    @make_method('/beam/freq', 'f')
    def set_freq(self, path, args):
        self.freq, = args

    @make_method('/beam/freq2', 'f')
    def set_freq2(self, path, args):
        self.freq2, = args

    @make_method('/beam/rot', 'f')
    def set_rot(self, path, args):
        self.rot, = args

    @make_method('/beam/offset', 'f')
    def set_offset(self, path, args):
        self.offset, = args

def main():
    parser = argparse.ArgumentParser(description='Beam line toy')
    parser.add_argument('--port', type=int, default=8989, help='Port to start OSC server [default=%(default)s]')
    parser.add_argument('--pps', type=int, default=20000, help='PPS for show [default=%(default)s]')
    parser.add_argument('--scale', type=float, default=1.0, help='Scaling for show [default=%(default)s]')
    parser.add_argument('--freq', type=float, default=1.0, help='Frequency of wave for show [default=%(default)s]')

    args = parser.parse_args()

    toy = BeamToy(args.port, args.freq)
    toy.playshow(args.scale, args.pps)

if __name__ == '__main__':
    main()
