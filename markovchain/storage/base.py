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

    def split_state(self, state):
        """Split state string.

        Parameters
        ----------
        state : `str`

        Returns
        -------
        `list` of `str`
        """
        return state.split(self.state_separator)

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
    def links(self, links):
        """Add links.

        Parameters
        ----------
        links : `generator` of (`islice` of `str`, `str`)
            Links to add.
        """
        pass

    @abstractmethod
    def random_link(self, state):
        """Get a random link.

        Parameters
        ----------
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
