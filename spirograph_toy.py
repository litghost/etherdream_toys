import dac
import itertools
from ILDA import readFrames, readFirstFrame
import liblo
from liblo import make_method
import argparse
from math import cos, sin


COORD_MAX = 32767
COORD_MIN = -32768
COORD_RANGE = COORD_MAX - COORD_MIN

class SpirographToy(liblo.Server):
    def __init__(self, port, freq, rot_freq, l, k):
        liblo.Server.__init__(self, port)

        if l < 0 or l > 1:
            raise ValueError('l out of bounds')

        if k <= 0 or k > 1:
            raise ValueError('k out of bounds')

        self.freq = freq
        self.rot_freq = rot_freq
        self.l = l
        self.k = k
        self.R = COORD_MAX

    @make_method('/spiro/freq', 'f')
    def set_freq(self, path, args):
        self.freq, = args

    @make_method('/spiro/rot_freq', 'f')
    def set_rot_freq(self, path, args):
        self.rot_freq, = args

    @make_method('/spiro/l', 'f')
    def set_l(self, path, args):
        l, = args

        if l >= 0 and l <= 1:
            self.l = l

    @make_method('/spiro/k', 'f')
    def set_k(self, path, args):
        k, = args

        if k > 0 and k <= 1:
            self.k = k

    @make_method('/spiro/R', 'f')
    def set_R(self, path, args):
        self.R, = args

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


        def fun(t):
            t_s = t*self.freq # scaled
            x = self.R*((1-self.k)*cos(t_s)+self.l*self.k*cos((1-self.k)/self.k*t_s))
            y = self.R*((1-self.k)*sin(t_s)-self.l*self.k*sin((1-self.k)/self.k*t_s))

            x_rot = x*cos(t*self.rot_freq)-y*sin(t*self.rot_freq)
            y_rot = x*sin(t*self.rot_freq)+y*cos(t*self.rot_freq)
        
            return x_rot, y_rot

        def stream_points():
            last_dwell = 0
            t = 0.
            while True:
                x, y = fun(t)
                p = (x, y, 0, 0, COORD_MAX)
                yield p
                t += 1

                self.recv(0)

        itr = iter(stream_points())

        d.play_iter(pps, bp.buffer_capacity, itr)

def main():
    parser = argparse.ArgumentParser(description='Play an ILDA show')
    parser.add_argument('--port', type=int, default=8989, help='Port to start OSC server [default=%(default)s]')
    parser.add_argument('--pps', type=int, default=20000, help='PPS for show [default=%(default)s]')
    parser.add_argument('--scale', type=float, default=1.0, help='Scaling for show [default=%(default)s]')
    parser.add_argument('--freq', type=float, default=1.0, help='Frequency of wave for show [default=%(default)s]')
    parser.add_argument('--rot_freq', type=float, default=1.0, help='Rotation Frequency  [default=%(default)s]')
    parser.add_argument('--l', type=float, default=0.4, help='l spirograph parameter (rho/r) [default=%(default)s]')
    parser.add_argument('--k', type=float, default=0.5, help='k spirograph parameter (r/R) [default=%(default)s]')

    args = parser.parse_args()
    toy = SpirographToy(args.port, args.freq, args.rot_freq, args.l, args.k)
    toy.playshow(args.scale, args.pps)

if __name__ == '__main__':
    main()

