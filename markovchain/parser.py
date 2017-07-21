from collections import deque
from itertools import repeat, islice

from .util import SaveLoad, to_list, fill, load
from .scanner import Scanner


class ParserBase(SaveLoad):
    classes = {}

    def __init__(self, parse=None):
        if parse is not None:
            self.parse = parse

    def __call__(self, data, part=False):
        return self.parse(data)


class Parser(ParserBase):
    def __init__(self, state_sizes=None,
                 reset_on_sentence_end=True):
        super().__init__()
        self.state = None
        self.state_size = None
        self._state_sizes = None
        self.reset_on_sentence_end = reset_on_sentence_end
        self.end = True
        self.state_sizes = [1] if state_sizes is None else state_sizes

    @property
    def state_sizes(self):
        return self._state_sizes

    @state_sizes.setter
    def state_sizes(self, state_sizes):
        if self.state is None or self._state_sizes != state_sizes:
            if any(s <= 0 for s in state_sizes):
                raise ValueError('parser state size <= 0: {0}'.format(state_sizes))
            self.state_size = max(state_sizes)
            self._state_sizes = state_sizes
            self.reset(True)

    def reset(self, state_size_changed=False):
        if state_size_changed:
            self.state = deque(repeat('', self.state_size),
                               maxlen=self.state_size)
        else:
            self.state.extend(repeat('', self.state_size))
        self.end = True

    def __call__(self, data, part=False):
        for word in data:
            if isinstance(word, tuple):
                cmd, arg = word
                if cmd == Scanner.START:
                    self.reset()
                    self.state.append(arg)
                    self.end = False
                else:
                    raise ValueError('invalid parser input: {0}'.format(word))
            elif word == Scanner.END:
                if not self.end and self.reset_on_sentence_end:
                    self.reset()
                self.end = True
            else:
                for sz in self.state_sizes:
                    start = self.state_size - sz
                    yield islice(self.state, start, self.state_size), word
                self.state.append(word)
                self.end = False

        if not part:
            self.reset()

    def __eq__(self, parser):
        return (self.reset_on_sentence_end == parser.reset_on_sentence_end
                and self.state_size == parser.state_size)

    def save(self):
        data = super().save()
        data['state_sizes'] = self.state_sizes
        data['reset_on_sentence_end'] = self.reset_on_sentence_end
        return data


class LevelParser(ParserBase):
    def __init__(self, levels=1, parsers=None):
        super().__init__()
        self._parsers = None
        self._parsers_max = None
        self._levels = None
        self.levels = levels
        self.parsers = parsers

    @property
    def parsers(self):
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
        return self._levels

    @levels.setter
    def levels(self, levels):
        if levels <= 0:
            raise ValueError('level count <= 0')
        self._levels = levels
        if self._parsers_max is not None:
            self.parsers = self._parsers_max

    def reset(self):
        for parser in self.parsers:
            parser.reset()

    def __call__(self, data, part=False):
        if part:
            raise NotImplementedError()
        for level, parser in zip(data, self.parsers):
            yield from parser(level, part)

    def __eq__(self, parser):
        return (self.levels == parser.levels
                and self.parsers == parser.parsers)

    def save(self):
        data = super().save()
        data['levels'] = self.levels
        if self.parsers is None:
            data['parsers'] = None
        else:
            data['parsers'] = [parser.save() for parser in self.parsers]
        return data
