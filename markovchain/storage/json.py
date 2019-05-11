import sys
import json
from collections import deque
from itertools import chain, repeat, tee

from .base import Storage


class JsonStorage(Storage):
    """JSON storage.

    Attributes
    ----------
    nodes : `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
    backward : `None` or `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
    """
    def __init__(self, nodes=None, backward=None, settings=None):
        """JSON storage constructor.

        Parameters
        ----------
            nodes : `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`]), optional
            backward : `bool` or `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`]), optional
        """
        if nodes is None:
            nodes = {}

        if backward is None:
            if settings is not None:
                if settings.get('storage', {}).get('backward', False):
                    backward = {}
                else:
                    backward = None
        elif isinstance(backward, bool):
            if backward:
                backward = {}
            else:
                backward = None

        super().__init__(settings)
        self.nodes = nodes
        self.backward = backward

    def __eq__(self, storage):
        return (self.nodes == storage.nodes
                and self.backward == storage.backward
                and super().__eq__(storage))

    @staticmethod
    def do_replace_state_separator(data, old, new):
        """Replace state separator.

        Parameters
        ----------
        data : `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
            Data.
        old : `str`
            Old separator.
        new : `str`
            New separator.
        """
        for key, dataset in data.items():
            data[key] = dict(
                (k.replace(old, new), v)
                for k, v in dataset.items()
            )

    @staticmethod
    def do_get_dataset(data, key, create=False):
        """Get a dataset.

        Parameters
        ----------
        data : `None` or `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
            Data.
        key : `str`
            Dataset key.
        create : `bool`, optional
            Create a dataset if it does not exist.

        Returns
        -------
        `None` or `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
        """
        if data is None:
            return None
        try:
            return data[key]
        except KeyError:
            if create:
                dataset = {}
                data[key] = dataset
                return dataset
            else:
                raise

    @staticmethod
    def add_link(dataset, source, target, count=1):
        """Add a link.

        Parameters
        ----------
        dataset : `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
            Dataset.
        source : `iterable` of `str`
            Link source.
        target : `str`
            Link target.
        count : `int`, optional
            Link count (default: 1).
        """
        try:
            node = dataset[source]
            values, links = node
            if isinstance(links, list):
                try:
                    idx = links.index(target)
                    values[idx] += count
                except ValueError:
                    links.append(target)
                    values.append(count)
            elif links == target:
                node[0] += count
            else:
                node[0] = [values, count]
                node[1] = [links, target]
        except KeyError:
            dataset[source] = [count, target]

    def replace_state_separator(self, old_separator, new_separator):
        self.do_replace_state_separator(
            self.nodes,
            old_separator,
            new_separator
        )
        if self.backward is not None:
            self.do_replace_state_separator(
                self.backward,
                old_separator,
                new_separator
            )

    def get_dataset(self, key, create=False):
        return (
            self.do_get_dataset(self.nodes, key, create),
            self.do_get_dataset(self.backward, key, create)
        )

    def add_links(self, links, dataset_prefix=''):
        for dataset, src, dst in links:
            forward, backward = self.get_dataset(dataset_prefix + dataset, True)
            if backward is not None and dst is not None:
                src, src2 = tee(src)
                dst2 = next(src2)
                src2 = self.join_state(chain(src2, (dst,)))
                self.add_link(backward, src2, dst2)
            src = self.join_state(src)
            self.add_link(forward, src, dst)

    def get_state(self, state, size):
        return deque(chain(repeat('', size), state), maxlen=size)

    def get_states(self, dataset, string):
        dataset = self.get_dataset(dataset)[0]
        string = string.lower()
        return [key for key in dataset.keys() if string in key.lower()]

    def get_links(self, dataset, state, backward=False):
        """
        Raises
        ------
        ValueError
            If backward == `True` and self.backward is `None`.
        """
        if backward and self.backward is None:
            raise ValueError('no backward nodes')
        try:
            node = dataset[int(backward)][self.join_state(state)]
            if not isinstance(node[0], list):
                return [(node[0], node[1])]
            return list(zip(*node))
        except KeyError:
            return []

    def follow_link(self, link, state, backward=False):
        value = link[1]
        if backward:
            state.appendleft(value)
        else:
            state.append(value)
        return state

    def do_save(self, fp=None):
        """Save to file.

        Parameters
        ----------
        fp : `file` or `str`, optional
            Output file (default: stdout).
        """

        data = {
            'settings': self.settings,
            'nodes': self.nodes,
            'backward': self.backward
        }

        if fp is None:
            json.dump(data, sys.stdout, ensure_ascii=False)
        elif isinstance(fp, str):
            with open(fp, 'w+') as fp2:
                json.dump(data, fp2, ensure_ascii=False)
        else:
            json.dump(data, fp, ensure_ascii=False)

    def close(self):
        pass

    @classmethod
    def load(cls, fp):
        if isinstance(fp, str):
            with open(fp, 'rt') as fp2:
                data = json.load(fp2)
        else:
            data = json.load(fp)
        return cls(**data)
