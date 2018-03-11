import sys
import json
from collections import deque
from itertools import chain, repeat

from .base import Storage


class JsonStorage(Storage):
    """JSON storage.

    Attributes
    ----------
    nodes : `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`])
    """
    def __init__(self, nodes=None, settings=None):
        """JSON storage constructor.

        Parameters
        ----------
            nodes : `dict` of `dict` of ([`int`, `str`] or [`list` of `int`, `list` of `str`]), optional
        """
        if nodes is None:
            nodes = {}
        super().__init__(settings)
        self.nodes = nodes

    def __eq__(self, storage):
        return (self.nodes == storage.nodes
                and super().__eq__(storage))

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
        for key, data in self.nodes.items():
            self.nodes[key] = dict(
                (k.replace(old_separator, new_separator), v)
                for k, v in data.items()
            )

    def get_dataset(self, key, create=False):
        try:
            return self.nodes[key]
        except KeyError:
            if create:
                data = {}
                self.nodes[key] = data
                return data
            else:
                raise

    def add_links(self, links, dataset_prefix=''):
        for dataset, src, dst in links:
            dataset = self.get_dataset(dataset_prefix + dataset, True)
            src = self.join_state(src)
            self.add_link(dataset, src, dst)

    def get_state(self, state, size):
        return deque(chain(repeat('', size), state), maxlen=size)

    def get_states(self, dataset, string):
        dataset = self.get_dataset(dataset)
        return [key for key in dataset.keys() if string in key]

    def get_links(self, dataset, state, backward=False):
        """
        Raises
        ------
        NotImplementedError
            If backward == `True`.
        """
        if backward:
            raise NotImplementedError()
        try:
            node = dataset[self.join_state(state)]
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
        if fp is None:
            fp = sys.stdout
        data = {
            'settings': self.settings,
            'nodes': self.nodes
        }
        json.dump(data, fp, ensure_ascii=False)

    @classmethod
    def load(cls, fp):
        if isinstance(fp, str):
            with open(fp, 'rt') as fp2:
                data = json.load(fp2)
        else:
            data = json.load(fp)
        return cls(**data)
