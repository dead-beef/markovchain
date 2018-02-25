from .storage import JsonStorage, SqliteStorage
from .scanner import Scanner, CharScanner, RegExpScanner
from .parser import Parser, LevelParser
from .base import Markov
from .text import MarkovText
try:
    from .image import MarkovImage
except ImportError:
    pass

Parser.add_class(Parser, LevelParser)
Scanner.add_class(CharScanner, RegExpScanner)
