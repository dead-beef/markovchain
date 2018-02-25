from argparse import FileType
from sys import stdout #, stderr
from os import replace, remove, path, SEEK_SET, SEEK_END

from .. import MarkovText, JsonStorage, SqliteStorage
from ..util import truncate
from .util import (
    load, save, infiles, JSON, SQLITE,
    tqdm, BAR_FORMAT, BAR_DESC_SIZE
)
from .util import cmd_settings # pylint:disable=unused-import


def create_arg_parser(parent):
    """Create command subparsers.

    Parameters
    ----------
    parent : `argparse.ArgumentParser`
        Command parser.
    """

    arg1 = parent.add_subparsers(dest='command')

    arg2 = arg1.add_parser('create')
    arg2.add_argument('-P', '--progress',
                      action='store_true',
                      help='show progress bar')
    arg2.add_argument('-s', '--settings',
                      type=FileType('r'), default=None,
                      help='settings json file')
    arg2.add_argument('-o', '--output',
                      default=None,
                      help='output file (default: stdout)')
    arg2.add_argument('input', nargs='*',
                      help='input file (default: stdin)')

    arg2 = arg1.add_parser('update')
    arg2.add_argument('-P', '--progress',
                      action='store_true',
                      help='show progress bar')
    arg2.add_argument('-s', '--settings',
                      type=FileType('r'), default=None,
                      help='settings json file')
    arg2.add_argument('-o', '--output',
                      default=None,
                      help='output file (default: rewrite state file)')
    arg2.add_argument('state',
                      help='state file')
    arg2.add_argument('input', nargs='*',
                      help='input file (default: stdin)')

    arg2 = arg1.add_parser('settings')
    arg2.add_argument('state',
                      help='state file')

    arg2 = arg1.add_parser('generate')
    arg2.add_argument('-P', '--progress',
                      action='store_true',
                      help='show progress bar')
    arg2.add_argument('-nf', '--no-format',
                      dest='format',
                      action='store_false',
                      help='do not format sentences')
    arg2.add_argument('-s', '--settings',
                      type=FileType('r'), default=None,
                      help='settings json file')
    arg2.add_argument('-ss', '--state-size',
                      type=int, default=None,
                      help='generator state size')
    arg2.add_argument('-st', '--start',
                      default=None,
                      help='sentence start')
    arg2.add_argument('-w', '--words',
                      type=int, default=256,
                      help='max sentence size (default: %(default)s)')
    arg2.add_argument('-ws', '--word-separator',
                      default=' ',
                      help='output word separator (default: \' \')')
    arg2.add_argument('-S', '--sentences',
                      type=int, default=1,
                      help='number of generated sentences (default: %(default)s)')
    arg2.add_argument('-o', '--output',
                      type=FileType('w'), default=stdout,
                      help='output file (default: stdout)')
    arg2.add_argument('state',
                      help='state file')

    arg2.set_defaults(format=True)

def read(fnames, markov, progress):
    """Read data files and update a generator.

    Parameters
    ----------
    fnames : `list` of `str`
        File paths.
    markov : `markovchain.base.MarkovBase`
        Generator to update.
    progress : `bool`
        Show progress bar.
    """
    with infiles(fnames, progress) as fnames:
        for fname in fnames:
            with open(fname, 'r') as fp:
                if progress:
                    fp.seek(0, SEEK_END)
                    total = fp.tell()
                    title = truncate(fname, BAR_DESC_SIZE - 1, False)
                    pbar = tqdm(total=total, desc=title,
                                leave=False, unit='byte',
                                bar_format=BAR_FORMAT, dynamic_ncols=True)
                    fp.seek(0, SEEK_SET)
                    prev = 0
                else:
                    pbar = None

                try:
                    line = fp.readline()
                    while line:
                        markov.data(line.lower(), True)
                        if pbar is not None:
                            pos = fp.tell()
                            if pos <= total:
                                pbar.update(pos - prev)
                                prev = pos
                        line = fp.readline()
                finally:
                    if pbar is not None:
                        pbar.close()

                markov.data('', False)

def cmd_create(args):
    """Create a generator.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    """
    if args.type == SQLITE:
        if args.output is not None and path.exists(args.output):
            remove(args.output)
        storage = SqliteStorage(db=args.output, settings=args.settings)
    else:
        storage = JsonStorage(settings=args.settings)
    markov = MarkovText.load(storage)
    read(args.input, markov, args.progress)
    save(markov, args.output, args)

def cmd_update(args):
    """Update a generator.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    """
    args.output = None

    markov = load(MarkovText, args.state, args)
    read(args.input, markov, args.progress)
    if args.output is None:
        if args.type == SQLITE:
            save(markov, None, args)
        elif args.type == JSON:
            name, ext = path.splitext(args.state)
            tmp = name + '.tmp' + ext
            save(markov, tmp, args)
            replace(tmp, args.state)
    else:
        save(markov, args.output, args)

def cmd_generate(args):
    """Generate text.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    """

    markov = load(MarkovText, args.state, args)
    ss = range(args.sentences)

    if args.progress:
        title = truncate(args.output.name, BAR_DESC_SIZE - 1, False)
        ss = tqdm(ss, desc=title,
                  bar_format=BAR_FORMAT, dynamic_ncols=True)

    if args.start is not None:
        args.start = args.start.lower()

    if not args.format:
        markov.do_format = lambda x: x

    for _ in ss:
        data = markov(args.words,
                      state_size=args.state_size,
                      start=args.start)
        if data:
            print(data)
