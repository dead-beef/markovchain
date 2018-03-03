from math import floor
from itertools import islice
from functools import reduce
from PIL import Image

from ..scanner import Scanner
from ..util import fill, to_list, load
from .traversal import Traversal, HLines
from .util import pixel_to_state


class ImageScanner(Scanner):
    """Image scanner class.

    Attributes
    ----------
    resize : (`int`, `int`) or `None`
        If not None, resize images before scanning.
    min_size : `int`
        Minimum image size.
    """
    def __init__(self,
                 resize=None,
                 levels=1,
                 level_scale=4,
                 scale=Image.BICUBIC,
                 traversal=None):
        """Image scanner constructor.

        Parameters
        ----------
        resize : (`int`, `int`) or `None`, optional
            If not `None`, resize images before scanning (default: `None`).
        convert_type : `int`, optional
            Image conversion type (default: 1).
        dither : `bool`
            If `True`, enable image dithering (default: `False`).
        palette : `list` of `int`, optional
            Image palette (default: `markovchain.image.util.palette(8, 4, 8)`).
        levels : `int`, optional
            Number of scanner levels (default: 1).
        level_scale : `int` or `list` of `int`
            Level scale factors.
        scale : `int`, optional
            Scale quality (default: `PIL.Image.BICUBIC`).
        traversal : `dict` or `markovchain.image.traversal.Traversal` or `list` of (`dict` or `markovchain.image.traversal.Traversal`), optional
            Level traversals (default: `markovchain.image.traversal.HLines()`).
        """
        super().__init__()
        self._levels = None
        self._level_scale = None
        self._level_scale_max = None
        self._palette = None
        self._traversal = None
        self._traversal_max = None
        self.min_size = None
        self.palette_image = None
        self.resize = tuple(resize) if resize is not None else None
        self.levels = levels
        self.level_scale = level_scale
        if isinstance(scale, str):
            scale = Image.__getattribute__(scale)
        self.scale = scale
        self.traversal = traversal

    @property
    def traversal(self):
        """`markovchain.image.traversal.Traversal`: Image traversal.
        """
        return self._traversal

    @traversal.setter
    def traversal(self, ts):
        ts = to_list(ts)

        for i, tr in enumerate(ts):
            ts[i] = load(tr, Traversal, HLines)

        if self.levels is not None:
            filled = fill(ts, self.levels, True)
        else:
            filled = ts

        self._traversal_max = ts if len(ts) > len(filled) else filled
        self._traversal = filled

    @property
    def levels(self):
        """`int`: Number of levels.
        """
        return self._levels

    @levels.setter
    def levels(self, levels):
        if levels <= 0:
            raise ValueError('level count <= 0')
        self._levels = levels
        if self._traversal_max is not None:
            self.traversal = self._traversal_max
        if self._level_scale_max is not None:
            self.level_scale = self._level_scale_max

    @property
    def level_scale(self):
        """`list` of `int`: Level scale factors.
        """
        return self._level_scale

    @level_scale.setter
    def level_scale(self, scale):
        scale = to_list(scale)

        if any(x <= 1 for x in scale):
            raise ValueError('level scale <= 1: {0}'.format(scale))

        if self.levels is not None:
            filled = fill(scale, self.levels - 1)
            if filled:
                size = reduce(lambda x, y: x * y, filled)
            else:
                size = 1
        else:
            filled = scale
            size = 1

        self._level_scale_max = scale if len(scale) > len(filled) else filled
        self._level_scale = filled
        self.min_size = size

    def input(self, img):
        """Resize input image if necessary.

        Parameters
        ----------
        img : `PIL.Image`
            Input image.

        Raises
        ------
        ValueError
            If input image is too small.

        Returns
        -------
        `PIL.Image`
            Resized image or input image.
        """
        img_width, img_height = img.size

        if self.resize:
            width, height = self.resize
            scale = min(width / img_width, height / img_height)
            img = img.resize((floor(img_width * scale),
                              floor(img_height * scale)))
            img_width, img_height = img.size

        if img_width < self.min_size or img_height < self.min_size:
            raise ValueError('input image is too small: {0} x {1} < {2} x {2}'
                             .format(img_width, img_height, self.min_size))

        return img

    def level(self, img, level):
        """Get image level.

        Parameters
        ----------
        img : `PIL.Image`
            Input image.
        level : `int`
            Level number.

        Returns
        -------
        `PIL.Image`
            Converted image.
        """
        if level < self.levels - 1:
            width, height = img.size
            scale = reduce(lambda x, y: x * y,
                           islice(self.level_scale, level, self.levels))
            img = img.resize((width // scale, height // scale), self.scale)
        return img

    def _scan_level(self, level, prev, img):
        """Scan a level.

        Parameters
        ----------
        level : `int`
            Level number.
        prev : `PIL.Image` or None
            Previous level image or None if level == 0.
        img : `PIL.Image`
            Current level image.

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END` or (`markovchain.scanner.Scanner.START`, `str`))
            Token generator.
        """
        if level == 0:
            width, height = img.size
        else:
            width, height = prev.size

        tr = self.traversal[0](width, height, ends=(level == 0))
        if level == 0:
            for xy in tr:
                if xy is None:
                    yield self.END
                else:
                    yield pixel_to_state(img.getpixel(xy))
            yield self.END
        else:
            scale = self.level_scale[level - 1]
            for xy in tr:
                x0 = xy[0] * scale
                y0 = xy[1] * scale
                start = (
                    self.START,
                    pixel_to_state(prev.getpixel(xy))
                )
                yield start
                for dxy in self.traversal[level](scale, scale, True):
                    if dxy is None:
                        yield start
                    yield pixel_to_state(
                        img.getpixel((x0 + dxy[0], y0 + dxy[1]))
                    )
                yield self.END

    def __call__(self, img, part=False):
        """Scan an image.

        Parameters
        ----------
        img : `PIL.Image`
            Image to scan.
        part : `bool`, optional
            True if data is partial.

        Raises
        ------
        NotImplementedError
            If `part` is `True`.

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END` or (`markovchain.scanner.Scanner.START`, `str`))
            Token generator.
        """
        if part:
            raise NotImplementedError()

        prev = None
        resized = self.input(img)

        for level in range(self.levels):
            img = self.level(resized, level)
            yield self._scan_level(level, prev, img)
            prev = img

    def __eq__(self, scanner):
        return (self.resize == scanner.resize
                and self.traversal == scanner.traversal
                and self.levels == scanner.levels
                and self.level_scale == scanner.level_scale
                and self.scale == scanner.scale)

    def save(self):
        """Convert to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().save()
        data['resize'] = list(self.resize) if self.resize is not None else None
        data['traversal'] = [t.save() for t in self.traversal]
        data['levels'] = self.levels
        data['level_scale'] = self.level_scale
        data['scale'] = self.scale
        return data
