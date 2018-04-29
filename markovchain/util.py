from itertools import islice, repeat
from copy import deepcopy
from custom_inherit import DocInheritMeta


DOC_INHERIT = DocInheritMeta(
    style='numpy',
    abstract_base_class=False
)

DOC_INHERIT_ABSTRACT = DocInheritMeta(
    style='numpy',
    abstract_base_class=True
)


class SaveLoad(metaclass=DOC_INHERIT_ABSTRACT):
    """Base class for converting to/from JSON.

    Attributes
    ----------
    classes : `dict`
        Class group.

    Examples
    --------
    >>> class SaveLoadGroup(SaveLoad):
    ...     classes = {}
    ...
    >>> class SaveLoadObject(SaveLoadGroup):
    ...     def __init__(self, attr=None):
    ...         self.attr = attr
    ...     def save(self):
    ...         data = super().save()
    ...         data['attr'] = self.attr
    ...         return data
    ...
    >>> SaveLoadGroup.add_class(SaveLoadObject)
    >>> SaveLoadGroup.classes
    {'SaveLoadObject': <class '__main__.SaveLoadObject'>}
    >>> obj = SaveLoadObject(0)
    >>> data = obj.save()
    >>> data
    {'attr': 0, '__class__': 'SaveLoadObject'}
    >>> obj2 = SaveLoadGroup.load(data)
    >>> type(obj2)
    <class '__main__.SaveLoadObject'>
    >>> obj2.attr
    0
    """

    classes = {}

    @classmethod
    def add_class(cls, *args):
        """Add classes to the group.

        Parameters
        ----------
        *args : `type`
            Classes to add.
        """
        for cls2 in args:
            cls.classes[cls2.__name__] = cls2

    @classmethod
    def remove_class(cls, *args):
        """Remove classes from the group.

        Parameters
        ----------
        *args : `type`
            Classes to remove.
        """
        for cls2 in args:
            try:
                del cls.classes[cls2.__name__]
            except KeyError:
                pass

    @classmethod
    def load(cls, data):
        """Create an object from JSON data.

        Parameters
        ----------
        data : `dict`
            JSON data.

        Returns
        ----------
        `object`
            Created object.

        Raises
        ------
        KeyError
            If `data` does not have the '__class__' key
            or the necessary class is not in the class group.
        """
        ret = cls.classes[data['__class__']]
        data_cls = data['__class__']
        del data['__class__']
        try:
            ret = ret(**data)
        finally:
            data['__class__'] = data_cls
        return ret

    def save(self):
        """Convert an object to JSON.

        Returns
        ----------
        `dict`
            JSON data.
        """
        return {
            '__class__': self.__class__.__name__
        }


class ObjectWrapper: # pylint:disable=too-few-public-methods
    """Base class for wrapping objects.

    Example
    -------
    >>> class Object:
    ...     def method(self):
    ...         return 2
    ...
    >>> class Wrapper(ObjectWrapper):
    ...     def method(self):
    ...         return super().method() * 2
    ...
    >>> obj = Object()
    >>> wrapped = Wrapper(obj)
    >>> wrapped.method()
    4
    """
    def __init__(self, obj):
        self.__class__ = type(
            obj.__class__.__name__,
            (self.__class__, obj.__class__),
            {}
        )
        self.__dict__ = obj.__dict__


def const(x):
    """Return a function that takes any arguments and returns the specified value.

    Parameters
    ----------
    x
        Value to return.

    Returns
    -------
    `function`
    """
    return lambda *args, **kwargs: x

def to_list(x):
    """Convert a value to a list.

    Parameters
    ----------
    x
        Value.

    Returns
    -------
    `list`

    Examples
    --------
    >>> to_list(0)
    [0]
    >>> to_list({'x': 0})
    [{'x': 0}]
    >>> to_list(x ** 2 for x in range(3))
    [0, 1, 4]
    >>> x = [1, 2, 3]
    >>> to_list(x)
    [1, 2, 3]
    >>> _ is x
    True
    """
    if isinstance(x, list):
        return x
    if not isinstance(x, dict):
        try:
            return list(x)
        except TypeError:
            pass
    return [x]

def fill(xs, length, copy=False):
    """Convert a value to a list of specified length.

    If the input is too short, fill it with its last element.

    Parameters
    ----------
    xs
        Input list or value.
    length : `int`
        Output list length.
    copy : `bool`, optional
        Deep copy the last element to fill the list (default: False).

    Returns
    -------
    `list`

    Raises
    ------
    ValueError
        If `xs` is empty and `length` > 0

    Examples
    --------
    >>> fill(0, 3)
    [0, 0, 0]
    >>> fill((x ** 2 for x in range(3)), 1)
    [0]
    >>> x = [{'x': 0}, {'x': 1}]
    >>> y = fill(x, 4)
    >>> y
    [{'x': 0}, {'x': 1}, {'x': 1}, {'x': 1}]
    >>> y[2] is y[1]
    True
    >>> y[3] is y[2]
    True
    >>> y = fill(x, 4, True)
    >>> y
    [{'x': 0}, {'x': 1}, {'x': 1}, {'x': 1}]
    >>> y[2] is y[1]
    False
    >>> y[3] is y[2]
    False
    """
    if isinstance(xs, list) and len(xs) == length:
        return xs

    if length <= 0:
        return []

    try:
        xs = list(islice(xs, 0, length))
        if not xs:
            raise ValueError('empty input')
    except TypeError:
        xs = [xs]

    if len(xs) < length:
        if copy:
            last = xs[-1]
            xs.extend(deepcopy(last) for _ in range(length - len(xs)))
        else:
            xs.extend(islice(repeat(xs[-1]), 0, length - len(xs)))

    return xs

def int_enum(cls, val):
    """Get int enum value.

    Parameters
    ----------
    cls : `type`
        Int enum class.
    val : `int` or `str`
        Name or value.

    Returns
    -------
    `IntEnum`

    Raises
    ------
    ValueError
    """
    if isinstance(val, str):
        val = val.upper()
        try:
            return getattr(cls, val)
        except AttributeError:
            raise ValueError('{0}.{1}'.format(cls, val))
    return cls(val)

def load(obj, cls, default_factory):
    """Create or load an object if necessary.

    Parameters
    ----------
    obj : `object` or `dict` or `None`
    cls : `type`
    default_factory : `function`

    Returns
    -------
    `object`
    """
    if obj is None:
        return default_factory()
    if isinstance(obj, dict):
        return cls.load(obj)
    return obj

def _extend(dst, src):
    for key, val in src.items():
        if isinstance(val, dict):
            try:
                old = dst[key]
                if isinstance(old, dict):
                    _extend(old, val)
                else:
                    dst[key] = val
            except KeyError:
                dst[key] = val
        else:
            dst[key] = val

def extend(dst, *args):
    """Recursively update a dictionary.

    Parameters
    ----------
    dst : `dict`
        Dictionary to update.
    *args : `dict`

    Returns
    -------
    `dict`
        Updated dictionary.

    Examples
    --------
    >>> extend({'x': {'y': 0}}, {'x': {'z': 1}})
    {'x': {'y': 0, 'z': 1}}
    """
    for src in args:
        _extend(dst, src)
    return dst

def truncate(string, maxlen, end=True):
    """Truncate a string.

    Parameters
    ----------
    string : `str`
        String to truncate.
    maxlen : `int`
        Maximum string length.
    end : `boolean`, optional
        Remove characters from the end (default: `True`).

    Raises
    ------
    ValueError
        If `maxlen` <= 3.

    Returns
    -------
    `str`
        Truncated string.

    Examples
    --------
    >>> truncate('str', 6)
    'str'
    >>> truncate('long string', 8)
    'long ...'
    >>> truncate('long string', 8, False)
    '...tring'
    """
    if maxlen <= 3:
        raise ValueError('maxlen <= 3')

    if len(string) <= maxlen:
        return string

    if end:
        return string[:maxlen - 3] + '...'

    return '...' + string[3 - maxlen:]


def state_size_dataset(sz):
    """Get dataset key part for state size.

    Parameters
    ----------
    sz : `int`
        State size.

    Returns
    -------
    `str`
        Dataset key part.
    """
    return '_ss%d' % sz


def level_dataset(lv):
    """Get dataset key part for level.

    Parameters
    ----------
    lv : `int`
        Level.

    Returns
    -------
    `str`
        Dataset key part.
    """
    return '_lv%d' % lv
