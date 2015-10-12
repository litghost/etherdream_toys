import dac
import itertools
from ILDA import readFrames, readFirstFrame
import liblo
import argparse
import math

COORD_MAX = 32767
COORD_MIN = -32768
COORD_RANGE = COORD_MAX - COORD_MIN

def playshow(scale, pps, freq, amp, phase_v, step):
    a, bp = dac.find_first_dac()
    d = dac.DAC(a)

    target = liblo.Address(a, 60000)
    liblo.send(target, "/geom/tl", int(-1), int(1))
    liblo.send(target, "/geom/tr", int(1), int(1))
    liblo.send(target, "/geom/bl", int(-1), int(-1))
    liblo.send(target, "/geom/br", int(1), int(-1))
    liblo.send(target, "/geom/pps", pps)
    liblo.send(target, "/geom/size", scale)

    def fun(x, t):
        return round(amp*float(COORD_RANGE)/2*math.sin(freq*2*math.pi*float(x)/COORD_RANGE+2*math.pi*phase_v*t))

    def stream_points():
        t = 0
        while True:
            for x in xrange(COORD_MIN, COORD_MAX, step):
                yield (x, fun(x, t), 0, 0, COORD_MAX)

            t += 1

    itr = iter(stream_points())

    d.play_iter(pps, bp.buffer_capacity, itr)

def main():
    parser = argparse.ArgumentParser(description='Play an ILDA show')
    parser.add_argument('--pps', type=int, default=20000, help='PPS for show [default=%(default)s]')
    parser.add_argument('--scale', type=float, default=1.0, help='Scaling for show [default=%(default)s]')
    parser.add_argument('--freq', type=float, default=1.0, help='Frequency of wave for show [default=%(default)s]')
    parser.add_argument('--amp', type=float, default=1.0, help='Amplitude for show [default=%(default)s]')
    parser.add_argument('--phase_velocity', type=float, default=0.0, help='Phase velocity for show [default=%(default)s]')
    parser.add_argument('--steps', type=int, default=100, help='Number of steps per wave [default=%(default)s]')

    args = parser.parse_args()
    playshow(args.scale, args.pps, args.freq, args.amp, args.phase_velocity, args.steps)

if __name__ == '__main__':
    main()
