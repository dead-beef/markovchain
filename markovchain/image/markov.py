from itertools import repeat, islice

from .scanner import ImageScanner
from .type import ImageType, Indexed
from ..base import Markov
from ..parser import LevelParser
from ..util import load, fill, level_dataset
from .util import pixel_to_state, state_to_pixel


class MarkovImage(Markov):
    """Markov image generator.
    """

    DEFAULT_SCANNER = ImageScanner
    DEFAULT_PARSER = LevelParser
    DEFAULT_IMGTYPE = Indexed

    def __init__(self,
                 levels=1,
                 imgtype=None,
                 *args, **kwargs):
        """Markov image generator constructor.

        Parameters
        ----------
        levels : `int`, optional
            Number of levels.
        imgtype : `None` or `dict` or `markovchain.image.type.ImageType`
        """
        super().__init__(*args, **kwargs)
        self.imgtype = load(imgtype, ImageType, self.DEFAULT_IMGTYPE)
        self._levels = None
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
        imgs = self.imgtype.convert(data)
        for channel, data in zip(self.imgtype.channels, imgs):
            key = dataset + channel
            data = self.scanner(data, part)
            if isinstance(self.parser, LevelParser):
                self.storage.add_links(self.parser(data, part, key))
            else:
                for level, level_data in enumerate(data):
                    level_key = key + level_dataset(level)
                    level_data = self.parser(level_data, part, level_key)
                    self.storage.add_links(level_data)

    def get_settings_json(self):
        data = super().get_settings_json()
        data['imgtype'] = self.imgtype.save()
        data['levels'] = self.levels
        return data

    def __eq__(self, markov):
        return (self.imgtype == markov.imgtype
                and self.levels == markov.levels
                and super().__eq__(markov))

    def __call__(self, width, height,
                 state_size=None, levels=None,
                 start_level=-1, start_image=None,
                 dataset=''):
        """Generate an image.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_size : `None` or `int` or `list` of `int`, optional
            State size (default: `None`).
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

        Raises
        ------
        ValueError
        """
        if start_level is None:
            if start_image is not None:
                start_level = 0
        elif start_level < 0:
            start_image = None
        elif start_level + 1 >= self.levels:
            if start_image is None:
                raise ValueError('invalid start level: {0}'.format(start_level))
            return start_image

        if start_image is not None:
            width, height = start_image.size
            start_image = self.imgtype.convert(start_image)
        else:
            start_image = repeat(None)
            start_level = -1

        if levels is None:
            levels = self.scanner.levels - start_level - 1
        elif levels <= 0 or start_level + levels >= self.levels:
            raise ValueError('invalid level count: {0}'.format(levels))

        state_sizes = fill(state_size, levels)
        for i, state_size in enumerate(state_sizes):
            if state_size is None:
                if isinstance(self.parser, LevelParser):
                    level = start_level + 1 + i
                    state_sizes[i] = self.parser.parsers[level].state_sizes[0]
                else:
                    state_sizes[i] = self.parser.state_sizes[0]

        channels = [
            self._channel(
                width, height, state_sizes,
                start_level, img, dataset + channel
            )
            for channel, img in zip(self.imgtype.channels, start_image)
        ]

        return self.imgtype.merge(channels)

    def _imgdata(self, width, height,
                 state_size=None, start='', dataset=''):
        """Generate image pixels.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_size : `int` or `None`, optional
            State size to use for generation (default: `None`).
        start : `str`, optional
            Initial state (default: '').
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
        if size > 0 and start:
            yield state_to_pixel(start)
            size -= 1

        while size > 0:
            prev_size = size

            pixels = self.generate(state_size, start, dataset)
            pixels = islice(pixels, 0, size)

            for pixel in pixels:
                yield state_to_pixel(pixel)
                size -= 1

            if prev_size == size:
                if start:
                    yield from repeat(state_to_pixel(start), size)
                else:
                    raise RuntimeError('empty generator')

    @staticmethod
    def _write_imgdata(img, data, tr, x=0, y=0):
        """Write image data.

        Parameters
        ----------
        img : `PIL.Image.Image`
            Image.
        data : `iterable` of `int`
            Image data.
        tr : `markovchain.image.traversal.Traversal`
            Image traversal.
        x : `int`
            X offset.
        y : `int`
            Y offset.
        """
        for pixel, (x1, y1) in zip(data, tr):
            img.putpixel((x + x1, y + y1), pixel)
        return img

    def _channel(self, width, height, state_sizes,
                 start_level, start_image, dataset):
        """Generate a channel.

        Parameters
        ----------
        width : `int`
            Image width.
        height : `int`
            Image height.
        state_sizes : `list` of (`int` or `None`)
            Level state sizes.
        start_level : `int`
            Initial level.
        start_image : `PIL.Image` or `None`
            Initial level image.
        dataset : `str`
            Dataset key prefix.

        Returns
        -------
        `PIL.Image`
            Generated image.
        """
        ret = start_image
        for level, state_size in enumerate(state_sizes, start_level + 1):
            key = dataset + level_dataset(level)
            if start_image is not None:
                scale = self.scanner.level_scale[level - 1]
                width *= scale
                height *= scale
            ret = self.imgtype.create_channel(width, height)
            if start_image is None:
                tr = self.scanner.traversal[0](width, height, ends=False)
                data = self._imgdata(width, height, state_size, '', key)
                self._write_imgdata(ret, data, tr)
            else:
                tr = self.scanner.traversal[0](
                    start_image.size[0],
                    start_image.size[1],
                    ends=False
                )
                for xy in tr:
                    start = pixel_to_state(start_image.getpixel(xy))
                    data = self._imgdata(scale, scale, state_size, start, key)
                    blk = self.scanner.traversal[level](scale, scale, False)
                    x, y = xy
                    x *= scale
                    y *= scale
                    self._write_imgdata(ret, data, blk, x, y)
            start_image = ret
        return ret
