from .storage import JsonStorage
from .scanner import Scanner
from .parser import ParserBase, Parser
from .util import load, DOC_INHERIT, state_size_dataset


class Markov(metaclass=DOC_INHERIT):
    """Markov chain generator base class.

    Attributes
    ----------
    DEFAULT_SCANNER : `type`
        Default scanner class.
    DEFAULT_PARSER : `type`
        Default parser class.
    DEFAULT_STORAGE : `type`
        Default storage class.
    scanner : `markovchain.scanner.Scanner`
    parser : `markovchain.parser.ParserBase`
    storage : `markovchain.storage.Storage`
    """
    DEFAULT_SCANNER = Scanner
    DEFAULT_PARSER = Parser
    DEFAULT_STORAGE = JsonStorage

    def __init__(self,
                 scanner=None,
                 parser=None,
                 storage=None):
        """Markov chain generator base class constructor.

        Parameters
        ----------
        scanner : `dict` or `markovchain.scanner.Scanner`, optional
            Scanner (default: `DEFAULT_SCANNER()`).
        parser : `dict` or `markovchain.parser.ParserBase`, optional
            Parser (default: `DEFAULT_PARSER()`).
        storage : `markovchain.storage.Storage`, optional
            Parser (default: `DEFAULT_STORAGE()`).
        """
        if storage is None:
            storage = self.DEFAULT_STORAGE()
        #if scanner is None:
        #    scanner = storage.settings.get('scanner', None)
        #if parser is None:
        #    scanner = storage.settings.get('parser', None)
        self.storage = storage
        self.scanner = load(scanner, Scanner, self.DEFAULT_SCANNER)
        self.parser = load(parser, ParserBase, self.DEFAULT_PARSER)

    def __eq__(self, markov):
        return (self.scanner == markov.scanner
                and self.parser == markov.parser
                and self.storage == markov.storage)

    def data(self, data, part=False, dataset=''):
        """Parse data and update links.

        Parameters
        ----------
        data
            Data to parse.
        part : `bool`, optional
            True if data is partial (default: `False`).
        dataset : `str`, optional
            Dataset key prefix (default: '').
        """
        links = self.parser(self.scanner(data, part), part, dataset)
        self.storage.add_links(links)

    def generate(self, state_size=None, start=(), dataset='', backward=False):
        """Generate a sequence.

        Parameters
        ----------
        state_size : `int`, optional
            State size (default: parser.state_sizes[0]).
        start : `str` or `iterable` of `str`, optional
            Initial state (default: ()).
        dataset : `str`, optional
            Dataset key prefix.
        backward : `bool`, optional
            Link direction.

        Returns
        -------
        `generator` of `str`
            State generator.
        """
        if state_size is None:
            try:
                state_size = next(iter(self.parser.state_sizes))
            except StopIteration:
                return
        #elif (self.parser is not None
        #      and state_size not in self.parser.state_sizes):
        #    raise ValueError('invalid state size: {0}: not in {1}'
        #                     .format(state_size, self.parser.state_sizes))
        dataset += state_size_dataset(state_size)
        return self.storage.generate(start, state_size, dataset, backward)

    def get_settings_json(self):
        """Convert generator settings to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        return {
            'scanner': None if self.scanner is None else self.scanner.save(),
            'parser': None if self.parser is None else self.parser.save()
        }

    def save(self, fp=None):
        """Save to file.

        Parameters
        ----------
        fp : `file`, optional
            Output file.
        """
        self.storage.settings['markov'] = self.get_settings_json()
        self.storage.save(fp)

    def close(self):
        """Close.
        """
        self.storage.close()

    @classmethod
    def from_storage(cls, storage):
        """Load from storage.

        Parameters
        ----------
        storage : `markovchain.storage.Storage`

        Returns
        -------
        `markovchain.Markov`
        """
        args = dict(storage.settings.get('markov', {}))
        args['storage'] = storage
        return cls(**args)

    @classmethod
    def from_file(cls, fp, storage=None):
        """Load from file.

        Parameters
        ----------
        fp : `str` or `file`
            File or path.
        storage : `type`, optional
            Storage class (default: cls.DEFAULT_STORAGE)

        Returns
        -------
        `markovchain.Markov`
        """
        if storage is None:
            storage = cls.DEFAULT_STORAGE
        return cls.from_storage(storage.load(fp))

    @classmethod
    def from_settings(cls, settings=None, storage=None):
        """Create from settings.

        Parameters
        ----------
        settings : `dict`, optional
            Settings (default: None).
        storage : `type`, optional
            Storage class (default: cls.DEFAULT_STORAGE)

        Returns
        -------
        `markovchain.Markov`
        """
        if storage is None:
            storage = cls.DEFAULT_STORAGE
        return cls.from_storage(storage(settings=settings))
