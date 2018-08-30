from abc import abstractmethod
from random import randint

from ..util import DOC_INHERIT_ABSTRACT


class Storage(metaclass=DOC_INHERIT_ABSTRACT):
    """Storage base class.

    Attributes
    ----------
    settings : `dict`
    state_separator : `str`
    """

    def __init__(self, settings=None):
        """Storage base constructor.

        Parameters
        ----------
        settings: `dict`, optional
        """
        if settings is None:
            settings = {}
        self.settings = settings
        sep = settings.get('storage', {}).get('state_separator', ' ')
        self._state_separator = sep

    def __eq__(self, storage):
        return self.settings == storage.settings

    @property
    def state_separator(self):
        """`str` : State separator.
        """
        return self._state_separator

    @state_separator.setter
    def state_separator(self, separator):
        if self._state_separator is not None:
            self.replace_state_separator(self._state_separator, separator)
        self._state_separator = separator

    def split_state(self, state):
        """Split state string.

        Parameters
        ----------
        state : `str`

        Returns
        -------
        `list` of `str`
        """
        if self.state_separator:
            return state.split(self.state_separator)
        return list(state)

    def join_state(self, state):
        """Join states.

        Parameters
        ----------
        state : `iterable` of `str`

        Returns
        -------
        `str`
        """
        return self.state_separator.join(state)

    def random_link(self, dataset, state, backward=False):
        """Get a random link.

        Parameters
        ----------
        dataset : `object`
            Dataset from `self.get_dataset()`.
        state : `object`
            Link source.
        backward : `bool`, optional
            Link direction.

        Raises
        ------
        ValueError
            If link count is invalid.

        Returns
        -------
        (`str` or `None`, `object` or `None`)
            Link value and next state.
        """
        links = self.get_links(dataset, state, backward)
        if not links:
            return None, None
        x = randint(0, sum(link[0] for link in links) - 1)
        for link in links:
            count = link[0]
            if x < count:
                return link[1], self.follow_link(link, state, backward)
            x -= count
        raise RuntimeError('invalid link sum')

    def generate(self, state, size, dataset, backward=False):
        """Generate a sequence.

        Parameters
        ----------
        state : `str` or `iterable` of `str`
            Initial state.
        size : `int`
            State size.
        dataset : `str`
            Dataset key.
        backward : `bool`, optional
            Link direction.

        Returns
        -------
        `generator` of `str`
            Node value generator.
        """
        if isinstance(state, str):
            state = self.split_state(state)
        state = self.get_state(state, size)
        dataset = self.get_dataset(dataset)
        while True:
            link, state = self.random_link(dataset, state, backward)
            if link is None or backward and link == '':
                return
            yield link

    def save(self, fp=None):
        """Update settings JSON data and save to file.

        Parameters
        ----------
        fp : `file` or `str`, optional
            Output file.
        """
        self.settings['storage'] = {
            'state_separator': self.state_separator
        }
        self.do_save(fp)

    @abstractmethod
    def close(self):
        """Close."""
        pass

    @abstractmethod
    def get_dataset(self, key, create=False):
        """Get data set by key.

        Parameters
        ----------
        key : `str`
            Dataset key.
        create : `bool`, optional
            Create dataset if it does not exist.

        Returns
        -------
        `object`
            Dataset.

        Raises
        ------
        KeyError
            If dataset does not exist and `create` == `False`.
        """
        pass

    @abstractmethod
    def replace_state_separator(self, old_separator, new_separator):
        """Replace state separator.

        Parameters
        ----------
        old_separator : `str`
            Old state separator.
        new_separator : `str`
            New state separator.
        """
        pass

    @abstractmethod
    def add_links(self, links, dataset_prefix=''):
        """Add links.

        Parameters
        ----------
        links : `generator` of (`str`, `islice` of `str`, `str`)
            Links to add.
        dataset_prefix : `str`, optional
            Dataset key prefix.
        """
        pass

    @abstractmethod
    def get_state(self, state, size):
        """Convert strings to state.

        Parameters
        ----------
        state : `iterable` of `str`
            Node values.
        size : `int`
            State size.

        Returns
        -------
        `object`
            State.
        """
        pass

    @abstractmethod
    def get_states(self, dataset, string):
        """Get all states containing a substring.

        Parameters
        ----------
        dataset : `str`
            Dataset key.
        string : `str`
            String to search.

        Returns
        -------
        `list` of `str`
            States.
        """
        pass

    @abstractmethod
    def get_links(self, dataset, state, backward=False):
        """Get links.

        Parameters
        ----------
        dataset : `object`
            Dataset from `self.get_dataset()`.
        state : `object`
            State from `self.get_state()`.
        backward : `bool`, optional
            Link direction.

        Returns
        -------
        `None` or `list` of (`int`, `str`, `object`)
            Links (count, value, data).
        """
        pass

    @abstractmethod
    def follow_link(self, link, state, backward=False):
        """Follow a link.

        Parameters
        ----------
        link : (`int`, `str`, `object`)
            Link to follow.
        state : `object`
            State.
        backward : `bool`, optional
            Link direction.

        Returns
        -------
        `object`
            New state.
        """
        pass

    @abstractmethod
    def do_save(self, fp=None):
        """Save to file.

        Parameters
        ----------
        fp : `file` or `str`, optional
            Output file.
        """
        pass

    @classmethod
    @abstractmethod
    def load(cls, fp):
        """Load from file.

        Parameters
        ----------
        fp : `file` or `str`, optional
            Input file or path.

        Returns
        -------
        `markovchain.storage.Storage`
            Loaded storage.
        """
        pass
