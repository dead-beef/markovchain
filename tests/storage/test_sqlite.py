import os
import pytest

from markovchain import SqliteStorage


def get_nodes(cursor):
    cursor.execute('SELECT id, value FROM nodes')
    return cursor.fetchall()

def get_datasets(cursor):
    cursor.execute('SELECT id, key FROM datasets')
    return cursor.fetchall()

def get_links(cursor, source):
    cursor.execute(
        'SELECT dataset, value, count FROM links WHERE source=?',
        (source,)
    )
    return cursor.fetchall()

def test_sqlite_storage_empty():
    storage = SqliteStorage()
    assert storage.db
    assert storage.cursor
    tables = storage.get_tables()
    assert 'main' in tables
    assert 'nodes' in tables
    assert 'links' in tables
    assert 'datasets' in tables

def test_sqlite_storage_get_dataset():
    storage = SqliteStorage()
    with pytest.raises(KeyError):
        storage.get_dataset('0')
    assert storage.get_dataset('0', True) == 1
    assert storage.get_dataset('0', True) == 1
    assert storage.get_dataset('1', True) == 2

def test_sqlite_storage_add_links():
    storage = SqliteStorage()
    storage.add_links([
        ('0', ('x',), 'y'),
        ('0', ('y',), 'z'),
        ('0', ('x',), 'y')
    ])
    assert get_datasets(storage.cursor) == [(1, '0')]
    assert get_nodes(storage.cursor) == [(1, 'x'), (2, 'y'), (3, 'z')]
    assert get_links(storage.cursor, 1) == [(1, 'y', 2)]
    assert get_links(storage.cursor, 2) == [(1, 'z', 1)]
    assert get_links(storage.cursor, 3) == []

    storage.add_links([('0', ('x',), 'z'), ('1', ('x',), 'y')])
    assert get_datasets(storage.cursor) == [(1, '0'), (2, '1')]
    assert get_links(storage.cursor, 1) == [
        (1, 'y', 2), (1, 'z', 1), (2, 'y', 1)
    ]

@pytest.mark.parametrize('links,state,random,call,res', [
    ([('0', ('x',), 'y')], 'y', None, None, None),
    ([('0', ('x',), 'y')], 'x', 0, (0, 0), 'y'),
    ([('0', ('x',), 'y'), ('0', ('x',), 'z')], 'x', 0, (0, 1), 'y'),
    ([('0', ('x',), 'y'), ('0', ('x',), 'z')], 'x', 1, (0, 1), 'z')
])
def test_sqlite_storage_random_link(mocker, links, state, random, call, res):
    randint = mocker.patch(
        'markovchain.storage.sqlite.randint',
        return_value=random
    )
    storage = SqliteStorage()
    storage.add_links(links)
    link, next_state = storage.random_link(storage.get_dataset('0'), state)
    assert link == res
    if res is None:
        assert next_state is None
    else:
        assert next_state == storage.get_node(link)
    if call is None:
        assert randint.call_count == 0
    else:
        randint.assert_called_once_with(*call)

def test_sqlite_storage_state_separator():
    storage = SqliteStorage()
    storage.add_links([('0', ('x', 'y'), 'z'), ('0', ('y', 'z'), 'x')])
    assert get_nodes(storage.cursor) == [(1, 'x y'), (2, 'y z'), (3, 'z x')]
    storage.state_separator = ':'
    assert get_nodes(storage.cursor) == [(1, 'x:y'), (2, 'y:z'), (3, 'z:x')]

def test_sqlite_storage_save_load(tmpdir):
    db = os.path.join(str(tmpdir), 'test.db')
    storage = SqliteStorage(db=db)
    storage.state_separator = ':'
    storage.add_links([('0', ('x', 'y'), 'z'), ('0', ('y', 'z'), 'x')])
    nodes = get_nodes(storage.cursor)
    storage.save()
    loaded = SqliteStorage.load(db)
    assert nodes == get_nodes(loaded.cursor)
    assert storage.state_separator == loaded.state_separator
