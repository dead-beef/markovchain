from abc import abstractmethod

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
    def random_link(self, dataset, state):
        """Get a random link.

        Parameters
        ----------
        dataset : `object`
            Dataset from `Storage.get_dataset`.
        state : `deque` of `str`
            Link source.

        Raises
        ------
        ValueError
            If link count is invalid.

        Returns
        -------
        (`str`, `deque` of `str`)
            Link value and updated state.
        """
        pass

    @abstractmethod
    def do_save(self, fp=None):
        """Save to file.

        Parameters
        ----------
        fp : `file`
            Output file.
        """
        pass

    def save(self, fp=None):
        """Update settings JSON data and save to file.

        Parameters
        ----------
        fp : `file`
            Output file.
        """
        self.settings['storage'] = {
            'state_separator': self.state_separator
        }
        self.do_save(fp)

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
