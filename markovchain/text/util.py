import re

FORMAT_REPLACE = [(re.compile(expr), repl) for expr, repl in [
    (r'\s+'               , r' '       ), # pylint:disable=bad-whitespace
    (r'\s*([^\w\s]+)\s*'  , r'\1'      ), # pylint:disable=bad-whitespace
    (r'([,.?!])(\w)'      , r'\1 \2'   ), # pylint:disable=bad-whitespace
    (r'([\w,.?!])([[({<])', r'\1 \2'   ), # pylint:disable=bad-whitespace
    (r'([])}>])(\w)'      , r'\1 \2'   ), # pylint:disable=bad-whitespace
    (r'(\w)([-+*]+)(\w)'  , r'\1 \2 \3'), # pylint:disable=bad-whitespace
]]

RE_PUNCT = re.compile(r'^[^\w\s]+$')

def ispunct(string):
    """Return `True` if all characters in a string are punctuation
       and it is not empty.

    Parameters
    ----------
    string : `str`

    Returns
    -------
    `bool`
    """
    return RE_PUNCT.match(string) is not None

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

def format_sentence_string(string, end_chars='.?!', default_end='.'):
    """Format a sentence.

    Parameters
    ----------
    string : `str`
        Sentence.
    end_chars : `str`, optional
        Sentence ending characters (default: '.?!').
    default_end : `str`, optional
        Default sentence ending character (default: '.').

    Returns
    -------
    str
        Formatted sentence.

    Examples
    --------
    >>> format_sentence_string('  ..?!word  ,  (word)..  word')
    'Word, (word).. word.'
    >>> format_sentence_string('word WORD', default_end='?')
    'Word word?'
    >>> format_sentence_string('word,', end_chars=',')
    'Word,'
    """
    string = lstrip_ws_and_chars(string.rstrip(), end_chars)

    if not string:
        return string

    if string[-1] not in end_chars:
        string += default_end

    string = capitalize(string)

    for expr, repl in FORMAT_REPLACE:
        string = re.sub(expr, repl, string)

    return string

def format_sentence(parts, join_with=' ', end_chars='.?!', default_end='.'):
    """Format a sentence.

    Parameters
    ----------
    parts : `str` or `iterable` of `str`
        Sentence parts.
    join_with : `str`, optional
        Part separator (default: ' ').
    end_chars : `str`, optional
        Sentence ending characters (default: '.?!').
    default_end : `str`, optional
        Default sentence ending character (default: '.').

    Returns
    -------
    str
        Formatted sentence.

    Examples
    --------
    >>> format_sentence('word WORD', default_end='?')
    'Word word?'
    >>> format_sentence('word,', end_chars=',')
    'Word,'
    >>> format_sentence('word' for _ in range(3))
    'Word word word.'
    >>> format_sentence(('word' for _ in range(3)), join_with=',')
    'Word, word, word.'
    """
    if isinstance(parts, str):
        sentence = parts
    else:
        sentence = join_with.join(parts)

    return format_sentence_string(sentence, end_chars, default_end)
