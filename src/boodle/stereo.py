# Boodler: a programmable soundscape tool
# Copyright 2002-2011 by Andrew Plotkin <erkyrath@eblong.com>
#   <http://boodler.org/>
# This program is distributed under the LGPL.
# See the LGPL document, or the above URL, for details.
"""stereo: Utility functions for stereo panning.

These functions return a stereo object -- an object which represents a
range of stereo positions for a soundscale. Stereo objects can be passed
to new_channel_pan() or sched_note_pan().

default() -- return the default stereo position
shift() -- return a simple stereo shift
shiftxy() -- return a two-dimensional stereo shift
scale() -- return a stretched or compressed stereo effect
scalexy() -- return a two-dimensional stereo scaling
fixed() -- return a stereo effect which is compressed to a point
fixedx() -- an alias for fixed
fixedy() -- return a stereo effect which is compressed to a point on the Y axis
fixedxy() -- return a stereo effect compressed to a point on the XY plane
compose() -- apply one stereo effect on top of another
cast() -- convert an object to a stereo effect
"""

# Currently, a stereo object is represented as a tuple of zero, two, or
# four floats: (xscale, xshift, yscale, yshift). A 2-tuple only has
# the X values, and the 0-tuple represents the identity (1,0,1,0).
# However, the implementation may change in the future. So keep using
# these utility functions.

# Handy constants representing the identity
Identity = ()
Identity_2 = (1.0, 0.0)
Identity_4 = (1.0, 0.0, 1.0, 0.0)


def default():
    """default() -> stereo

    Return a stereo object which describes the default stereo position --
    no shift, no contraction.
    """
    return ()


def shift(pos):
    """shift(pos) -> stereo

    Return a simple stereo shift. If pos is zero, there is no shift in
    origin; this returns the default stereo position. -1 means directly
    to the left; 1 means directly to the right. More extreme values
    recede into the distance.
    """

    if pos == 0:
        return ()
    return (1.0, float(pos))


def shiftxy(posx=0, posy=0):
    """shiftxy(posx=0, posy=0) -> stereo

    Return a two-dimensional stereo shift. If posy is zero (or omitted),
    this is equivalent to shift(posx).
    """

    if posx == 0 and posy == 0:
        return ()
    if posy == 0:
        return (1.0, float(posx))
    return (1.0, float(posx), 1.0, float(posy))


def scale(size):
    """scale(size) -> stereo

    Return a stereo effect which is not shifted left or right, but is
    compressed or stretched from the center. If size is less than 1,
    the channels are compressed; zero causes every sound to be perfectly
    centered. If size is greater than 1, the channels are spread apart.
    Negative values cause the left and right channels to swap.
    """

    if size == 1:
        return ()
    return (float(size), 0.0)


def scalexy(sizex=1, sizey=1):
    """scalexy(sizex=1, sizey=1) -> stereo

    Return a two-dimensional stereo scaling. If sizey is 1 (or omitted),
    this is equivalent to scale(sizex).
    """

    if sizex == 1 and sizey == 1:
        return ()
    if sizey == 1:
        return (float(sizex), 0.0)
    return (float(sizex), 0.0, float(sizey), 0.0)


def fixed(pos):
    """fixed(pos) -> stereo

    Return a stereo effect which is compressed to a point (on the X axis).
    All sounds contained in this effect, no matter how shifted, will come
    from a single point. If pos is zero, this will be the center; if -1,
    directly to the left; if 1, directly to the right.
    """
    return (0.0, float(pos))


def fixedx(pos):
    """fixedx(pos) -> stereo

    An alias for fixed(pos).
    """
    return fixed(pos)


def fixedy(posy):
    """fixedy(posy) -> stereo

    Return a stereo effect which is compressed to a point on the Y axis.
    """
    return (1.0, 0.0, 0.0, float(posy))


def fixedxy(posx, posy):
    """fixedxy(posx, posy) -> stereo

    Return a stereo effect which is compressed to a point on the XY plane.
    """
    return (0.0, float(posx), 0.0, float(posy))


def compose(stereo1, stereo2):
    """compose(stereo1, stereo2):

    Return a stereo effect which is the result of applying of stereo1
    on top of stereo2. This is the equivalent of a channel set to
    stereo1, containing a channel stereo2.

    """
    len1 = len(stereo1)
    len2 = len(stereo2)
    maxlen = max(len1, len2)

    if maxlen == 0:
        return ()

    if maxlen == 2:
        if len1 == 0:
            (scale1, shift1) = (1.0, 0.0)
        else:
            (scale1, shift1) = stereo1
        if len2 == 0:
            (scale2, shift2) = (1.0, 0.0)
        else:
            (scale2, shift2) = stereo2

        return (scale2 * scale1, (shift2 * scale1) + shift1)

    if maxlen == 4:
        (scalex1, shiftx1, scaley1, shifty1) = extend_tuple(stereo1)
        (scalex2, shiftx2, scaley2, shifty2) = extend_tuple(stereo2)
        return (
            scalex2 * scalex1,
            (shiftx2 * scalex1) + shiftx1,
            scaley2 * scaley1,
            (shifty2 * scaley1) + shifty1,
        )

    raise TypeError('compose: stereo tuples must have length 0, 2, or 4')


def cast(obj):
    """cast(obj) -> stereo

    Convert obj into a stereo object. If obj is None, this returns the
    default stereo position. If obj is a number, this returns a simple
    stereo shift -- no scaling. If obj is a stereo object, this returns
    it.
    """

    if obj is None:
        return ()
    objtyp = type(obj)

    if objtyp is tuple:
        if len(obj) in [0, 2, 4]:
            for val in obj:
                if not isinstance(val, float):
                    raise TypeError('stereo must be a tuple of floats')
            return obj
        raise TypeError('stereo tuple must have length 0, 2, or 4')

    if objtyp in (int, float):
        if obj == 0:
            return ()
        return (1.0, float(obj))

    raise TypeError('object can\'t be converted to stereo')


def extend_tuple(obj):
    """extend_tuple(obj) -> stereo

    Given a stereo object, return a 4-tuple which is an equivalent stereo
    object.

    (This is an internal function. Outside callers should not make use
    of it.)
    """

    olen = len(obj)

    if olen == 0:
        return Identity_4

    if olen == 2:
        return (obj[0], obj[1], 1.0, 0.0)

    if olen == 4:
        return obj
