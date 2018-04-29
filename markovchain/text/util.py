import re
import enum


RE_PUNCT = re.compile(r'^[^\w\s]+$')
RE_WORD = re.compile(r'\w+')

RE_FLAGS = 'AILMSUX'
RE_CUSTOM_FLAGS = 'O'


class ReplyMode(enum.IntEnum):
    """Text reply mode.
    """
    END = 0
    START = 1
    REPLY = 2


class CharCase(enum.IntEnum):
    """Character case."""
    PRESERVE = 0
    TITLE = 1
    UPPER = 2
    LOWER = 3

    def convert(self, string):
        """Return a copy of string converted to case.

        Parameters
        ----------
        string : `str`

        Returns
        -------
        `str`

        Examples
        --------
        >>> CharCase.LOWER.convert('sTr InG')
        'str ing'
        >>> CharCase.UPPER.convert('sTr InG')
        'STR ING'
        >>> CharCase.TITLE.convert('sTr InG')
        'Str ing'
        >>> CharCase.PRESERVE.convert('sTr InG')
        'sTr InG'
        """
        if self == self.__class__.TITLE:
            return capitalize(string)
        if self == self.__class__.UPPER:
            return string.upper()
        if self == self.__class__.LOWER:
            return string.lower()
        return string


class ReFlags(enum.IntEnum):
    """Custom regexp flags.

    Attributes
    ----------
    O : `int`
    OVERLAP : `int`
        Replace overlapping occurrences of pattern.
    """
    O = 1
    OVERLAP = 1


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


def re_flags(flags, custom=ReFlags):
    """Parse regexp flag string.

    Parameters
    ----------
    flags: `str`
        Flag string.
    custom: `IntEnum`, optional
        Custom flag enum (default: None).

    Returns
    -------
    (`int`, `int`)
        (flags for `re.compile`, custom flags)

    Raises
    ------
    ValueError
    """
    re_, custom_ = 0, 0
    for flag in flags.upper():
        try:
            re_ |= getattr(re, flag)
        except AttributeError:
            if custom is not None:
                try:
                    custom_ |= getattr(custom, flag)
                except AttributeError:
                    raise ValueError('Invalid custom flag "%s"' % flag)
            else:
                raise ValueError('Invalid regexp flag "%s"' % flag)
    return re_, custom_

def re_flags_str(flags, custom_flags):
    """Convert regexp flags to string.

    Parameters
    ----------
    flags : `int`
        Flags.
    custom_flags : `int`
        Custom flags.

    Returns
    -------
    `str`
        Flag string.
    """
    res = ''
    for flag in RE_FLAGS:
        if flags & getattr(re, flag):
            res += flag
    for flag in RE_CUSTOM_FLAGS:
        if custom_flags & getattr(ReFlags, flag):
            res += flag
    return res

def re_sub(pattern, repl, string, count=0, flags=0, custom_flags=0):
    """Replace regular expression.

    Parameters
    ----------
    pattern : `str` or `_sre.SRE_Pattern`
        Compiled regular expression.
    repl : `str` or `function`
        Replacement.
    string : `str`
        Input string.
    count: `int`
        Maximum number of pattern occurrences.
    flags : `int`
        Flags.
    custom_flags : `int`
        Custom flags.
    """
    if custom_flags & ReFlags.OVERLAP:
        prev_string = None
        while string != prev_string:
            prev_string = string
            string = re.sub(pattern, repl, string, count, flags)
        return string
    return re.sub(pattern, repl, string, count, flags)
