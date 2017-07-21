import re

from .util import SaveLoad


class Scanner(SaveLoad):
    classes = {}

    END = None
    START = None

    def __init__(self, scan=None):
        if scan is not None:
            self.scan = scan

    def __call__(self, data, part=False):
        return self.scan(data)

    def reset(self):
        pass


class CharScanner(Scanner):
    def __init__(self, end_chars='.?!', default_end='.'):
        super().__init__()
        self.end_chars = end_chars
        self.default_end = default_end
        self.start = False
        self.end = False

    def reset(self):
        self.start = False
        self.end = False

    def __call__(self, data, part=False):
        if not self.end_chars:
            yield from data
            self.start = self.start or bool(data)
            self.end = False
        else:
            for char in data:
                if char in self.end_chars:
                    if not self.start:
                        continue
                    self.end = True
                else:
                    if self.end:
                        yield self.END
                        self.end = False
                    self.start = True
                yield char

        if not part and self.start:
            if not self.end and self.default_end is not None:
                yield self.default_end
            yield self.END
            self.reset()

    def __eq__(self, scanner):
        return (self.end_chars == scanner.end_chars
                and self.default_end == scanner.default_end)

    def save(self):
        data = super().save()
        data['end_chars'] = self.end_chars
        data['default_end'] = self.default_end
        return data


class RegExpScanner(Scanner):
    DEFAULT_EXPR = re.compile(
        r'(?:(?P<end>[.!?]+)|(?P<word>(?:[^\w\s]+|\w+)))'
    )

    @staticmethod
    def get_regexp(x):
        if isinstance(x, str):
            return re.compile(x)
        return x

    @staticmethod
    def get_group(match, group):
        try:
            return match.group(group)
        except IndexError:
            return None

    def __init__(self, expr=DEFAULT_EXPR, default_end='.'):
        super().__init__()
        self.expr = self.get_regexp(expr)
        self.default_end = default_end
        self.end = True

    def reset(self):
        self.end = True

    def __call__(self, data, part=False):
        if not self.expr.groups:
            for match in self.expr.finditer(data):
                yield match.group()

            self.end = self.end and not bool(data)
        else:
            for match in self.expr.finditer(data):
                group = self.get_group(match, 'end')
                if group is not None:
                    if not self.end:
                        yield group
                        yield self.END
                        self.end = True
                else:
                    self.end = False
                    group = self.get_group(match, 'word')
                    if group is not None:
                        yield group
                    else:
                        yield match.group()

        if not part and not self.end:
            if self.default_end is not None:
                yield self.default_end
            yield self.END
            self.reset()

    def __eq__(self, scanner):
        return (self.expr == scanner.expr
                and self.default_end == scanner.default_end)

    def save(self):
        data = super().save()
        data['expr'] = self.expr.pattern
        data['default_end'] = self.default_end
        return data
