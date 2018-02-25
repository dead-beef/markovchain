import sys
import json
from random import randint

from .base import Storage


class JsonStorage(Storage):
    """JSON storage.

    Attributes
    ----------
    nodes : `dict` of ((`str`, `int`) or (`list` of `str`, `list` of `int`))
    """
    def __init__(self, nodes=None, settings=None):
        """JSON storage constructor.

        Parameters
        ----------
            nodes : `dict` of ((`str`, `int`) or (`list` of `str`, `list` of `int`)), optional
        """
        if nodes is None:
            nodes = {}
        super().__init__(settings)
        self.nodes = nodes

    def __eq__(self, storage):
        return (self.nodes == storage.nodes
                and super().__eq__(storage))

    def replace_state_separator(self, old_separator, new_separator):
        self.nodes = dict(
            (k.replace(old_separator, new_separator), v)
            for k, v in self.nodes.items()
        )

    def links(self, links):
        for src, dst in links:
            src = self.join_state(src)
            try:
                node = self.nodes[src]
                nodes, values = node
                if isinstance(nodes, list):
                    try:
                        idx = nodes.index(dst)
                        values[idx] += 1
                    except ValueError:
                        nodes.append(dst)
                        values.append(1)
                elif nodes == dst:
                    node[1] += 1
                else:
                    node[0] = [nodes, dst]
                    node[1] = [values, 1]
            except KeyError:
                self.nodes[src] = [dst, 1]

    def random_link(self, state):
        try:
            node = self.nodes[self.join_state(state)]
            if not isinstance(node[0], list):
                state.append(node[0])
                return node[0], state
        except KeyError:
            return None, None

        nodes, values = node
        link_sum = sum(values)

        x = randint(0, link_sum - 1)
        for value, count in zip(nodes, values):
            if x < count:
                state.append(value)
                return value, state
            x -= count

        raise ValueError('invalid link sum: ' + str(self))

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
