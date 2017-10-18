from itertools import chain, repeat, islice
from PIL import Image

from .scanner import ImageScanner
from .util import palette as default_palette
from ..parser import LevelParser
from ..util import fill


class MarkovImageMixin:
    """Markov chain image generator mixin.
    """

    DEFAULT_SCANNER = ImageScanner
    DEFAULT_PARSER = LevelParser

    def __init__(self,
                 levels=1,
                 palette=None,
                 *args, **kwargs):
        """Markov chain image generator constructor.

        Parameters
        ----------
        levels : `int`, optional
            Number of levels.
        palette : `list` of `int`, optional
            Image palette (default: `markovchain.image.util.palette(8, 4, 8)`).
        """
        super().__init__(*args, **kwargs)
        if palette is None:
            try:
                palette = self.scanner.palette
            except AttributeError:
                palette = default_palette(8, 4, 8)
        elif len(palette) == 3:
            palette = default_palette(*palette)
        self.palette = palette
        self.levels = levels

    @property
    def levels(self):
        """`int` : Number of levels.
        """
        return self._levels

    @levels.setter
    def levels(self, levels):
        if self.scanner is not None:
            self.scanner.levels = levels
        if self.parser is not None:
            self.parser.levels = levels
        self._levels = levels

    def _imgdata(self, width, height, state_size=None, start=None):
        """Generate image pixels.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_size : `int` or `None`, optional
            State size to use for generation (default: `None`).
        start : `str` or `None`, optional
            Initial state (default: `None`).

        Raises
        ------
        RuntimeError
            If generator is empty.

        Returns
        -------
        `generator` of `int`
            Pixel generator.
        """
        maxlength = width * height
        if maxlength > 0 and start is not None:
            yield int(start[-2:], 16)
            maxlength -= 1
        while maxlength > 0:
            prevmaxlength = maxlength
            for pixel in self.generate(maxlength=maxlength,
                                       state_size=state_size,
                                       start=start):
                yield int(pixel[-2:], 16)
                maxlength -= 1
            if prevmaxlength == maxlength:
                if start is not None:
                    pixel = int(start[-2:], 16)
                    yield from repeat(pixel, maxlength)
                else:
                    raise RuntimeError('empty generator')

    def image(self, width, height,
              state_size=None,
              start=None, levels=None,
              start_level=-1, start_image=None):
        """Generate an image.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_size : `int` or `None`, optional
            State size to use for generation (default: `None`).
        start : `str` or `None`, optional
            Initial state (default: `None`).
        levels : `int`, optional
            Number of generated levels (default: `self.scanner.levels`).
        start_level : `int`, optional
            Initial level (default: -1).
        start_image : `PIL.Image` or `None`
            Initial level image (default: `None`).

        Returns
        -------
        `PIL.Image`
            Generated image.
        """
        if levels is None:
            levels = self.scanner.levels
        elif levels <= 0 or levels > self.levels:
            raise ValueError('invalid level count: {0}'.format(levels))

        if start_image is not None:
            start_image = self.scanner.set_palette(start_image)
        else:
            start_level = -1

        if start_level is None or start_level < 0:
            start_level = -1
            start_image = None
        elif start_level + 1 >= levels:
            return start_image

        state_sizes = fill(state_size, levels)
        #if any(sz is not None and sz not in parser.state_sizes
        #       for sz, parser in zip(state_sizes, self.parser.parsers)):
        #    raise ValueError('invalid state sizes: {0}: not in {1}'.format(
        #        state_sizes,
        #        [parser.state_sizes for parser in self.parser.parsers]
        #    ))

        prev = start_image
        gen_levels = islice(enumerate(state_sizes), start_level + 1, levels)

        if prev is not None:
            width, height = prev.size

        for level, state_size in gen_levels:
            if state_size is None:
                try:
                    state_size = self.parser.parsers[level].state_sizes[0]
                except AttributeError:
                    pass

            if prev is not None:
                scale = self.scanner.level_scale[level - 1]
                width *= scale
                height *= scale

            ret = Image.new('P', (width, height))
            ret.putpalette(self.palette)

            if prev is None:
                tr = self.scanner.traversal[0](width, height, ends=False)
                data = self._imgdata(width, height, state_size, start)
                for xy, pixel in zip(tr, data):
                    ret.putpixel(xy, pixel)
            else:
                tr = self.scanner.traversal[0](
                    prev.size[0],
                    prev.size[1],
                    ends=False
                )
                for xy in tr:
                    start = '%02X%02X' % (level - 1, prev.getpixel(xy))
                    x0, y0 = xy
                    x0 *= scale
                    y0 *= scale
                    data = self._imgdata(scale, scale, state_size, start)
                    blk = self.scanner.traversal[level](scale, scale, False)
                    for pixel, (x1, y1) in zip(data, blk):
                        ret.putpixel((x0 + x1, y0 + y1), pixel)

            prev = ret

        return ret

    def data(self, data, part=False):
        """Parse data and update links.

        Parameters
        ----------
        data : `PIL.Image`
            Data to parse.
        part : `bool`, optional
            `True` if data is partial (default: `False`).
        """
        if isinstance(self.parser, LevelParser):
            self.links(self.parser(self.scanner(data, part), part))
        else:
            data = chain.from_iterable(self.scanner(data, part))
            self.links(self.parser(data, part))

    def get_save_data(self):
        """Convert generator settings to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().get_save_data()
        data['palette'] = self.palette
        data['levels'] = self.levels
        return data

    def __eq__(self, markov):
        return (self.palette == markov.palette
                and self.levels == markov.levels)
