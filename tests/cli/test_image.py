import os
import json
import pytest

from markovchain.cli.main import main


@pytest.mark.parametrize('fname,settings,data,args,res', [
])
def test_cli_image(mocker, mock_cli, fname, settings, data, args, res):
    mock_cli(mocker)

    statefile = os.path.join(mock_cli.dir, fname)
    datafile = os.path.join(mock_cli.dir, 'data.txt')
    settingsfile = os.path.join(mock_cli.dir, 'settings.json')

    cmd = ['text', 'create', '-o', statefile]
    if settings is not None:
        with open(settingsfile, 'wt') as fp:
            json.dump(settings, fp)
        cmd.extend(('-s', settingsfile))
    if len(data) > 0:
        with open(datafile, 'wt') as fp:
            fp.write(data[0])
        cmd.append(datafile)
    mock_cli.run(main, cmd)
    mock_cli.assert_output('', '')

    update = data[1:]
    if update:
        cmd = ['text', 'update']
        cmd.append(statefile)
        for i, data_ in enumerate(data):
            datafile = os.path.join(mock_cli.dir, 'data%d.txt' % i)
            cmd.append(datafile)
            with open(datafile, 'wt') as fp:
                fp.write(data_)
        mock_cli.run(main, cmd)
        mock_cli.assert_output('', '')

    cmd = ['text', 'generate']
    cmd.extend(args)
    cmd.append(statefile)
    mock_cli.run(main, cmd)
    mock_cli.assert_output(res, '')
