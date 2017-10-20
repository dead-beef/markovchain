import re

from .util import SaveLoad


class Scanner(SaveLoad):
    """Base scanner class.

    Attributes
    ----------
    classes : `dict`
        Scanner class group.
    START
        Sentence start token.
    END
        Sentence end token.

    Examples
    --------
    >>> scan = Scanner(lambda data: data.split())
    >>> scan('a b c')
    ['a', 'b', 'c']
    """

    classes = {}

    END = None
    START = None

    def __init__(self, scan=None):
        """Base scanner constructor.

        Parameters
        ----------
        scan : `function`, optional
        """
        if scan is not None:
            self.scan = scan

    def __call__(self, data, part=False):
        """Scan data.

        Parameters
        ----------
        data
            Data to scan.
        part : `bool`, optional
            `True` if data is partial (default: `False`).

        Returns
        -------
        `object`
            self.scan(data)
        """
        return self.scan(data)

    def reset(self):
        """Reset scanner state.
        """
        pass


class CharScanner(Scanner):
    """Character scanner.

    Attributes
    ----------
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
    def __init__(self, end_chars='.?!', default_end='.'):
        """Character scanner constructor.

        Parameters
        ----------
        end_chars : `str`, optional
            Sentence ending characters (default: '.?!').
        default_end : `str`, optional
            Default sentence ending character (default: '.').
        """
        super().__init__()
        self.end_chars = end_chars
        self.default_end = default_end
        self.start = False
        self.end = False

    def reset(self):
        """Reset scanner state.
        """
        self.start = False
        self.end = False

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

    def __eq__(self, scanner):
        return (self.end_chars == scanner.end_chars
                and self.default_end == scanner.default_end)

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


class RegExpScanner(Scanner):
    """Regular expression scanner.

    Attributes
    ----------
    DEFAULT_EXPR : `_sre.SRE_Pattern`
        Default regular expression.
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

    def __init__(self, expr=DEFAULT_EXPR, default_end='.'):
        """Regular expression scanner constructor.

        Parameters
        ----------
        expr : `str` or `_sre.SRE_Pattern`, optional
            Regular expression (default: `markovchain.scanner.RegExpScanner.DEFAULT_EXPR`).
            It should have groups 'end' (sentence ending punctuation)
            and 'word' (words / other punctuation).
        default_end : `str`, optional
            Default sentence ending string (default: '.').
        """
        super().__init__()
        self.expr = self.get_regexp(expr)
        self.default_end = default_end
        self.end = True

    def reset(self):
        """Reset scanner state.
        """
        self.end = True

    def __call__(self, data, part=False):
        """Scan a string.

        Parameters
        ----------
        data : `str`
            String to scan.
        part : `bool`, optional
            `True` if data is partial (default: `False`).

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

    def __eq__(self, scanner):
        return (self.expr == scanner.expr
                and self.default_end == scanner.default_end)

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
