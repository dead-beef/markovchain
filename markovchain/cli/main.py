from sys import argv, stderr
from argparse import ArgumentParser

from .util import set_args
from ..text import cli as text
from ..info import CLI_VERSION

try:
    from ..image import cli as image
except ImportError:
    image = None

def main():
    """CLI main function.
    """
    parser = ArgumentParser()
    parser.add_argument('-v', '--version',
                        action='version', version=CLI_VERSION)

    parsers = parser.add_subparsers(dest='dtype')

    text.create_arg_parser(parsers.add_parser('text'))
    if image is not None:
        image.create_arg_parser(parsers.add_parser('image'))

    if len(argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    dtype = globals()[args.dtype]
    try:
        set_args(args, dtype.BASE)
        cmd = getattr(dtype, 'cmd_' + args.command)
        cmd(args)
    except ValueError as err:
        print(str(err), file=stderr)
        exit(1)
