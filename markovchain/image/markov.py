from itertools import chain, repeat, islice
from PIL import Image

from .scanner import ImageScanner
from .util import palette as default_palette
from ..base import Markov
from ..parser import LevelParser
from ..util import fill, level_dataset


class MarkovImage(Markov):
    """Markov image generator.
    """

    DEFAULT_SCANNER = ImageScanner
    DEFAULT_PARSER = LevelParser

    def __init__(self,
                 levels=1,
                 palette=None,
                 *args, **kwargs):
        """Markov image generator constructor.

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
        self._levels = None
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

    def _imgdata(self,
                 width, height,
                 state_size=None,
                 start=None,
                 dataset=''):
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
        dataset : `str`, optional
            Dataset key prefix (default: '').

        Raises
        ------
        RuntimeError
            If generator is empty.

        Returns
        -------
        `generator` of `int`
            Pixel generator.
        """
        size = width * height
        if size > 0 and start is not None:
            yield int(start, 16)
            size -= 1

        while size > 0:
            prev_size = size
            pixels = self.generate(state_size, start, dataset)
            pixels = islice(pixels, 0, size)

            for pixel in pixels:
                yield int(pixel, 16)
                size -= 1

            if prev_size == size:
                if start is not None:
                    yield from repeat(int(start, 16), size)
                else:
                    raise RuntimeError('empty generator')

    def data(self, data, part=False, dataset=''):
        """
        Parameters
        ----------
        data : `PIL.Image`
            Image to parse.
        part : `bool`, optional
            True if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').
        """
        #if self.parser is None:
        #    raise ValueError('no parser')
        data = self.scanner(data, part)
        if isinstance(self.parser, LevelParser):
            self.storage.add_links(self.parser(data, part, dataset))
        else:
            for level, level_data in enumerate(data):
                key = dataset + level_dataset(level)
                self.storage.add_links(self.parser(level_data, part, key))

    def get_settings_json(self):
        data = super().get_settings_json()
        data['palette'] = self.palette
        data['levels'] = self.levels
        return data

    def __eq__(self, markov):
        return (self.palette == markov.palette
                and self.levels == markov.levels
                and super().__eq__(markov))

    def __call__(self, width, height,
                 state_size=None,
                 start=None, levels=None,
                 start_level=-1, start_image=None,
                 dataset=''):
        """Generate an image.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_size : `int` or `None`, optional
            State size (default: `None`).
        start : `str` or `None`, optional
            Initial state (default: `None`).
        levels : `int`, optional
            Number of levels to generate (default: `self.scanner.levels`).
        start_level : `int`, optional
            Initial level (default: -1).
        start_image : `PIL.Image` or `None`
            Initial level image (default: `None`).
        dataset : `str`, optional
            Dataset key prefix (default: '').

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
            key = dataset + level_dataset(level)

            if state_size is None:
                if isinstance(self.parser, LevelParser):
                    state_size = self.parser.parsers[level].state_sizes[0]
                else:
                    state_size = self.parser.state_sizes[0]

            if prev is not None:
                scale = self.scanner.level_scale[level - 1]
                width *= scale
                height *= scale

            ret = Image.new('P', (width, height))
            ret.putpalette(self.palette)

            if prev is None:
                tr = self.scanner.traversal[0](width, height, ends=False)
                data = self._imgdata(width, height, state_size, start, key)
                for xy, pixel in zip(tr, data):
                    ret.putpixel(xy, pixel)
            else:
                tr = self.scanner.traversal[0](
                    prev.size[0],
                    prev.size[1],
                    ends=False
                )
                for xy in tr:
                    start = '%02X' % prev.getpixel(xy)
                    x0, y0 = xy
                    x0 *= scale
                    y0 *= scale
                    data = self._imgdata(scale, scale, state_size, start, key)
                    blk = self.scanner.traversal[level](scale, scale, False)
                    for pixel, (x1, y1) in zip(data, blk):
                        ret.putpixel((x0 + x1, y0 + y1), pixel)

            prev = ret

        return ret
