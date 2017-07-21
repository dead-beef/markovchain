from itertools import islice, repeat
from copy import deepcopy


class SaveLoad:
    classes = {}

    @classmethod
    def add_class(cls, *args):
        for cls2 in args:
            cls.classes[cls2.__name__] = cls2

    @classmethod
    def remove_class(cls, *args):
        for cls2 in args:
            try:
                del cls.classes[cls2.__name__]
            except KeyError:
                pass

    @classmethod
    def load(cls, data):
        ret = cls.classes[data['__class__']]
        data_cls = data['__class__']
        del data['__class__']
        try:
            ret = ret(**data)
        finally:
            data['__class__'] = data_cls
        return ret

    def save(self):
        return {
            '__class__': self.__class__.__name__
        }


class ObjectWrapper: # pylint:disable=too-few-public-methods
    def __init__(self, obj):
        self.__class__ = type(
            obj.__class__.__name__,
            (self.__class__, obj.__class__),
            {}
        )
        self.__dict__ = obj.__dict__


def const(x):
    return lambda *args: x

def to_list(x):
    if isinstance(x, list):
        return x
    if not isinstance(x, dict):
        try:
            return list(x)
        except TypeError:
            pass
    return [x]

def fill(xs, length, copy=False):
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

def load(obj, cls, default_factory):
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
    for src in args:
        _extend(dst, src)
    return dst

def truncate(string, maxlen, end=True):
    if maxlen <= 3:
        raise ValueError('maxlen <= 3')

    if len(string) <= maxlen:
        return string

    if end:
        return string[:maxlen - 3] + '...'

    return '...' + string[3 - maxlen:]
