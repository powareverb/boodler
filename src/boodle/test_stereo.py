import unittest

from boodle.stereo import (
    cast, compose, default, extend_tuple, fixed, fixedx, fixedy, fixedxy,
    scale, scalexy, shift, shiftxy)


class TestStereo(unittest.TestCase):

    def assertStereo(self, val, tup):
        self.assertEqual(val, tup)
        self.assertEqual(val, cast(val))

    def test_extend(self):
        self.assertStereo(extend_tuple(()), (1, 0, 1, 0))
        self.assertStereo(extend_tuple((2.0, 3.0)), (2, 3, 1, 0))
        self.assertStereo(extend_tuple((2.0, 3.0, 4.0, 5.0)), (2, 3, 4, 5))

    def test_construct(self):
        self.assertStereo(default(), ())

        self.assertStereo(shift(0), ())
        self.assertStereo(shift(-2), (1, -2))

        self.assertStereo(scale(1), ())
        self.assertStereo(scale(3), (3, 0))

        self.assertStereo(shiftxy(), ())
        self.assertStereo(shiftxy(0), ())
        self.assertStereo(shiftxy(0, 0), ())
        self.assertStereo(shiftxy(3), (1, 3))
        self.assertStereo(shiftxy(0, 3), (1, 0, 1, 3))
        self.assertStereo(shiftxy(2, 3), (1, 2, 1, 3))
        self.assertStereo(shiftxy(0.2, 0.3), (1, 0.2, 1, 0.3))

        self.assertStereo(scalexy(), ())
        self.assertStereo(scalexy(1), ())
        self.assertStereo(scalexy(1, 1), ())
        self.assertStereo(scalexy(3), (3, 0))
        self.assertStereo(scalexy(1, 3), (1, 0, 3, 0))
        self.assertStereo(scalexy(2, 3), (2, 0, 3, 0))
        self.assertStereo(scalexy(0.4, -0.5), (0.4, 0, -0.5, 0))

        self.assertStereo(fixed(2), (0, 2))
        self.assertStereo(fixedx(-2), (0, -2))
        self.assertStereo(fixedy(3), (1, 0, 0, 3))
        self.assertStereo(fixedxy(2, 3), (0, 2, 0, 3))

        self.assertStereo(cast(None), ())
        self.assertStereo(cast(()), ())
        self.assertStereo(cast(0), ())
        self.assertStereo(cast(0.0), ())
        self.assertStereo(cast(-2), (1, -2))
        self.assertStereo(cast(-2), (1, -2))
        self.assertStereo(cast(-2.0), (1, -2))

    def test_compose(self):
        self.assertStereo(compose((), ()), ())

        self.assertStereo(compose(shift(1.5), shift(2)), (1.0, 3.5))
        self.assertStereo(compose(scale(1.5), scale(-2)), (-3, 0))
        self.assertStereo(compose(scale(2), shift(1)), (2, 2))
        self.assertStereo(compose(shift(1), scale(2)), (2, 1))

        self.assertStereo(compose(default(), default()), ())
        val1 = compose(shift(-1), scale(4))
        self.assertStereo(compose(default(), val1), val1)
        self.assertStereo(compose(val1, default()), val1)

        val2 = compose(shift(3), scale(0.5))
        self.assertStereo(compose(val1, val2), (2, 11))

        val4 = compose(shiftxy(2, 7), scalexy(4, 6))
        self.assertStereo(val4, (4, 2, 6, 7))
        self.assertStereo(compose(default(), val4), val4)
        self.assertStereo(compose(val4, default()), val4)

        self.assertStereo(compose(scale(2), val4), (8, 4, 6, 7))
        self.assertStereo(compose(val4, scale(2)), (8, 2, 6, 7))
        self.assertStereo(compose(shift(2), val4), (4, 4, 6, 7))
        self.assertStereo(compose(val4, shift(2)), (4, 10, 6, 7))

        val3 = compose(shiftxy(1, -1), scalexy(0.5, 2))
        self.assertStereo(compose(val3, val4), (2, 2, 12, 13))
        self.assertStereo(compose(val4, val3), (2, 6, 12, 1))
