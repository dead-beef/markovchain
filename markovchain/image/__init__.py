from .markov import MarkovImageMixin
from .scanner import ImageScanner
from .traversal import Traversal, HLines, VLines, Spiral, Blocks, Hilbert

from ..scanner import Scanner
from ..parser import Parser, LevelParser

Scanner.add_class(ImageScanner)
Traversal.add_class(HLines, VLines, Spiral, Blocks, Hilbert)
