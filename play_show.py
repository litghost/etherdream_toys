import dac
import itertools
from ILDA import readFrames, readFirstFrame
import liblo
import argparse

def playshow(scale, pps, fn):
    a, bp = dac.find_first_dac()
    d = dac.DAC(a)

    target = liblo.Address(a, 60000)
    liblo.send(target, "/geom/tl", int(-1), int(1))
    liblo.send(target, "/geom/tr", int(1), int(1))
    liblo.send(target, "/geom/bl", int(-1), int(-1))
    liblo.send(target, "/geom/br", int(1), int(-1))
    liblo.send(target, "/geom/pps", pps)
    liblo.send(target, "/geom/size", scale)

    with open(fn, 'rb') as f:
        frames = list(readFrames(f))

    def stream_points():
        while True:
            for f in frames:
                for p in f.iterPoints():
                    yield p.encode()

    itr = iter(stream_points())

    d.play_iter(pps, bp.buffer_capacity, itr)

def main():
    parser = argparse.ArgumentParser(description='Play an ILDA show')
    parser.add_argument('filename', help='Filename of ILDA show')
    parser.add_argument('--pps', type=int, default=20000, help='PPS for show [default=%(default)s]')
    parser.add_argument('--scale', type=float, default=1.0, help='Scaling for show [default=%(default)s]')

    args = parser.parse_args()
    playshow(args.scale, args.pps, args.filename)

if __name__ == '__main__':
    main()
