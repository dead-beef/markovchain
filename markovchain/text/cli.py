from argparse import FileType
from sys import stdout, stderr
from os import replace, remove, path, SEEK_SET, SEEK_END

from .. import CharScanner
from ..util import truncate
from ..cli.util import (
    load, save, infiles, JSON, SQLITE,
    tqdm, BAR_FORMAT, BAR_DESC_SIZE
)
from ..cli.util import cmd_settings # pylint:disable=unused-import

BASE = ()

def create_arg_parser(parent):
    """Create command subparsers.

    Parameters
    ----------
    parent : ArgumentParser
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

def read(fnames, markov, progress):
    """Read data files and update a generator.

    Parameters
    ----------
    fnames : list of str
        File paths.
    markov : MarkovBase
        Generator to update.
    progress : bool
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
    args : Namespace
        Command arguments.
    """
    if args.type == SQLITE:
        if args.output is not None and path.exists(args.output):
            remove(args.output)
        args.settings['db'] = args.output

    markov = args.markov(**args.settings)
    read(args.input, markov, args.progress)
    save(markov, args.output, args)

def cmd_update(args):
    """Update a generator.

    Parameters
    ----------
    args : Namespace
        Command arguments.
    """
    args.output = None

    markov = load(args.markov, args.state, args)
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
    args : Namespace
        Command arguments.
    """
    ispunct = lambda s: (s.isprintable()
                         and not s.isalnum()
                         and not s.isspace())
    markov = load(args.markov, args.state, args)
    ss = range(args.sentences)

    if args.progress:
        title = truncate(args.output.name, BAR_DESC_SIZE - 1, False)
        ss = tqdm(ss, desc=title,
                  bar_format=BAR_FORMAT, dynamic_ncols=True)

    if args.start is not None:
        parse = markov.parser(markov.scanner(args.start.lower(), True), True)
        for _ in parse:
            pass
        state = list(markov.parser.state)
        markov.scanner.reset()
        markov.parser.reset()
    else:
        state = None

    try:
        if isinstance(markov.scanner, CharScanner):
            for _ in ss:
                chars = iter(markov.generate(args.words,
                                             state_size=args.state_size,
                                             start=state))
                prev = next(chars)

                if state is not None:
                    print(args.start, end='', file=args.output)
                    start = False
                else:
                    start = True

                for char in chars:
                    if ispunct(prev):
                        if prev in '.!?':
                            start = True
                    elif not prev.isspace():
                        if start:
                            prev = prev.upper()
                            start = False
                    if prev != '\n':
                        print(prev, end='', file=args.output)
                    prev = char
                if prev == '\n':
                    prev = ''
                elif not ispunct(prev):
                    prev += '.'
                print(prev, file=args.output)
        else:
            for _ in ss:
                words = iter(markov.generate(args.words,
                                             state_size=args.state_size,
                                             start=state))
                first = next(words)

                if state is not None:
                    print(args.start,
                          end='' if state[-1].isspace() else ' ',
                          file=args.output)
                else:
                    first = first.title()

                prev = first

                for word in words:
                    print(prev,
                          end=args.word_separator if not ispunct(word) else '',
                          file=args.output)
                    prev = word
                if not ispunct(prev[-1]):
                    prev += '.'
                print(prev, file=args.output)
    except StopIteration:
        if state is not None:
            print('Not found', file=stderr)
            exit(1)
        raise
