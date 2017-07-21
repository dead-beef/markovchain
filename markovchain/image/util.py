from colorsys import hsv_to_rgb
from math import floor


def palette(hues, saturations, values):
    size = hues * saturations * values
    if size > 256:
        raise ValueError('palette size > 256: {0}'.format(size))
    if min(hues, saturations, values) < 1:
        raise ValueError('invalid palette size: {0} {1} {2}'
                         .format(hues, saturations, values))

    ret = []
    if hues == 1 and saturations == 1:
        if values == 1:
            size = 0
        else:
            nvalues = values - 1
            for value in range(values):
                value1 = value * 255 // nvalues
                ret.extend((value1, value1, value1))
    else:
        for saturation in range(1, saturations + 1):
            saturation1 = saturation / saturations
            for hue in range(1, hues + 1):
                hue1 = hue / hues
                for value in range(1, values + 1):
                    value1 = value / values
                    ret.extend(floor(x * 255)
                               for x in hsv_to_rgb(hue1, saturation1, value1))

    ret.extend(0 for _ in range((256 - size) * 3))
    return ret


def convert(ctype, img, palette_img, dither=False):
    if ctype == 0:
        img2 = img.convert(mode='P')
        img2.putpalette(palette_img.getpalette())
        return img2

    img.load()
    palette_img.load()
    if palette_img.palette is None:
        raise ValueError('invalid palette image')
    im = img.im.convert('P', int(dither), palette_img.im)
    return img._new(im) # pylint: disable=protected-access
