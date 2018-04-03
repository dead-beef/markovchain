import re
import enum


RE_PUNCT = re.compile(r'^[^\w\s]+$')
RE_WORD = re.compile(r'\w+')


class CharCase(enum.IntEnum):
    """Character case."""
    PRESERVE = 0
    TITLE = 1
    UPPER = 2
    LOWER = 3

    def convert(self, string):
        if self == self.__class__.TITLE:
            return capitalize(string)
        if self == self.__class__.UPPER:
            return string.upper()
        if self == self.__class__.LOWER:
            return string.lower()
        return string


def ispunct(string):
    """Return `True` if all characters in a string are punctuation
    and it is not empty.

    Parameters
    ----------
    string : `str`

    Returns
    -------
    `bool`

    Examples
    --------
    >>> ispunct('.,?')
    True
    >>> ispunct('.x.')
    False
    >>> ispunct('. ')
    False
    >>> ispunct('')
    False
    """
    return RE_PUNCT.match(string) is not None

def get_words(string):
    """Find all words in a string.

    Parameters
    ----------
    string : `str`

    Returns
    -------
    `list` of `str`

    Examples
    --------
    >>> get_words('  ..?!word  ,  (Word)..  word')
    ['word', 'Word', 'word']
    """
    return RE_WORD.findall(string)

def lstrip_ws_and_chars(string, chars):
    """Remove leading whitespace and characters from a string.

    Parameters
    ----------
    string : `str`
        String to strip.
    chars : `str`
        Characters to remove.

    Returns
    -------
    `str`
        Stripped string.

    Examples
    --------
    >>> lstrip_ws_and_chars(' \\t.\\n , .x. ', '.,?!')
    'x. '
    """
    res = string.lstrip().lstrip(chars)
    while len(res) != len(string):
        string = res
        res = string.lstrip().lstrip(chars)
    return res

def capitalize(string):
    """Capitalize a sentence.

    Parameters
    ----------
    string : `str`
        String to capitalize.

    Returns
    -------
    `str`
        Capitalized string.

    Examples
    --------
    >>> capitalize('worD WORD WoRd')
    'Word word word'
    """
    if not string:
        return string
    if len(string) == 1:
        return string.upper()
    return string[0].upper() + string[1:].lower()
