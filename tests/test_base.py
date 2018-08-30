from collections import deque
from unittest.mock import Mock, call
import pytest

from markovchain import Markov
from markovchain.parser import ParserBase
from markovchain.scanner import Scanner


def test_markov_base_properties():
    storage = Mock(settings={})
    markov = Markov(storage=storage)
    assert isinstance(markov.parser, ParserBase)
    assert isinstance(markov.scanner, Scanner)
    assert markov.storage is storage

@pytest.mark.parametrize('data,part,dataset', [
    ([], False, ''),
    ([1, 2, 3], True, 'data')
])
def test_markov_base_data(data, part, dataset):
    storage = Mock(settings={})
    scanner = Mock(return_value=0)
    parser = Mock(return_value=1)
    markov = Markov(parser=parser, scanner=scanner, storage=storage)
    markov.data(data, part, dataset)
    scanner.assert_called_once_with(data, part)
    parser.assert_called_once_with(0, part, dataset)
    storage.add_links.assert_called_once_with(1)

@pytest.mark.parametrize('state_sizes, args, call', [
    ([1], (1, 'x', 'd'), ('x', 1, 'd_1', False)),
    ([2, 1], (None, 'y', 'dd', True), ('y', 2, 'dd_2', True)),
    ([], (None, 'y', 'dd'), None)
])
def test_markov_base_generate(mocker, state_sizes, args, call):
    mocker.patch(
        'markovchain.base.state_size_dataset',
        wraps=lambda ss: '_%d' % ss
    )
    markov = Markov(
        parser=Mock(state_sizes=state_sizes),
        scanner=Mock(),
        storage=Mock(generate=Mock(return_value=0))
    )
    res = markov.generate(*args)
    if call is not None:
        assert res == 0
        markov.storage.generate.assert_called_with(*call)
    else:
        assert res is None
        assert markov.storage.generate.call_count == 0

def test_markov_base_get_settings_json():
    markov = Markov(
        parser=Mock(save=lambda: 0),
        scanner=Mock(save=lambda: 1),
        storage=Mock()
    )
    json = markov.get_settings_json()
    assert json == {
        'scanner': 1,
        'parser': 0
    }

@pytest.mark.parametrize('test,res', [
    (((0, 0, 0), (0, 0, 0)), True),
    (((0, 0, 0), (0, 0, 1)), False),
    (((0, 0, 0), (0, 1, 0)), False),
    (((0, 0, 0), (1, 0, 0)), False)
])
def test_markov_eq(test, res):
    markov = []
    for scanner, parser, storage in test:
        m = Markov()
        m.scanner = scanner
        m.parser = parser
        m.storage = storage
        markov.append(m)
    assert (markov[0] == markov[1]) == res

def test_markov_base_save(mocker):
    mocker.patch('markovchain.Markov.get_settings_json', return_value=0)
    storage = Mock(settings={})
    markov = Markov(
        parser=Mock(),
        scanner=Mock(),
        storage=storage
    )
    markov.save(1)
    assert storage.settings == {'markov': 0}
    storage.save.assert_called_once_with(1)
    markov.get_settings_json.assert_called_once_with() # pylint:disable=no-member

def test_markov_base_close():
    storage = Mock(settings={}, close=Mock())
    markov = Markov(
        parser=Mock(),
        scanner=Mock(),
        storage=storage
    )
    markov.close()
    storage.close.assert_called_once_with()
