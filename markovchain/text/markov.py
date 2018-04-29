import random
from itertools import chain, islice, cycle

from .formatter import FormatterBase, Formatter
from .rank import Rank, Const
from .scanner import RegExpScanner
from .util import get_words, ReplyMode
from ..parser import Parser
from ..base import Markov
from ..util import load, state_size_dataset


class MarkovText(Markov):
    """Markov text generator class.
    """

    DEFAULT_SCANNER = RegExpScanner
    DEFAULT_PARSER = Parser
    DEFAULT_FORMATTER = Formatter
    DEFAULT_RANK = Const

    def __init__(self,
                 scanner=None,
                 parser=None,
                 storage=None,
                 formatter=None,
                 rank=None):
        super().__init__(scanner, parser, storage)
        self.rank = load(rank, Rank, self.DEFAULT_RANK)
        self.formatter = load(formatter, FormatterBase, self.DEFAULT_FORMATTER)

    def __eq__(self, markov):
        return (super().__eq__(markov)
                and self.rank == markov.rank
                and self.formatter == markov.formatter)

    def get_settings_json(self):
        data = super().get_settings_json()
        data['rank'] = self.rank.save()
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
        """Format generated text.

        Parameters
        ----------
        parts : `iterable` of `str`
            Text parts.
        """
        text = self.storage.state_separator.join(parts)
        return self.formatter(text)

    def get_cont_state(self, string, backward=False):
        """Get initial states from input string.

        Parameters
        ----------
        string : `str` or `None`
        backward : `bool`

        Returns
        -------
        `tuple` of `str`
        """
        if string is None:
            return ()
        for _ in self.parser(self.scanner(string, True), True):
            if backward and len(self.parser.state[0]):
                break
        state = tuple(self.parser.state)
        self.scanner.reset()
        self.parser.reset()
        return state

    def get_reply_states(self, string, dataset):
        """Get initial states from input string.

        Parameters
        ----------
        string : `str`
            Input string.
        dataset : `str`
            Dataset key.

        Returns
        -------
        `list` of `list` of `str`
        """
        words = get_words(string)
        if not words:
            return []
        long_word = 4
        long_words = [word for word in words if len(word) >= long_word]
        short_words = [word for word in words if len(word) < long_word]
        for words in (long_words, short_words):
            ret = [
                states
                for states in (
                    self.storage.get_states(dataset, word)
                    for word in words
                )
                if states
            ]
            if ret:
                return ret
        return []

    def generate_cont(self, max_length, state_size,
                      reply_to, backward, dataset):
        """Generate texts from start/end.

        Parameters
        ----------
        max_length : `int` or `None`
            Maximum sentence length.
        state_size : `int`
            State size.
        reply_to : `str` or `None`
            Input string.
        backward : `bool`
            `True` to generate text start.
        dataset: `str`
            Dataset key prefix.

        Returns
        -------
        `generator` of `str`
            Generated texts.
        """
        state = self.get_cont_state(reply_to, backward)
        while True:
            parts = self.generate(state_size, state, dataset, backward)
            if reply_to is not None:
                if backward:
                    parts = chain(reversed(list(parts)), (reply_to,))
                else:
                    parts = chain((reply_to,), parts)
            parts = islice(parts, 0, max_length)
            yield self.format(parts)

    def generate_replies(self, max_length, state_size, reply_to, dataset):
        """Generate replies.

        Parameters
        ----------
        max_length : `int` or `None`
            Maximum sentence length.
        state_size : `int`
            State size.
        reply_to : `str`
            Input string.
        dataset: `str`
            Dataset key prefix.

        Returns
        -------
        `generator` of `str`
            Generated texts.
        """
        state_sets = self.get_reply_states(
            reply_to,
            dataset + state_size_dataset(state_size)
        )

        if not state_sets:
            yield from self.generate_cont(max_length, state_size,
                                          None, False, dataset)
            return

        random.shuffle(state_sets)

        generate = lambda state, backward: self.generate(
            state_size, state,
            dataset, backward
        )

        for states in cycle(state_sets):
            state = random.choice(states)
            parts = chain(
                reversed(list(generate(state, True))),
                (state,),
                generate(state, False)
            )
            parts = islice(parts, 0, max_length)
            yield self.format(parts)

    def __call__(self,
                 max_length=None,
                 state_size=None,
                 reply_to=None,
                 reply_mode=ReplyMode.END,
                 dataset=''):
        """Generate text.

        Parameters
        ----------
        max_length : `int` or `None`, optional
            Maximum sentence length (default: None).
        state_size : `int`, optional
            State size (default: parser.state_sizes[0]).
        reply_to : `str` or `None`, optional
            Input string (default: None).
        reply_mode : `markovchain.text.util.ReplyMode`, optional
            Reply mode (default: `markovchain.text.util.ReplyMode.END`)
        dataset: `str`, optional
            Dataset key prefix (default: '').

        Returns
        -------
        `str`
        """
        if reply_to is None:
            reply_mode = ReplyMode.END

        if state_size is None:
            state_size = next(iter(self.parser.state_sizes))

        if max_length is not None and max_length <= 0:
            return self.format('')

        if reply_mode == ReplyMode.REPLY:
            text = self.generate_replies(max_length, state_size,
                                         reply_to, dataset)
        else:
            backward = reply_mode == ReplyMode.START
            text = self.generate_cont(max_length, state_size,
                                      reply_to, backward, dataset)

        text = islice(text, 0, self.rank.size)
        text = self.rank(text)
        return random.choice(text)
