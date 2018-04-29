from .storage import JsonStorage, SqliteStorage
from .scanner import Scanner
from .parser import Parser, LevelParser
from .base import Markov

Parser.add_class(Parser, LevelParser)
