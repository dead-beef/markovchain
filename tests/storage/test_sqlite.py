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

@pytest.mark.parametrize('state,size,res', [
    ([], 4, None),
    (['x'], 1, 1),
    (['x', 'y'], 1, 2),
    (['x', 'y'], 2, 3)
])
def test_sqlite_storage_get_state(state, size, res):
    storage = SqliteStorage()
    storage.add_links([('0', ('x',), 'y'), ('0', ('x', 'y'), 'z')])
    assert storage.get_state(state, size) == res

@pytest.mark.parametrize('dataset,string,res', [
    ('0', 'x', ['XX', 'xy', 'xz']),
    ('0', 'y', ['xy', 'yz']),
    ('0', 'q', []),
    ('1', 'x', ['x']),
    ('1', 'y', [])
])
def test_json_storage_get_states(dataset, string, res):
    storage = SqliteStorage()
    storage.add_links([
        ('0', ('XX',), 'xy'),
        ('0', ('xy',), 'yz'),
        ('0', ('yz',), 'xz'),
        ('0', ('xz',), None),
        ('1', ('x',), 'y')
    ])
    test = storage.get_states(dataset, string)
    test.sort()
    assert test == res

@pytest.mark.parametrize('args,res', [
    ((1,), [(1, 'y', 2), (1, 'z', 3)]),
    ((2,), [(1, 'z', 3)]),
    ((3,), []),
    ((1, True), []),
    ((2, True), [(1, 'x', 1)]),
    ((3, True), [(1, 'x', 1), (1, 'y', 2)])
])
def test_sqlite_storage_get_links(args, res):
    storage = SqliteStorage()
    storage.add_links([
        ('0', ('x',), 'y'),
        ('0', ('x',), 'z'),
        ('0', ('y',), 'z')
    ])
    assert storage.get_links(1, *args) == res

@pytest.mark.parametrize('args,res', [
    (((0, 1, 2), 3, False), 2),
    (((1, 2, 3), 4, True), 3),
])
def test_sqlite_storage_follow_link(args, res):
    storage = SqliteStorage()
    assert storage.follow_link(*args) == res

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

def test_sqlite_storage_close(tmpdir):
    db = os.path.join(str(tmpdir), 'test.db')
    storage = SqliteStorage(db=db)

    storage.add_links([('0', ('x',), 'y')])
    storage.save()
    nodes = get_nodes(storage.cursor)
    storage.add_links([('0', ('z',), 'u')])
    storage.close()
    assert storage.cursor is None
    assert storage.db is None

    loaded = SqliteStorage.load(db)
    assert nodes == get_nodes(loaded.cursor)
