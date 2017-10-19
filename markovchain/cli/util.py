import json
import sys
import os
import bz2
from itertools import chain
from contextlib import contextmanager

try:
    from tqdm import tqdm
    TQDM_IMPORT_ERROR = None
except ImportError as err:
    tqdm = None
    TQDM_IMPORT_ERROR = err

from .. import MarkovBase, MarkovJsonMixin, MarkovSqliteMixin


JSON = 0
SQLITE = 1
IJSON_MIN_SIZE = 4 * 1024 * 1024
IJSON_MIN_COMPRESSED_SIZE = 512 * 1024

BAR_DESC_SIZE = 12
BAR_N_SIZE = 8
BAR_RATE_SIZE = 14
BAR_FORMAT = '{{desc:<{0}.{0}}}{{percentage:3.0f}}%' \
             '|{{bar}}| ' \
             '{{n_fmt:>{1}.{1}}}/{{total_fmt:<{1}.{1}}} '\
             '{{elapsed}}<{{remaining:^5}} {{rate_fmt:>{2}.{2}}}' \
                 .format(BAR_DESC_SIZE, BAR_N_SIZE, BAR_RATE_SIZE)


class NoProgressBar:
    """Missing progress bar class.

    Attributes
    ----------
    warning : `bool`
        True if a missing progress bar warning was printed.
    """
    warning = False

    @classmethod
    def print_warning(cls):
        """Print a missing progress bar warning if it was not printed.
        """
        if not cls.warning:
            cls.warning = True
            print('Can\'t create progress bar:', str(TQDM_IMPORT_ERROR),
                  file=sys.stderr)

    def update(self, *args, **kwargs):
        """Do nothing.
        """
        pass

    def close(self, *args, **kwargs):
        """Do nothing.
        """
        pass


def no_tqdm(iterable=None, *args, **kwargs): # pylint: disable=unused-argument
    """Print a missing progress bar warning if it was not printed.

    Parameters
    ----------
    iterable : `iterable` or `None`, optional
        Iterable to decorate with a progress bar (default: None).

    Returns
    -------
    `iterable` or `markovchain.cli.util.NoProgressBar`
    """
    NoProgressBar.print_warning()
    if iterable is not None:
        return iterable
    return NoProgressBar()

if tqdm is None:
    tqdm = no_tqdm # pylint: disable=invalid-name

def pprint(data, indent=0, end='\n'):
    """Pretty print JSON data.

    Parameters
    ----------
    data
        JSON data.
    indent : `int`, optional
        Indent level in characters (default: 0).
    end : `str`, optional
        String to print after the data (default: '\\\\n').
    """
    if isinstance(data, dict):
        print('{')
        new_indent = indent + 4
        space = ' ' * new_indent
        keys = list(sorted(data.keys()))
        for i, k in enumerate(keys):
            print(space, json.dumps(k), ': ', sep='', end='')
            pprint(data[k], new_indent,
                   end=',\n' if i < len(keys) - 1 else '\n')
        print(' ' * indent, '}', sep='', end=end)
    elif isinstance(data, list):
        if any(isinstance(x, (dict, list)) for x in data):
            print('[')
            new_indent = indent + 4
            space = ' ' * new_indent
            for i, x in enumerate(data):
                print(space, end='')
                pprint(x, new_indent,
                       end=',\n' if i < len(data) - 1 else '\n')
            print(' ' * indent, ']', sep='', end=end)
        else:
            print(json.dumps(data), end=end)
    else:
        print(json.dumps(data), end=end)

def load(markov, fname, args):
    """Load a markov chain generator.

    Parameters
    ----------
    markov : `type`
        Markov chain generator class.
    fname : `str`
        Input file path.
    args : `argparse.Namespace`
        Command arguments.
    """
    if issubclass(markov, MarkovJsonMixin):
        size = os.path.getsize(fname)

        if fname.endswith('bz2'):
            op = bz2.open
            maxsize = IJSON_MIN_COMPRESSED_SIZE
        else:
            op = open
            maxsize = IJSON_MIN_SIZE

        if size > maxsize:
            mode = 'rb'
        else:
            mode = 'rt'

        if args.progress:
            print('Loading JSON data...')

        with op(fname, mode) as fp:
            return markov.load(fp, args.settings)
    else:
        return markov.load(fname, args.settings)

def save(markov, fname, args):
    """Save a markov chain generator.

    Parameters
    ----------
    markov : `MarkovBase`
        Markov chain generator.
    fname : `str`
        Output file path.
    args : `argparse.Namespace`
        Command arguments.
    """
    if isinstance(markov, MarkovJsonMixin):
        if fname is None:
            markov.save(sys.stdout)
        else:
            if fname.endswith('bz2'):
                op = bz2.open
            else:
                op = open

            if args.progress:
                print('Saving JSON data...')

            with op(fname, 'wt') as fp:
                markov.save(fp)
    else:
        markov.save()

def set_args(args, base):
    """Set computed command arguments.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    base : `iterable` of `type`
        Generator mixins.

    Raises
    ------
    ValueError
        If output file is stdout and progress bars are enabled.
    """
    try:
        if args.output is sys.stdout and args.progress:
            raise ValueError('args.output is stdout and args.progress')
    except AttributeError:
        pass

    try:
        fname = '.' + args.type
    except AttributeError:
        try:
            fname = args.state
        except AttributeError:
            try:
                fname = args.output
            except AttributeError:
                fname = '.json'

    if fname is None or fname.endswith('.json') or fname.endswith('.bz2'):
        args.type = JSON
    else:
        args.type = SQLITE

    if args.type == JSON:
        dtype = MarkovJsonMixin
    elif args.type == SQLITE:
        dtype = MarkovSqliteMixin

    base = tuple(chain((dtype,), base, (MarkovBase,)))

    class Markov(*base): # pylint: disable=too-few-public-methods
        pass

    try:
        settings = args.settings
        has_settings = True
    except AttributeError:
        settings = None
        has_settings = False

    if has_settings:
        if settings is not None:
            settings = json.load(settings)
            args.settings.close()
        else:
            settings = {}

    args.settings = settings
    args.markov = Markov

def check_output_format(fmt, nfiles):
    """Validate file format string.

    Parameters
    ----------
    fmt : `str`
        File format string.
    nfiles : `int`
        Number of files.

    Raises
    ------
    ValueError
        If nfiles < 0 or format string is invalid.
    """
    if nfiles < 0:
        raise ValueError('Invalid file count: ' + str(nfiles))
    if nfiles == 1:
        return
    try:
        fmt % nfiles
    except TypeError as err:
        raise ValueError(''.join(
            ('Invalid file format string: ', fmt, ': ', str(err))
        ))

@contextmanager
def infiles(fnames, progress, leave=True):
    """Get input file paths.

    Parameters
    ----------
    fnames : `list` of `str`
        File paths.
    progress : `bool`
        Show progress bar.
    leave : `bool`, optional
        Leave progress bar (default: True).

    Returns
    -------
    `generator` of `str`
        Input file paths.
    """
    if progress:
        if fnames:
            fnames = tqdm(fnames, desc='Loading', unit='file',
                          bar_format=BAR_FORMAT,
                          leave=leave, dynamic_ncols=True)
        else:
            progress = False

    yield fnames

    if progress:
        fnames.close()

@contextmanager
def outfiles(fmt, nfiles, progress, leave=True):
    """Get output file paths.

    Parameters
    ----------
    fmt : `str`
        File path format string.
    nfiles : `int`
        Number of files.
    progress : `bool`
        Show progress bars.
    leave : `bool`, optional
        Leave progress bar (default: True).

    Raises
    ------
    ValueError
        If nfiles <= 0.

    Returns
    -------
    `generator` of `str`
        Output file paths.
    """
    if nfiles > 1:
        fnames = (fmt % i for i in range(nfiles))
    elif nfiles == 1:
        fnames = (fmt,)
    else:
        raise ValueError('output file count <= 0')

    if progress:
        fnames = tqdm(fnames, total=nfiles,
                      desc='Generating', unit='file',
                      bar_format=BAR_FORMAT,
                      leave=leave, dynamic_ncols=True)

    yield fnames

    if progress:
        fnames.close()

def cmd_settings(args):
    """Print generator settings.

    Parameters
    ----------
    args : `argparse.Namespace`
        Command arguments.
    """
    markov = load(args.markov, args.state, args)
    data = markov.get_save_data()
    try:
        del data['nodes']
    except KeyError:
        pass
    pprint(data)
