from itertools import chain, islice, tee

from ..scanner import CharScanner, RegExpScanner
from ..parser import Parser
from ..base import Markov
from .util import format_sentence


class MarkovText(Markov):
    """Markov text generator class.
    """

    DEFAULT_SCANNER = RegExpScanner
    DEFAULT_PARSER = Parser

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

    def do_format(self, string):
        """Format a sentence.

        Parameters
        ----------
        string : `str`
            Sentence to format.
        """
        return format_sentence(string)

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
        return self.do_format(string)

    def __call__(self,
                 max_length=None,
                 state_size=None,
                 start=None,
                 dataset=''):
        """Generate a sentence.

        Parameters
        ----------
        max_length : `int` or `None`, optional
            Maximum sentence length (default: None).
        state_size : `int`, optional
            State size (default: parser.state_sizes[0]).
        start : `None` or `str` or `iterable` of `str`, optional
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
            for _ in self.parser(self.scanner(start, True), True):
                pass
            state = list(self.parser.state)
            self.scanner.reset()
            self.parser.reset()
        elif start is not None:
            state, start = tee(start)
        else:
            state = None

        parts = self.generate(state_size, state, dataset)
        if max_length is not None:
            parts = islice(parts, 0, max_length)

        if isinstance(start, str):
            parts = chain((start,), parts)
        elif start is not None:
            parts = chain(start, parts)

        return self.format(parts)
