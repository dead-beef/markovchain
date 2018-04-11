from .markov import MarkovText
from .format import FormatterBase, Noop as NoopFormatter, Formatter
from .rank import Rank, Const as ConstRank, Test as TestRank
from .scanner import CharScanner, RegExpScanner
from ..scanner import Scanner


FormatterBase.add_class(NoopFormatter, Formatter)
Rank.add_class(ConstRank, TestRank)
Scanner.add_class(CharScanner, RegExpScanner)
