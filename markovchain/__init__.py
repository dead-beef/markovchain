from .scanner import Scanner, CharScanner, RegExpScanner
from .parser import Parser, LevelParser
from .base import MarkovBase
from .json import MarkovJsonMixin
from .sqlite import MarkovSqliteMixin

Parser.add_class(Parser, LevelParser)
Scanner.add_class(CharScanner, RegExpScanner)
