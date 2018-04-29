from .markov import MarkovText
from .formatter import FormatterBase, Noop as NoopFormatter, Formatter
from .rank import Rank, Const as ConstRank, Test as TestRank
from .scanner import CharScanner, RegExpScanner
from .util import ReplyMode
from ..scanner import Scanner


FormatterBase.add_class(NoopFormatter, Formatter)
Rank.add_class(ConstRank, TestRank)
Scanner.add_class(CharScanner, RegExpScanner)
