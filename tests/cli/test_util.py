from unittest.mock import Mock, MagicMock, mock_open

from io import StringIO
from argparse import Namespace
import json
import sys

import pytest

from markovchain import JsonStorage, SqliteStorage
from markovchain.cli.util import (
    no_tqdm, NoProgressBar,
    pprint, load, save,
    set_args, JSON, SQLITE,
    check_output_format,
    infiles, outfiles
)


def test_no_progress_bar_warning(mocker):
    stderr = mocker.patch('sys.stderr', new_callable=StringIO)
    pbar = NoProgressBar()
    assert stderr.getvalue() == ''
    assert not NoProgressBar.warning
    pbar.print_warning()
    assert stderr.getvalue() != ''
    assert NoProgressBar.warning
    pbar.print_warning()
    assert stderr.getvalue() != ''
    assert NoProgressBar.warning

def test_no_tqdm(mocker):
    no_pbar = mocker.patch('markovchain.cli.util.NoProgressBar')
    pbar = no_tqdm(total=100, leave=False, desc='')
    assert isinstance(pbar, Mock)
    no_pbar.assert_called_with()
    no_pbar.print_warning.assert_called_with()
    no_pbar.reset_mock()
    iterable = range(3)
    pbar = no_tqdm(iterable)
    assert pbar is iterable
    no_pbar.assert_not_called()
    no_pbar.print_warning.assert_called_with()


@pytest.mark.parametrize('test', [
    {'x': 0, 'y': [{'z': '0'}, {'z': '1'}]},
    [{'x': 0.1, 'y': {'y': False, 'z': None, 'u': 3}}, {'z': 0}]
])
def test_pprint(mocker, test):
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    res = json.dumps(test, indent=4, sort_keys=True) + '\n'
    pprint(test)
    assert stdout.getvalue() == res

@pytest.mark.parametrize('test,res', [
    ([], '[]\n'),
    ([0, 1, 2], '[0, 1, 2]\n'),
    ([True, None], '[true, null]\n'),
    ([0, [1, 2], 3], '[\n    0,\n    [1, 2],\n    3\n]\n')
])
def test_pprint_array(mocker, test, res):
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    pprint(test)
    assert stdout.getvalue() == res


@pytest.mark.parametrize('fname,bz2,stdout', [
    ('test.json', False, False),
    ('test.json.bz2', True, True)
])
def test_load_json(mocker, fname, bz2, stdout):
    open_ = mocker.patch('builtins.open', new_callable=mock_open)
    bz2open = mocker.patch('bz2.open', new_callable=mock_open)
    stdout_ = mocker.patch('sys.stdout', new_callable=StringIO)
    json_storage = MagicMock()
    json_storage_cls = mocker.patch(
        'markovchain.cli.util.JsonStorage',
        load=Mock(return_value=json_storage)
    )
    if bz2:
        handle = bz2open()
    else:
        handle = open_()

    cls = Mock(from_storage=Mock(return_value=0))
    args = Namespace(type=JSON, progress=stdout, settings={})

    assert load(cls, fname, args) == 0
    assert (stdout_.getvalue() != '') == stdout
    if bz2:
        assert not open_.called
        bz2open.assert_called_with(fname, 'rt')
    else:
        assert not bz2open.called
        open_.assert_called_with(fname, 'rt')
    json_storage_cls.load.assert_called_once_with(handle)
    cls.from_storage.assert_called_once_with(json_storage)

def test_load_sqlite(mocker):
    sqlite_storage = MagicMock()
    sqlite_storage_cls = mocker.patch(
        'markovchain.cli.util.SqliteStorage',
        load=Mock(return_value=sqlite_storage)
    )
    fname = 'test'
    cls = Mock(from_storage=Mock(return_value=0))
    args = Namespace(type=SQLITE, progress=False, settings={})
    assert load(cls, fname, args) == 0
    sqlite_storage_cls.load.assert_called_once_with(fname)
    cls.from_storage.assert_called_once_with(sqlite_storage)


@pytest.mark.parametrize('fname,bz2,stdout', [
    ('test.json', False, False),
    ('test.json.bz2', True, True)
])
def test_save_json(mocker, fname, bz2, stdout):
    open_ = mocker.patch('builtins.open', new_callable=mock_open)
    bz2open = mocker.patch('bz2.open', new_callable=mock_open)
    stdout_ = mocker.patch('sys.stdout', new_callable=StringIO)
    markov = Mock(storage=JsonStorage(), save=Mock())

    if bz2:
        handle = bz2open()
    else:
        handle = open_()

    args = Namespace(progress=stdout, settings={})

    save(markov, fname, args)
    assert (stdout_.getvalue() != '') == stdout
    if bz2:
        assert not open_.called
        bz2open.assert_called_with(fname, 'wt')
    else:
        assert not bz2open.called
        open_.assert_called_with(fname, 'wt')
    markov.save.assert_called_once_with(handle)

def test_save_sqlite():
    markov = Mock(storage=SqliteStorage(), save=Mock())
    fname = 'test'
    args = Namespace(progress=False, settings={})
    save(markov, fname, args)
    markov.save.assert_called_once_with()


def test_set_args_error():
    args = Namespace(output=sys.stdout, progress=True)
    with pytest.raises(ValueError):
        set_args(args)

@pytest.mark.parametrize('args,res', [
    (Namespace(), JSON),
    (Namespace(output='.db'), SQLITE),
    (Namespace(state='.json'), JSON),
    (Namespace(state='.json.bz2'), JSON),
    (Namespace(type='json'), JSON),
    (Namespace(output='.db', state='.json.bz2'), JSON),
    (Namespace(output='.db', state='.json.bz2', type='sqlite'), SQLITE)
])
def test_set_args_type(args, res):
    set_args(args)
    assert args.type == res

def test_set_args_settings(mocker):
    mocker.patch('json.load', new=lambda x: x())

    args = Namespace()
    set_args(args)
    assert args.settings == {} # pylint:disable=no-member

    args = Namespace(settings=None)
    set_args(args)
    assert args.settings == {} # pylint:disable=no-member

    s = list(range(3))
    mock = MagicMock(return_value=s)
    args = Namespace(settings=mock)
    set_args(args)
    assert args.settings == s # pylint:disable=no-member
    mock.close.assert_called_with()


@pytest.mark.parametrize('test', [
    ('test', -1),
    ('test', 0),
    ('test', 2),
    ('test%d%d', 2)
])
def test_check_output_format_error(test):
    with pytest.raises(ValueError):
        check_output_format(*test)

@pytest.mark.parametrize('test', [
    ('test', 1),
    ('test%d', 2)
])
def test_check_output_format(test):
    check_output_format(*test)


@pytest.mark.parametrize('test', [
    ([], True),
    (list(range(3)), False)
])
def test_infiles(mocker, test):
    tqdm = mocker.patch('markovchain.cli.util.tqdm')
    with infiles(*test) as iter_:
        assert not tqdm.called
        assert iter_ is test[0]

def test_infiles_progress(mocker):
    tqdm = mocker.patch('markovchain.cli.util.tqdm')
    test = [0, 1]
    with infiles(test, True) as pbar:
        assert tqdm.called
        assert (test,) in tqdm.call_args
        assert isinstance(pbar, Mock)
    pbar.close.assert_called_once_with()


@pytest.mark.parametrize('test', [
    ('', -1, False),
    ('', 0, False)
])
def test_outfiles_error(test):
    with pytest.raises(ValueError), outfiles(*test):
        pass

@pytest.mark.parametrize('test,res', [
    (('', 1, False), ['']),
    (('%d', 2, False), ['0', '1'])
])
def test_outfiles(mocker, test, res):
    tqdm = mocker.patch('markovchain.cli.util.tqdm')
    with outfiles(*test) as files:
        files = list(files)
        assert not tqdm.called
        assert files == res

def test_outfiles_progress(mocker):
    tqdm = mocker.patch('markovchain.cli.util.tqdm')
    test = ('%d', 3, True)
    res = ['0', '1', '2']
    with outfiles(*test) as pbar:
        assert tqdm.called
        assert list(tqdm.call_args[0][0]) == res
        assert isinstance(pbar, Mock)
    pbar.close.assert_called_once_with()
