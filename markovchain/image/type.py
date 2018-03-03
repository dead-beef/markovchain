from PIL import Image

from .util import convert, palette as default_palette
from ..util import SaveLoad, DOC_INHERIT


class ImageType(SaveLoad, metaclass=DOC_INHERIT):
    """Base image type class.

    Attributes
    ----------
    classes : `dict`
        Image traversal class group.
    mode : `str`
        Image mode.
    channel_mode : `str` or None
        Channel image mode.
    channels : `list` of `str`
        Channel dataset keys.
    """

    classes = {}
    mode = None
    channel_mode = None
    channels = ['']

    def __eq__(self, imgtype):
        return self.__class__ is imgtype.__class__

    def convert(self, img):
        """Convert an image to type.

        Parameters
        ----------
        img : `PIL.Image.Image`

        Returns
        -------
        `tuple` of `PIL.Image.Image`
        """
        return (img.convert(self.mode),)

    def create(self, width, height):
        """Create an image of type.

        Parameters
        ----------
        width: `int`
            Image width.
        height: `int`
            Image height.

        Returns
        -------
        `PIL.Image.Image`
        """
        return Image.new(self.mode, (width, height))

    def create_channel(self, width, height):
        """Create a channel.

        Parameters
        ----------
        width: `int`
            Image width.
        height: `int`
            Image height.

        Returns
        -------
        `PIL.Image.Image`
        """
        if self.channel_mode is None:
            return self.create(width, height)
        return Image.new(self.channel_mode, (width, height))

    def merge(self, imgs):
        """Merge image channels.

        Parameters
        ----------
        imgs : `list` of `PIL.Image.Image`

        Returns
        -------
        `PIL.Image.Image`

        Raises
        ------
        ValueError
            If image channel list is empty.
        """
        if not imgs:
            raise ValueError('empty channel list')
        if len(imgs) == 1:
            return imgs[0]
        return Image.merge(self.mode, imgs)


class Grayscale(ImageType):
    """Grayscale image type.
    """
    mode = 'L'


class RGB(ImageType):
    """RGB image type.
    """

    mode = 'RGB'
    channel_mode = 'L'
    channels = ['_R', '_G', '_B']

    def convert(self, img):
        return img.convert(self.mode).split()


class Indexed(ImageType):
    """Indexed image type.

    Attributes
    ----------
    palette : `list` of `int`
    dither : `bool`
    convert_type : `int`
    """

    mode = 'P'
    channel_mode = None

    def __init__(self, palette=None, dither=True, convert_type=1):
        self._palette = None
        self._palette_image = None
        self.palette = palette
        self.dither = dither
        self.convert_type = convert_type

    def __eq__(self, imgtype):
        return (super().__eq__(imgtype)
                and self.palette == imgtype.palette
                and self.dither == imgtype.dither
                and self.convert_type == imgtype.convert_type)

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        if palette is None:
            palette = [8, 4, 8]
        if len(palette) == 3:
            palette = default_palette(*palette)
        self._palette_image = Image.new('P', (1, 1))
        self._palette_image.putpalette(palette)
        self._palette = palette

    def create(self, width, height):
        ret = super().create(width, height)
        ret.putpalette(self.palette)
        return ret

    def convert(self, img):
        ret = convert(self.convert_type, img, self._palette_image, self.dither)
        return (ret,)

    def save(self):
        ret = super().save()
        ret['palette'] = self.palette
        ret['dither'] = self.dither
        ret['convert_type'] = self.convert_type
        return ret
