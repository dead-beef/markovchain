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

def test_markov_base_generate_empty():
    markov = Markov(parser=Mock(state_sizes=[]))
    assert list(markov.generate(state_size=None)) == []

def test_markov_base_generate_error():
    markov = Markov()
    markov.parser = None
    with pytest.raises(ValueError):
        list(markov.generate(state_size=None))

@pytest.mark.parametrize('state_size,start,res', [
    (1, None, ['']),
    (2, None, ['', '']),
    (3, None, ['', '', '']),
    (3, 'a b', ['', 'a', 'b']),
    (3, range(2), ['', 0, 1])
])
def test_markov_base_generate(mocker, state_size, start, res):
    state_size_dataset = mocker.patch(
        'markovchain.base.state_size_dataset',
        return_value='_0'
    )
    storage = Mock(
        random_link=Mock(side_effect=[('link', 'state'), (None, None)]),
        split_state=lambda s: s.split(),
        get_dataset=Mock(wraps=lambda s: 0)
    )
    markov = Markov(
        parser=Mock(),
        scanner=Mock(),
        storage=storage
    )
    assert list(markov.generate(state_size, start, 'data')) == ['link']
    assert storage.random_link.call_count == 2
    storage.random_link.assert_has_calls([
        call(0, deque(res, maxlen=state_size)),
        call(0, 'state')
    ])
    storage.get_dataset.assert_called_once_with('data_0')
    state_size_dataset.assert_called_with(state_size)

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
