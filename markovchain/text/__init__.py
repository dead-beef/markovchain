from .markov import MarkovText
from .format import FormatterBase, Noop, Formatter


FormatterBase.add_class(Noop, Formatter)
