from itertools import chain, islice, tee

from .format import FormatterBase, Formatter
from .scanner import CharScanner, RegExpScanner
from ..parser import Parser
from ..base import Markov
from ..util import load


class MarkovText(Markov):
    """Markov text generator class.
    """

    DEFAULT_SCANNER = RegExpScanner
    DEFAULT_PARSER = Parser
    DEFAULT_FORMATTER = Formatter

    def __init__(self,
                 scanner=None,
                 parser=None,
                 storage=None,
                 formatter=None):
        super().__init__(scanner, parser, storage)
        self.formatter = load(formatter, FormatterBase, self.DEFAULT_FORMATTER)

    def __eq__(self, markov):
        return (super().__eq__(markov)
                and self.formatter == markov.formatter)

    def get_settings_json(self):
        data = super().get_settings_json()
        data['formatter'] = self.formatter.save()
        return data

    def data(self, data, part=False, dataset=''):
        """
        Parameters
        ----------
        data : `str`
            Text to parse.
        part : `bool`, optional
            True if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').
        """
        return super().data(data, part)

    def format(self, parts):
        """Format a sentence.

        Parameters
        ----------
        parts : `iterable` of `str`
            Sentence parts.
        """
        try:
            string = self.scanner.join(parts)
        except AttributeError:
            if isinstance(self.scanner, CharScanner):
                join_with = ''
            else:
                join_with = ' '
            string = join_with.join(parts)
        return self.formatter(string)

    def parse_state(self, string):
        """
        Parameters
        ----------
        string : `str`

        Returns
        -------
        `list` of `str`
        """
        for _ in self.parser(self.scanner(string, True), True):
            pass
        state = list(self.parser.state)
        self.scanner.reset()
        self.parser.reset()
        return state

    def __call__(self,
                 max_length=None,
                 state_size=None,
                 start=(),
                 dataset=''):
        """Generate a sentence.

        Parameters
        ----------
        max_length : `int` or `None`, optional
            Maximum sentence length (default: None).
        state_size : `int`, optional
            State size (default: parser.state_sizes[0]).
        start : `str` or `iterable` of `str`, optional
            Starting state (default: []).
        dataset: `str`, optional
            Dataset key prefix (default: '').

        Returns
        -------
        `str`
            Generated sentence.
        """
        if max_length is not None and max_length <= 0:
            return self.format('')

        if isinstance(start, str):
            state = self.parse_state(start)
        else:
            state, start = tee(start)

        parts = self.generate(state_size, state, dataset)
        if max_length is not None:
            parts = islice(parts, 0, max_length)

        if isinstance(start, str):
            parts = chain((start,), parts)
        elif start is not None:
            parts = chain(start, parts)

        return self.format(parts)
