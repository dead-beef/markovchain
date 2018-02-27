import sys
from argparse import ArgumentParser

from . import text
from .util import set_args
from ..info import CLI_VERSION

try:
    from . import image
except ImportError:
    image = None

def main(args=None):
    """CLI main function.

    Parameters
    ----------
    args : `list` of `str`, optional
        CLI arguments (default: `sys.argv`).
    """
    parser = ArgumentParser()
    parser.add_argument('-v', '--version',
                        action='version', version=CLI_VERSION)

    parsers = parser.add_subparsers(dest='dtype')

    text.create_arg_parser(parsers.add_parser('text'))
    if image is not None:
        image.create_arg_parser(parsers.add_parser('image'))

    if len(sys.argv if args is None else args) <= 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(args)
    dtype = globals()[args.dtype]
    try:
        set_args(args)
        cmd = getattr(dtype, 'cmd_' + args.command)
        cmd(args)
    except ValueError as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)
