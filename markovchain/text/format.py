import re
from abc import abstractmethod

from ..util import SaveLoad, DOC_INHERIT_ABSTRACT
from .util import CharCase, lstrip_ws_and_chars


class FormatterBase(SaveLoad, metaclass=DOC_INHERIT_ABSTRACT):
    """Text formatter base class."""
    classes = {}

    @abstractmethod
    def __call__(self, string):
        """Format a string.

        Parameters
        ----------
        string : `str`
            String to format.

        Returns
        -------
        `str`
            Formatted string.
        """
        pass


class Noop(FormatterBase):
    """No-op formatter."""
    def __call__(self, string):
        return string


class Formatter(FormatterBase):
    """Default formatter.

    Attributes
    ----------
    case : `markovchain.text.util.CharCase`
        Character case
    replace : `list` of (_sre.SRE_Pattern, `str`)
        List of regular expressions to replace.
    end_chars : `str`
        Sentence ending characters.
    default_end : `None` or `str`
        Default sentence ending character.
    """
    # pylint:disable=bad-whitespace
    DEFAULT_REPLACE = [
        (r'\s+'               , r' '       ),
        (r'\s*([^\w\s]+)\s*'  , r'\1'      ),
        (r'([,.?!])(\w)'      , r'\1 \2'   ),
        (r'([\w,.?!])([[({<])', r'\1 \2'   ),
        (r'([])}>])(\w)'      , r'\1 \2'   ),
        (r'(\w)([-+*]+)(\w)'  , r'\1 \2 \3'),
    ]
    # pylint:enable=bad-whitespace
    def __init__(self,
                 case=CharCase.TITLE,
                 replace=None,
                 end_chars='.?!',
                 default_end='.'):
        """Formatter constructor.

        Parameters
        ----------
        case : `markovchain.text.util.CharCase` or `str`, optional
            Character case
        end_chars : `str`, optional
            Sentence ending characters (default: '.?!').
        default_end : `None` or `str`, optional
            Default sentence ending character (default: '.').
        replace : `list` of (`str`, `str`), optional
            List of regular expressions to replace (default: DEFAULT_REPLACE).
        """
        if replace is None:
            replace = self.DEFAULT_REPLACE
        if isinstance(case, str):
            case = getattr(CharCase, case.upper())
        else:
            case = CharCase(case)
        self.case = case
        self.replace = [(re.compile(expr), repl) for expr, repl in replace]
        self.end_chars = end_chars
        self.default_end = default_end

    def save(self):
        data = super().save()
        data['case'] = self.case
        data['replace'] = [(expr.pattern, repl) for expr, repl in self.replace]
        data['end_chars'] = self.end_chars
        data['default_end'] = self.default_end
        return data

    def __eq__(self, fmt):
        return (
            self.__class__ is fmt.__class__
            and self.case == fmt.case
            and self.replace == fmt.replace
            and self.end_chars == fmt.end_chars
            and self.default_end == fmt.default_end
        )

    def __call__(self, string):
        string = lstrip_ws_and_chars(string.rstrip(), self.end_chars)

        if not string:
            return string

        if self.default_end is not None and string[-1] not in self.end_chars:
            string += self.default_end

        string = self.case.convert(string)

        for expr, repl in self.replace:
            string = re.sub(expr, repl, string)

        return string
