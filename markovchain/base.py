from collections import deque
from itertools import chain, repeat

from .scanner import Scanner, RegExpScanner
from .parser import ParserBase, Parser
from .util import load


class MarkovBase:
    """Base markov chain generator class.

    Attributes
    ----------
    DEFAULT_SCANNER : `type`
        Default scanner class.
    DEFAULT_PARSER : `type`
        Default parser class.
    scanner : `markovchain.scanner.Scanner`
    parser : `markovchain.parser.ParserBase`
    """
    DEFAULT_SCANNER = RegExpScanner
    DEFAULT_PARSER = Parser

    def __init__(self, separator=' ', scanner=None, parser=None):
        """Base markov chain generator constructor.

        Attributes
        ----------
        separator : `str`, optional
            State separator (default: ' ').
        scanner : `dict` or `markovchain.scanner.Scanner`, optional
            Scanner (default: `markovchain.base.MarkovBase.DEFAULT_SCANNER()`).
        parser : `dict` or `markovchain.parser.ParserBase`, optional
            Parser (default: `markovchain.base.MarkovBase.DEFAULT_PARSER()`).
        """
        self._separator = None
        self.separator = separator
        self.scanner = load(scanner, Scanner, self.DEFAULT_SCANNER)
        self.parser = load(parser, ParserBase, self.DEFAULT_PARSER)

    @property
    def separator(self):
        """`str` : State separator.
        """
        return self._separator

    @separator.setter
    def separator(self, separator):
        old_separator = self._separator
        if old_separator is not None:
            self.replace_state_separator(old_separator, separator)
        self._separator = separator

    def __eq__(self, markov):
        return (self.separator == markov.separator
                and self.scanner == markov.scanner
                and self.parser == markov.parser)

    def data(self, data, part=False):
        """Parse data and update links.

        Parameters
        ----------
        data
            Data to parse.
        part : `bool`, optional
            True if data is partial (default: `False`).
        """
        #if self.parser is None:
        #    raise ValueError('no parser')

        self.links(self.parser(self.scanner(data, part), part))

    def generate(self, maxlength, state_size=None, start=None):
        """Generate a sentence.

        Parameters
        ----------
        maxlength : `int`
            Maximum sentence length.
        state_size : `int`, optional
            State size (default: parser.state_sizes[0]).
        start : `list` of `str`, optional
            Starting state (default: []).

        Returns
        -------
        `generator` of `str`
            Word generator.
        """
        if maxlength <= 0:
            return

        if state_size is None:
            if self.parser is None:
                raise ValueError('parser is None and state_size is None')
            try:
                state_size = next(iter(self.parser.state_sizes))
            except StopIteration:
                return
        #elif (self.parser is not None
        #      and state_size not in self.parser.state_sizes):
        #    raise ValueError('invalid state size: {0}: not in {1}'
        #                     .format(state_size, self.parser.state_sizes))

        if start is None:
            start = self.separator.join(repeat('', state_size))
            state = repeat('', state_size)
        else:
            if isinstance(start, str):
                start = start.split(self.separator)
            state = chain(repeat('', state_size), start)

        state = deque(state, maxlen=state_size)

        for _ in range(maxlength):
            link, state = self.random_link(state)
            if link is None:
                return
            yield link

    def get_save_data(self):
        """Convert generator settings to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        return {
            'separator': self.separator,
            'scanner': None if self.scanner is None else self.scanner.save(),
            'parser': None if self.parser is None else self.parser.save()
        }

    def replace_state_separator(self, old_separator, new_separator):
        """Replace state separator.

        Parameters
        ----------
        old_separator : `str`
            Old state separator.
        new_separator : `str`
            New state separator.
        """
        pass

    def links(self, links):
        """Update links.

        Parameters
        ----------
        links : `generator` of (`islice` of `str`, `str`)
            Links to add.

        Raises
        -------
        NotImplementedError
            If data mixin is missing.
        """
        raise NotImplementedError('missing data mixin')

    def random_link(self, state):
        """Get a random link.

        Parameters
        ----------
        state
            Link source.

        Raises
        -------
        NotImplementedError
            If data mixin is missing.
        """
        raise NotImplementedError('missing data mixin')

    @classmethod
    def load(cls, *args, **kwargs):
        """Load a generator.

        Raises
        -------
        NotImplementedError
            If data mixin is missing.
        """
        raise NotImplementedError('missing data mixin')

    def save(self, *args, **kwargs):
        """Save the generator.

        Raises
        -------
        NotImplementedError
            If data mixin is missing.
        """
        raise NotImplementedError('missing data mixin')
