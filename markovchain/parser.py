from collections import deque
from itertools import repeat, islice, count

from .util import (
    SaveLoad, to_list, fill, load,
    state_size_dataset, level_dataset
)
from .scanner import Scanner


class ParserBase(SaveLoad):
    """Base parser class.

    Attributes
    ----------
    classes : `dict`
        Parser class group.

    Examples
    --------
    >>> parse = ParserBase(lambda data: zip(data, data[1:]))
    >>> list(parse(['a', 'b', 'c']))
    [('a', 'b'), ('b', 'c')]
    """

    classes = {}

    def __init__(self, parse=None):
        """Base parser constructor.

        Parameters
        ----------
        parse : `function`, optional
        """
        if parse is not None:
            self.parse = parse

    def __call__(self, data, part=False, dataset=''):
        """Parse data.

        Parameters
        ----------
        data
            Data to parse.
        part : `bool`, optional
            True if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').

        Returns
        -------
        `object`
            self.parse(data)
        """
        return self.parse(data)


class Parser(ParserBase):
    """Default parser class.

    Attributes
    ----------
    state : `deque` of `str`
        Parser state.
    state_size : `int`
        Maximum parser state size.
    reset_on_sentence_end : `bool`
        Reset parser state on `markovchain.scanner.Scanner.END` token.
    end : `bool`
        True if a sentence is not started.

    Examples
    --------
    >>> tokens = ['a', 'b', '.', Scanner.END, 'c', '.', Scanner.END]
    >>> parse = Parser()
    >>> [(list(state), next) for state, next in parse(tokens)]
    [([''], 'a'), (['a'], 'b'), (['b'], '.'),
     ([''], 'c'), (['c'], '.')]
    >>> parse.state_sizes = 2
    >>> [(list(state), next) for state, next in parse(tokens)]
    [(['', ''], 'a'), (['', 'a'], 'b'), (['a', 'b'], '.'),
     (['', ''], 'c'), (['', 'c'], '.')]
    >>> parse.state_sizes = [1, 2]
    >>> [(list(state), next) for state, next in parse(tokens)]
    [([''], 'a'), (['', ''], 'a'),
     (['a'], 'b'), (['', 'a'], 'b'),
     (['b'], '.'), (['a', 'b'], '.'),
     ([''], 'c'), (['', ''], 'c'),
     (['c'], '.'), (['', 'c'], '.')]
    """
    def __init__(self, state_sizes=None,
                 reset_on_sentence_end=True):
        """Default parser constructor.

        Parameters
        ----------
        state_sizes : `int` or `list` of `int`, optional
            Parser state size(s) (default: [1]).
        reset_on_sentence_end : `bool`, optional
            Reset parser state on `markovchain.scanner.Scanner.END` token (default: `True`).
        """
        super().__init__()
        self.state = None
        self.state_size = None
        self._state_sizes = None
        self.reset_on_sentence_end = reset_on_sentence_end
        self.end = True
        self.state_sizes = [1] if state_sizes is None else state_sizes

    @property
    def state_sizes(self):
        """`list` of `int` : Parser state sizes.
        """
        return self._state_sizes

    @state_sizes.setter
    def state_sizes(self, state_sizes):
        state_sizes = to_list(state_sizes)
        if self.state is None or self._state_sizes != state_sizes:
            if any(s <= 0 for s in state_sizes):
                raise ValueError('parser state size <= 0: {0}'
                                 .format(state_sizes))
            self.state_size = max(state_sizes)
            self._state_sizes = state_sizes
            self.reset(True)

    def reset(self, state_size_changed=False):
        """Reset parser state.

        Parameters
        ----------
        state_size_changed : `bool`, optional
            `True` if maximum state size changed (default: `False`).
        """
        if state_size_changed:
            self.state = deque(repeat('', self.state_size),
                               maxlen=self.state_size)
        else:
            self.state.extend(repeat('', self.state_size))
        self.end = True

    def __call__(self, data, part=False, dataset=''):
        """Parse tokens.

        Parameters
        ----------
        data : `generator` of (`str` or `markovchain.scanner.Scanner.END` or (`markovchain.scanner.Scanner.START`, `str`))
            Tokens to parse.
        part : `bool`, optional
            `True` if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').

        Returns
        -------
        generator of (`str`, `islice` of `str`, `str`)
            Link generator.
        """
        datasets = [
            dataset + state_size_dataset(ss)
            for ss in self.state_sizes
        ]
        for word in data:
            if isinstance(word, tuple):
                cmd, arg = word
                if cmd == Scanner.START:
                    self.reset()
                    self.state.append(arg)
                    self.end = False
                else:
                    raise ValueError('invalid parser input: {0}'.format(word))
            else:
                if word == Scanner.END and self.end:
                    continue
                for dataset, sz in zip(datasets, self.state_sizes):
                    start = self.state_size - sz
                    yield (
                        dataset,
                        islice(self.state, start, self.state_size),
                        word
                    )
                if word == Scanner.END:
                    if self.reset_on_sentence_end:
                        self.reset()
                        continue
                else:
                    self.state.append(word)
                    self.end = False

        if not part:
            self.reset()

    def __eq__(self, parser):
        return (self.reset_on_sentence_end == parser.reset_on_sentence_end
                and self.state_size == parser.state_size)

    def save(self):
        """Convert to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().save()
        data['state_sizes'] = self.state_sizes
        data['reset_on_sentence_end'] = self.reset_on_sentence_end
        return data


class LevelParser(ParserBase):
    """Multilevel parser class.
    """
    def __init__(self, levels=1, parsers=None):
        """Multilevel parser constructor.

        Parameters
        ----------
        levels : `int`
            Number of levels.
        parsers : `list` of `markovchain.parser.ParserBase`
            Level parsers.
        """
        super().__init__()
        self._parsers = None
        self._parsers_max = None
        self._levels = None
        self.levels = levels
        self.parsers = parsers

    @property
    def parsers(self):
        """`list` of `markovchain.parser.ParserBase` : Level parsers.
        """
        return self._parsers

    @parsers.setter
    def parsers(self, parsers):
        parsers = to_list(parsers)

        for i, parser in enumerate(parsers):
            parsers[i] = load(parser, Parser, Parser)

        if self.levels is not None:
            filled = fill(parsers, self.levels, True)
        else:
            filled = parsers

        self._parsers_max = parsers if len(parsers) > len(filled) else filled
        self._parsers = filled

    @property
    def levels(self):
        """`int` : Number of levels.
        """
        return self._levels

    @levels.setter
    def levels(self, levels):
        if levels <= 0:
            raise ValueError('level count <= 0')
        self._levels = levels
        if self._parsers_max is not None:
            self.parsers = self._parsers_max

    def reset(self):
        """Reset parser state.
        """
        for parser in self.parsers:
            parser.reset()

    def __call__(self, data, part=False, dataset=''):
        """Parse tokens.

        Parameters
        ----------
        data : `generator` of `generator` of (`str` or `markovchain.scanner.Scanner.END` or (`markovchain.scanner.Scanner.START`, `str`))
            Levels to parse.
        part : `bool`, optional
            `True` if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').

        Returns
        -------
        `generator` of (`str`, `islice` of `str`, `str`)
            Link generator.
        """
        #if part:
        #    raise NotImplementedError()
        for level, level_data, parser in zip(count(0), data, self.parsers):
            yield from parser(level_data, part, dataset + level_dataset(level))

    def __eq__(self, parser):
        return (self.levels == parser.levels
                and self.parsers == parser.parsers)

    def save(self):
        """Convert to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().save()
        data['levels'] = self.levels
        if self.parsers is None:
            data['parsers'] = None
        else:
            data['parsers'] = [parser.save() for parser in self.parsers]
        return data
