from unittest.mock import Mock, call
import pytest

from markovchain import Parser, LevelParser, Scanner
from markovchain.parser import ParserBase


def parse(parser, data, part=False, separator=' '):
    return [(dataset, separator.join(src), dst)
            for dataset, src, dst in parser(data, part)]


def test_parser_properties():
    parser = Parser()

    with pytest.raises(ValueError):
        parser.state_sizes = [1, 0, 2]
    with pytest.raises(ValueError):
        parser.state_sizes = []

    assert parser.state_sizes == [1]
    assert parser.state_size == 1

    parser.state_sizes = [2, 1]
    assert parser.state_sizes == [2, 1]
    assert parser.state_size == 2
    assert parser.state.maxlen == 2
    assert list(parser.state) == ['', '']

    parser.state.append('test')
    parser.state_size = parser.state_size
    assert list(parser.state) == ['', 'test']

    parser.state_sizes = [3]
    assert list(parser.state) == ['', '', '']

def test_parser_parse(mocker):
    state_size_dataset = mocker.patch(
        'markovchain.parser.state_size_dataset',
        return_value='0'
    )
    parser = Parser(state_sizes=[2], reset_on_sentence_end=False)
    res = parse(parser, ['a', Scanner.END, 'b'], True, '::')
    assert res == [('0', '::', 'a'), ('0', '::a', None), ('0', '::a', 'b')]
    res = parse(parser, 'c', separator='::')
    assert res == [('0', 'a::b', 'c')]
    state_size_dataset.assert_has_calls(
        call(parser.state_sizes[0]) for _ in range(2)
    )

def test_parser_parse_default(mocker):
    state_size_dataset = mocker.patch(
        'markovchain.parser.state_size_dataset',
        return_value='0'
    )
    parser = Parser()
    assert parse(parser, '') == []
    assert parse(parser, 'abc', True) == [
        ('0', '', 'a'), ('0', 'a', 'b'), ('0', 'b', 'c')
    ]
    assert parse(parser, ['a', 'b', Scanner.END, 'c']) == [
        ('0', 'c', 'a'), ('0', 'a', 'b'), ('0', 'b', None), ('0', '', 'c')
    ]
    assert parse(parser, ['a', Scanner.END, Scanner.END, 'c']) == [
        ('0', '', 'a'), ('0', 'a', None), ('0', '', 'c')
    ]
    assert parse(parser, [Scanner.END] * 4) == []
    state_size_dataset.assert_has_calls(
        call(parser.state_sizes[0]) for _ in range(4)
    )

@pytest.mark.parametrize('test,res', [
    ('abcde', [('0', '  ', 'a'),
               ('0', '  a', 'b'), ('0', ' a b', 'c'),
               ('0', 'a b c', 'd'), ('0', 'b c d', 'e')]),
    (['a', 'b', 'c', Scanner.END, 'd', 'e'],
     [('0', '  ', 'a'), ('0', '  a', 'b'),
      ('0', ' a b', 'c'), ('0', 'a b c', None),
      ('0', '  ', 'd'), ('0', '  d', 'e')]),
    (['a', 'b', 'c', (Scanner.START, 'd'), 'e'],
     [('0', '  ', 'a'), ('0', '  a', 'b'),
      ('0', ' a b', 'c'), ('0', '  d', 'e')])
])
def test_parser_state_size(mocker, test, res):
    state_size_dataset = mocker.patch(
        'markovchain.parser.state_size_dataset',
        return_value='0'
    )
    parser = Parser(state_sizes=[3])
    assert parse(parser, test) == res
    state_size_dataset.assert_called_once_with(3)

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    (([2], False), ([2], False), True),
    (([2], False), ([2], True), False),
    (([2], False), ([2, 3], False), False)
])
def test_parser_eq(test, test2, res):
    parser = Parser(*test)
    parser2 = Parser(*test2)
    assert (parser == parser2) == res

@pytest.mark.parametrize('test', [
    ([1, 2, 3], False)
])
def test_parser_save_load(test):
    parser = Parser(*test)
    saved = parser.save()
    loaded = Parser.load(saved)
    assert parser == loaded


def test_level_parser_properties():
    parser = LevelParser()
    assert parser.levels == 1
    assert parser.parsers == [Parser()]

    with pytest.raises(ValueError):
        parser.levels = 0
    with pytest.raises(ValueError):
        parser.levels = -1
    assert parser.levels == 1

    parser.levels = 2
    assert parser.parsers == [Parser(), Parser()]

    level = Parser(state_sizes=[2, 3])
    parser.parsers = level
    assert parser.parsers == [level, level]

    parser.parsers = [Parser(), level, Parser()]
    assert parser.parsers == [Parser(), level]

    parser.levels = 1
    assert parser.parsers == [Parser()]

    parser.levels = 2
    assert parser.parsers[1] is level

def test_level_parser_reset():
    parsers = [Mock(), Mock()]
    parser = LevelParser(levels=2, parsers=parsers)
    parser.reset()
    for level in parsers:
        level.reset.assert_called_once_with()

@pytest.mark.parametrize('test,res', [
    ([[0], [1]], [0, 1]),
    ([[0]] * 5, [0, 1]),
    ([], [])
])
def test_level_parser_parse(mocker, test, res):
    level_dataset = mocker.patch(
        'markovchain.parser.level_dataset',
        return_value='0'
    )
    parsers = [
        Mock(wraps=ParserBase(lambda x: [0])),
        Mock(wraps=ParserBase(lambda x: [1]))
    ]
    parser = LevelParser(
        levels=2,
        parsers=parsers
    )
    assert list(parser(test, dataset='data')) == res
    if test:
        assert level_dataset.call_count == 2
        level_dataset.assert_has_calls([call(0), call(1)])
    for parser, data in zip(parsers, test):
        parser.assert_called_once_with(data, False, 'data0')

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((2, Parser()), (2, Parser()), True),
    ((1,), (2,), False),
    ((2, [Parser(), Parser(3)]), (2, Parser()), False)
])
def test_level_parser_eq(test, test2, res):
    assert (LevelParser(*test) == LevelParser(*test2)) == res

def test_level_parser_save_load():
    level = Parser(state_sizes=[2, 3])
    parser = LevelParser(levels=3, parsers=[level, Parser()])
    saved = parser.save()
    loaded = Parser.load(saved)
    assert parser == loaded
