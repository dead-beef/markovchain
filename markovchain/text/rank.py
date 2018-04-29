import sys
import math
from abc import abstractmethod
from itertools import chain, islice

from ..util import SaveLoad
from ..text.util import get_words


class Rank(SaveLoad):
    """Base text rank class.

    Attributes
    ----------
    size : `int`
    remove : `float`
    debug : `bool`
        If True, enable debug output.
    """
    classes = {}

    def __init__(self, size=10, remove=0.5):
        if size <= 0:
            raise ValueError('rank size <= 0')
        self.size = size
        self.remove = remove
        self.debug = False

    def __eq__(self, rank):
        return (super().__eq__(self, rank)
                and self.size == rank.size
                and abs(self.remove - rank.remove) < 1e-5)

    def save(self):
        ret = super().save()
        ret['size'] = self.size
        ret['remove'] = self.remove
        return ret

    @abstractmethod
    def rank(self, string):
        """Rank a string.

        Parameters
        ----------
        string : `str`

        Returns
        -------
        `float`
        """
        pass

    def __call__(self, strings):
        """Filter strings by rank.

        Parameters
        ----------
        strings : `iterable` of `str`
            Strings to filter.

        Returns
        -------
        `list` of `str`
            Filtered list.
        """
        strings = sorted(
            ((string, self.rank(string)) for string in strings),
            key=lambda x: -x[1]
        )
        end = max(1, len(strings) - int(self.remove * len(strings)))
        res = [string for string, rank in islice(strings, 0, end)]
        if self.debug:
            print(res, file=sys.stderr)
        return res


class Const(Rank):
    """Constant text rank."""
    def __init__(self, **_):
        super().__init__(1, 0.0)

    def rank(self, string):
        return 1


class Test(Rank):
    def __init__(self, size, remove):
        super().__init__(size=10, remove=0.5)
        self.header = False
        self.opt_words = 8
        self.opt_long_words = 4
        self.opt_long_word_ratio = 0.6
        self.long_word_length = 4

    def features(self, string):
        words = get_words(string)
        nwords = len(words)
        nlongwords = sum(
            1 for word in words
            if len(word) >= self.long_word_length
        )
        return [
            1 - abs(1 - nwords / self.opt_words),
            1 - abs(1 - nlongwords / self.opt_long_words) ** 2,
            #len(set(words)) / nwords,
            1 - abs(1 - nlongwords / nwords / self.opt_long_word_ratio)
        ]

    def log(self, res, features, string):
        if not self.header:
            self.header = True
            fmt = ' Rank     ' + '  %02d      ' * len(features)
            print(fmt % tuple(range(len(features))), file=sys.stderr)
        fmt = '%.04f    ' * (len(features) + 1) + '%s'
        print(fmt % tuple(chain((res,), features, (string,))), file=sys.stderr)

    def rank(self, string):
        features = self.features(string)
        for i, x in enumerate(features):
            features[i] = min(1, max(0, x))
        ret = sum(features) / len(features)
        if self.debug:
            self.log(ret, features, string)
        return ret

    def __call__(self, strings):
        self.header = False
        return super().__call__(strings)
