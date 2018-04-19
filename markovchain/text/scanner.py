import re
from abc import abstractmethod

from .util import CharCase
from ..scanner import Scanner
from ..util import int_enum


class TextScanner(Scanner):
    """Text scanner base class.

    Attributes
    ----------
    case : `markovchain.text.util.CharCase`
        Character case.
    """
    def __init__(self, case=CharCase.LOWER):
        """Text scanner constructor.

        Parameters
        ----------
        case : `str` or `int` or `markovchain.text.util.CharCase`, optional
            Character case (default: markovchain.text.util.CharCase.LOWER).
        """
        super().__init__()
        self.case = int_enum(CharCase, case)

    def __eq__(self, scanner):
        return self.case == scanner.case

    def __call__(self, data, part=False):
        """Scan a string.

        Parameters
        ----------
        data : `str`
            String to scan.
        part : `bool`, optional
            True if data is partial (default: `False`).

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END`)
            Token generator.
        """
        data = self.case.convert(data)
        return self.scan(data, part)

    def save(self):
        data = super().save()
        data['case'] = self.case
        return data

    @abstractmethod
    def scan(self, data, part):
        """Scan a string.

        Parameters
        ----------
        data : `str`
            String to scan.
        part : `bool`
            True if data is partial.

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END`)
            Token generator.
        """
        pass


class CharScanner(TextScanner):
    """Character scanner.

    Attributes
    ----------
    case : `markovchain.text.util.CharCase`
        Character case.
    end_chars : `str`
        Sentence ending characters.
    default_end : `str`
        Default sentence ending character.
    start : `bool`
        True if current sentence is started.
    end : `bool`
        True if current sentence is ended.

    Examples
    --------
    >>> scan = CharScanner()
    >>> list(scan('Word'))
    ['W', 'o', 'r', 'd', '.', Scanner.END]
    >>> list(scan('Word', True))
    ['W', 'o', 'r', 'd']
    >>> list(scan(''))
    ['.', Scanner.END]
    """
    def __init__(self, end_chars='.?!', default_end='.', case=CharCase.LOWER):
        """Character scanner constructor.

        Parameters
        ----------
        case : `str` or `int` or `markovchain.text.util.CharCase`, optional
            Character case (default: markovchain.text.util.CharCase.LOWER).
        end_chars : `str`, optional
            Sentence ending characters (default: '.?!').
        default_end : `str`, optional
            Default sentence ending character (default: '.').
        """
        super().__init__(case)
        self.end_chars = end_chars
        self.default_end = default_end
        self.start = False
        self.end = False

    def __eq__(self, scanner):
        return (super().__eq__(scanner)
                and self.end_chars == scanner.end_chars
                and self.default_end == scanner.default_end)

    def reset(self):
        """Reset scanner state.
        """
        self.start = False
        self.end = False

    def scan(self, data, part):
        """Scan a string.

        Parameters
        ----------
        data : `str`
            String to scan.
        part : `bool`
            True if data is partial.

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END`)
            Token generator.
        """
        if not self.end_chars:
            yield from data
            self.start = self.start or bool(data)
            self.end = False
        else:
            for char in data:
                if char in self.end_chars:
                    if not self.start:
                        continue
                    self.end = True
                else:
                    if self.end:
                        yield self.END
                        self.end = False
                    self.start = True
                yield char

        if not part and self.start:
            if not self.end and self.default_end is not None:
                yield self.default_end
            yield self.END
            self.reset()

    def save(self):
        """Convert to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().save()
        data['end_chars'] = self.end_chars
        data['default_end'] = self.default_end
        return data


class RegExpScanner(TextScanner):
    """Regular expression scanner.

    Attributes
    ----------
    DEFAULT_EXPR : `_sre.SRE_Pattern`
        Default regular expression.
    case : `markovchain.text.util.CharCase`
        Character case.
    expr : `_sre.SRE_Pattern`
        Regular expression..
    default_end : `str`
        Default sentence ending string.
    end : `bool`
        `True` if current sentence is ended.

    Examples
    --------
    >>> scan = RegExpScanner(lambda data: data.split())
    >>> list(scan('Word word. word'))
    ['Word', 'word', '.', Scanner.END, 'word', '.', Scanner.END]
    >>> list(scan('word', True))
    ['word']
    >>> list(scan(''))
    ['.', Scanner.END]
    """

    DEFAULT_EXPR = re.compile(
        r'(?:(?P<end>[.!?]+)|(?P<word>(?:[^\w\s]+|\w+)))'
    )

    def __init__(self, expr=DEFAULT_EXPR, default_end='.', case=CharCase.LOWER):
        """Regular expression scanner constructor.

        Parameters
        ----------
        case : `str` or `int` or `markovchain.text.util.CharCase`, optional
            Character case (default: markovchain.text.util.CharCase.LOWER).
        expr : `str` or `_sre.SRE_Pattern`, optional
            Regular expression (default: `markovchain.scanner.RegExpScanner.DEFAULT_EXPR`).
            It should have groups 'end' (sentence ending punctuation)
            and 'word' (words / other punctuation).
        default_end : `str`, optional
            Default sentence ending string (default: '.').
        """
        super().__init__(case)
        self.expr = self.get_regexp(expr)
        self.default_end = default_end
        self.end = True

    def __eq__(self, scanner):
        return (super().__eq__(scanner)
                and self.expr == scanner.expr
                and self.default_end == scanner.default_end)

    def reset(self):
        """Reset scanner state.
        """
        self.end = True

    def scan(self, data, part):
        """Scan a string.

        Parameters
        ----------
        data : `str`
            String to scan.
        part : `bool`
            `True` if data is partial.

        Returns
        -------
        `generator` of (`str` or `markovchain.scanner.Scanner.END`)
            Token generator.
        """
        if not self.expr.groups:
            for match in self.expr.finditer(data):
                yield match.group()

            self.end = self.end and not bool(data)
        else:
            for match in self.expr.finditer(data):
                group = self.get_group(match, 'end')
                if group is not None:
                    if not self.end:
                        yield group
                        yield self.END
                        self.end = True
                else:
                    self.end = False
                    group = self.get_group(match, 'word')
                    if group is not None:
                        yield group
                    else:
                        yield match.group()

        if not part and not self.end:
            if self.default_end is not None:
                yield self.default_end
            yield self.END
            self.reset()

    def save(self):
        """Convert the scanner to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().save()
        data['expr'] = self.expr.pattern
        data['default_end'] = self.default_end
        return data

    @staticmethod
    def get_regexp(x):
        """Compile a regular expression if necessary.

        Parameters
        ----------
        x : `str` or `_sre.SRE_Pattern`
            Regular expression.

        Returns
        -------
        `_sre.SRE_Pattern`
            Compiled regular expression.
        """
        if isinstance(x, str):
            return re.compile(x)
        return x

    @staticmethod
    def get_group(match, group):
        """Get a group from a regular expression match object if it exists.

        Parameters
        ----------
        match : `_sre.SRE_Match`
            Regular expression match object.
        group : `str` or `int`
            Group name or index.

        Returns
        -------
        `str` or `None`
        """
        try:
            return match.group(group)
        except IndexError:
            return None
