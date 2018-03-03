from .markov import MarkovImage
from .scanner import ImageScanner
from .traversal import Traversal, HLines, VLines, Spiral, Blocks, Hilbert
from .type import ImageType, RGB, Grayscale, Indexed

from ..scanner import Scanner
from ..parser import Parser, LevelParser

Scanner.add_class(ImageScanner)
Traversal.add_class(HLines, VLines, Spiral, Blocks, Hilbert)
ImageType.add_class(RGB, Grayscale, Indexed)
