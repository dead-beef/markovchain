from argparse import FileType
from os import replace, remove, path, SEEK_SET, SEEK_END

from ..storage import JsonStorage, SqliteStorage
from ..text import MarkovText, ReplyMode
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
                      help='do not format text')
    arg2.add_argument('-s', '--settings',
                      type=FileType('r'), default=None,
                      help='settings json file')
    arg2.add_argument('-ss', '--state-size',
                      type=int, default=None,
                      help='generator state size')
    arg2.add_argument('-S', '--start',
                      default=None,
                      help='text start')
    arg2.add_argument('-E', '--end',
                      default=None,
                      help='text end')
    arg2.add_argument('-R', '--reply',
                      default=None,
                      help='reply to text')
    arg2.add_argument('-w', '--words',
                      type=int, default=256,
                      help='max text size (default: %(default)s)')
    arg2.add_argument('-c', '--count',
                      type=int, default=1,
                      help='number of generated texts (default: %(default)s)')
    arg2.add_argument('-o', '--output',
                      type=FileType('w'), default=None,
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
                        markov.data(line, True)
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
    markov = MarkovText.from_storage(storage)
    read(args.input, markov, args.progress)
    save(markov, args.output, args)

def cmd_update(args):
    """Update a generator.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    """
    #args.output = None

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

    if args.start:
        if args.end or args.reply:
            raise ValueError('multiple input arguments')
        args.reply_to = args.start
        args.reply_mode = ReplyMode.END
    elif args.end:
        if args.reply:
            raise ValueError('multiple input arguments')
        args.reply_to = args.end
        args.reply_mode = ReplyMode.START
    elif args.reply:
        args.reply_to = args.reply
        args.reply_mode = ReplyMode.REPLY
    else:
        args.reply_to = None
        args.reply_mode = ReplyMode.END

    markov = load(MarkovText, args.state, args)

    ss = range(args.count)
    if args.progress:
        title = truncate(args.output.name, BAR_DESC_SIZE - 1, False)
        ss = tqdm(ss, desc=title,
                  bar_format=BAR_FORMAT, dynamic_ncols=True)

    if not args.format:
        markov.formatter = lambda x: x

    for _ in ss:
        data = markov(
            args.words,
            state_size=args.state_size,
            reply_to=args.reply_to,
            reply_mode=args.reply_mode
        )
        if data:
            print(data)
