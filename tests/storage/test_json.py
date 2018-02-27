from io import StringIO
import pytest

from markovchain import JsonStorage


def test_json_storage_empty():
    storage = JsonStorage()
    assert storage.nodes == {}
    assert storage.settings == {}

def test_json_storage_get_dataset():
    storage = JsonStorage()
    with pytest.raises(KeyError):
        storage.get_dataset('0')
    data = storage.get_dataset('0', True)
    assert data == {}
    assert storage.get_dataset('0', True) is data
    assert storage.get_dataset('1', True) is not data

def test_json_storage_add_links():
    storage = JsonStorage()
    storage.add_links([
        ('0', ('x',), 'y'),
        ('0', ('y',), 'z'),
        ('0', ('x',), 'y')
    ])
    assert storage.nodes == {
        '0': {
            'x': ['y', 2],
            'y': ['z', 1]
        }
    }
    storage.add_links([
        ('0', ('z',), 'x'),
        ('0', ('x',), 'z'),
        ('0', ('x',), 'y')
    ])
    assert storage.nodes == {
        '0': {
            'x': [['y', 'z'], [3, 1]],
            'y': ['z', 1],
            'z': ['x', 1]
        }
    }
    storage.add_links([
        ('1', ('x',), 'y')
    ])
    assert storage.nodes == {
        '0': {
            'x': [['y', 'z'], [3, 1]],
            'y': ['z', 1],
            'z': ['x', 1]
        },
        '1': {
            'x': ['y', 1]
        }
    }

@pytest.mark.parametrize('links,state,random,call,res', [
    ([('0', ('x',), 'y')], 'y', None, None, None),
    ([('0', ('x',), 'y')], 'x', 0, None, 'y'),
    ([('0', ('x',), 'y'), ('0', ('x',), 'z')], 'x', 0, (0, 1), 'y'),
    ([('0', ('x',), 'y'), ('0', ('x',), 'z')], 'x', 1, (0, 1), 'z'),
    ([('1', ('x',), 'y'), ('0', ('x',), 'z')], 'x', 0, None, 'z'),
])
def test_json_storage_random_link(mocker, links, state, random, call, res):
    randint = mocker.patch(
        'markovchain.storage.json.randint',
        return_value=random
    )
    storage = JsonStorage()
    storage.add_links(links)
    link, next_state = storage.random_link(storage.get_dataset('0'), [state])
    assert link == res
    if res is None:
        assert next_state is None
    else:
        assert next_state == [state, res]
    if call is None:
        assert randint.call_count == 0
    else:
        randint.assert_called_once_with(*call)

def test_json_storage_state_separator():
    storage = JsonStorage()
    storage.add_links([('0', ('x', 'y'), 'z'), ('1', ('y', 'z'), 'x')])
    assert storage.nodes == {
        '0': {
            'x y': ['z', 1]
        },
        '1': {
            'y z': ['x', 1]
        }
    }
    storage.state_separator = ':'
    assert storage.nodes == {
        '0': {
            'x:y': ['z', 1],
        },
        '1': {
            'y:z': ['x', 1]
        }
    }

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((), ({}), True),
    ((), ({'0': {'x':['y', 1]}}), False),
    (({'0': {'x':['y', 1]}}), ({'0': {'x':['y', 1]}}), True),
    ((), ({}, {'state_separator': ':'}), False)
])
def test_json_storage_eq(test, test2, res):
    assert (JsonStorage(*test) == JsonStorage(*test2)) == res

def test_json_storage_save_load():
    storage = JsonStorage(settings={'state_separator': ':'})
    storage.add_links([
        ('0', ('x',), 'y'),
        ('0', ('y',), 'z'),
        ('1', ('x',), 'y'),
        ('1', ('x',), 'z')
    ])

    fp = StringIO()
    storage.save(fp)
    fp.seek(0)
    loaded = JsonStorage.load(fp)
    assert storage == loaded
