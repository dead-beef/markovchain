from unittest.mock import Mock
import pytest

from markovchain.storage.base import Storage


class StorageTest(Storage):
    def replace_state_separator(self, old_separator, new_separator):
        pass
    def links(self, links):
        pass
    def random_link(self, state):
        pass
    def do_save(self, fp=None):
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
])
def test_storage_base_split_state(settings, test, res):
    assert StorageTest(settings).split_state(test) == res

@pytest.mark.parametrize('settings,test,res', [
    ({}, map(str, range(3)), '0 1 2'),
    ({'storage': {'state_separator': '-'}}, ['a', 'b'], 'a-b'),
])
def test_storage_base_join_state(settings, test, res):
    assert StorageTest(settings).join_state(test) == res

def test_storage_base_save():
    storage = StorageTest()
    storage.do_save = Mock()
    storage.state_separator = '+'
    storage.save(0)
    assert storage.settings['storage']['state_separator'] == '+'
    storage.do_save.assert_called_once_with(0)
