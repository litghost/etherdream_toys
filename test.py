import dac
import itertools
from ILDA import readFrames, readFirstFrame
import liblo

def main():
    a, bp = dac.find_first_dac()
    d = dac.DAC(a)

    scale = .35
    pps = 20000

    target = liblo.Address(a, 60000)
    liblo.send(target, "/geom/tl", int(-1), int(1))
    liblo.send(target, "/geom/tr", int(1), int(1))
    liblo.send(target, "/geom/bl", int(-1), int(-1))
    liblo.send(target, "/geom/br", int(1), int(-1))
    liblo.send(target, "/geom/pps", pps)
    liblo.send(target, "/geom/size", scale)

    with open('ildatest.ild', 'rb') as f:
        frames = list(readFrames(f))

    def stream_points():
        while True:
            for f in frames:
                for p in f.iterPoints():
                    yield p.encode()

    itr = iter(stream_points())

    d.play_iter(pps, bp.buffer_capacity, itr)

if __name__ == '__main__':
    main()
