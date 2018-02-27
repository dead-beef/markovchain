from io import StringIO
import os
import json
import pytest

from markovchain.cli.main import main


@pytest.mark.parametrize('fname,settings,data,args,res', [
    (
        'state.json',
        None,
        ['a b c'],
        (
            [],
            [],
            ['-w', '16', '-S', '3']
        ),
        'A b c.\nA b c.\nA b c.\n'
    ),
    (
        'state.db',
        None,
        ['a b', 'a b c d'],
        (
            [],
            [],
            ['-nf', '-st', 'b c', '-ws', '|']
        ),
        'b c|d|.\n'
    ),
    (
        'state.db',
        None,
        ['a b', 'a b c d'],
        (
            [],
            [],
            ['-st', 'a   b c', '-ws', '|']
        ),
        'A b c|d|.\n'
    ),
    (
        'state.json.bz2',
        {
            'markov': {
                'parser': {
                    '__class__': 'Parser',
                    'state_sizes': [1, 2]
                }
            }
        },
        ['a b c.\na b c.\na b c.\nb b d.'],
        (
            [],
            [],
            ['-ss', '2', '-st', 'b b']
        ),
        'B b d.\n'
    )
])
def test_cli_text(tmpdir, mocker, fname, settings, data, args, res):
    stdout = mocker.patch('sys.stdout', new_callable=StringIO)
    stderr = mocker.patch('sys.stderr', new_callable=StringIO)
    exit_ = mocker.patch('sys.exit')

    tmpdir = str(tmpdir)
    statefile = os.path.join(tmpdir, fname)
    datafile = os.path.join(tmpdir, 'data.txt')
    settingsfile = os.path.join(tmpdir, 'settings.json')

    cmd = ['text', 'create', '-o', statefile]
    if settings is not None:
        with open(settingsfile, 'wt') as fp:
            json.dump(settings, fp)
        cmd.extend(('-s', settingsfile))
    cmd.extend(args[0])
    if len(data) > 0:
        with open(datafile, 'wt') as fp:
            fp.write(data[0])
        cmd.append(datafile)
    main(cmd)
    assert exit_.call_count == 0
    assert stdout.getvalue() == ''
    assert stderr.getvalue() == ''

    update = data[1:]
    if update:
        cmd = ['text', 'update']
        cmd.extend(args[1])
        cmd.append(statefile)
        for i, data_ in enumerate(data):
            datafile = os.path.join(tmpdir, 'data%d.txt' % i)
            cmd.append(datafile)
            with open(datafile, 'wt') as fp:
                fp.write(data_)
        main(cmd)
        assert exit_.call_count == 0
        assert stdout.getvalue() == ''
        assert stderr.getvalue() == ''

    cmd = ['text', 'generate']
    cmd.extend(args[2])
    cmd.append(statefile)
    main(cmd)
    assert exit_.call_count == 0
    assert stdout.getvalue() == res
    assert stderr.getvalue() == ''
