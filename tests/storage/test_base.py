from unittest.mock import Mock, call
import pytest

from markovchain.storage.base import Storage


class StorageTest(Storage):
    def replace_state_separator(self, old_separator, new_separator):
        pass
    def get_dataset(self, key, create=False):
        pass
    def add_links(self, links, dataset_prefix=''):
        pass
    def get_state(self, state, size):
        pass
    def get_states(self, dataset, string):
        pass
    def get_links(self, dataset, state, backward=False):
        pass
    def follow_link(self, link, state, backward=False):
        pass
    def do_save(self, fp=None):
        pass
    def close(self):
        pass
    @classmethod
    def load(cls, fp):
        pass

def test_storage_base_abstract():
    with pytest.raises(TypeError):
        Storage()

def test_storage_base_properties():
    storage = StorageTest()
    storage.replace_state_separator = Mock()
    assert storage.state_separator == ' '
    storage.state_separator = ':'
    storage.replace_state_separator.assert_called_once_with(' ', ':')
    assert storage.state_separator == ':'

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    (({'state_separator': '-'},), ({'state_separator': '+'},), False)
])
def test_storage_base_eq(test, test2, res):
    assert (StorageTest(*test) == StorageTest(*test2)) == res

@pytest.mark.parametrize('settings,test,res', [
    ({}, 'a b c', ['a', 'b', 'c']),
    ({'storage': {'state_separator': '-'}}, 'a b-c d', ['a b', 'c d']),
    ({'storage': {'state_separator': ''}}, 'a b', ['a', ' ', 'b']),
])
def test_storage_base_split_state(settings, test, res):
    assert StorageTest(settings).split_state(test) == res

@pytest.mark.parametrize('settings,test,res', [
    ({}, map(str, range(3)), '0 1 2'),
    ({'storage': {'state_separator': '-'}}, ['a', 'b'], 'a-b'),
])
def test_storage_base_join_state(settings, test, res):
    assert StorageTest(settings).join_state(test) == res

@pytest.mark.parametrize('args,random,res', [
    (('data', 'x', True), 0, 'y'),
    (('data', 'x', True), 1, 'z'),
    (('data', 'z', False), 0, 'x'),
    (('data', 'y', True), [], None)
])
def test_storage_base_random_link(mocker, args, random, res):
    randint = mocker.patch(
        'markovchain.storage.base.randint',
        return_value=random
    )
    links = {
        'x': [(1, 'y'), (1, 'z')],
        'y': [],
        'z': [(1, 'x')]
    }
    storage = StorageTest()
    storage.get_links = Mock(
        wraps=lambda dataset, node, backward: links.get(node, [])
    )
    storage.follow_link = Mock(return_value=0)

    test = storage.random_link(*args)
    s = sum(count for count, link in links.get(args[1], []))
    storage.get_links.assert_called_with(*args)
    if s > 0:
        assert test == (res, 0)
        randint.assert_called_with(0, s - 1)
        storage.follow_link.assert_called_with(
            links[args[1]][random],
            args[1],
            args[2]
        )
    else:
        assert test == (None, None)
        assert randint.call_count == 0
        assert storage.follow_link.call_count == 0

@pytest.mark.parametrize('state,backward', [
    ('x', True),
    (['x', 'y'], False)
])
def test_storage_base_generate(state, backward):
    storage = StorageTest()
    storage.random_link = Mock(side_effect=[
        ('link', 'state'), ('link2', 'state2'), (None, None)
    ])
    storage.get_dataset = Mock(return_value=2)
    storage.get_state = Mock(return_value=1)
    storage.split_state = Mock(return_value=3)

    res = list(storage.generate(state, 4, 'data', backward))
    assert res == ['link', 'link2']
    storage.get_dataset.assert_called_with('data')
    if isinstance(state, str):
        storage.split_state.assert_called_with(state)
        storage.get_state.assert_called_with(3, 4)
    else:
        assert storage.split_state.call_count == 0
        storage.get_state.assert_called_with(state, 4)
    assert storage.random_link.call_count == 3
    storage.random_link.assert_has_calls([
        call(2, 1, backward),
        call(2, 'state', backward),
        call(2, 'state2', backward)
    ])

def test_storage_base_save():
    storage = StorageTest()
    storage.do_save = Mock()
    storage.state_separator = '+'
    storage.save(0)
    assert storage.settings['storage']['state_separator'] == '+'
    storage.do_save.assert_called_once_with(0)
