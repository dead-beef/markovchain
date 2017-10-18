import json
from random import randint

try:
    import ijson.backends.yajl2_cffi as ijson
except ImportError:
    try:
        import ijson.backends.yajl2 as ijson
    except ImportError:
        try:
            import ijson
        except ImportError:
            ijson = None

from .util import extend


class MarkovJsonMixin:
    """Markov chain JSON data mixin.

    Attributes
    ----------
    nodes : `dict` of ((`str`, `int`) or (`list` of `str`, `list` of `int`))
    """
    def __init__(self, nodes=None, *args, **kwargs):
        """Markov chain JSON data constructor.

        Attributes
        ----------
            nodes : `dict` of ((`str`, `int`) or (`list` of `str`, `list` of `int`)), optional
        """
        super().__init__(*args, **kwargs)
        if not nodes:
            self.nodes = {}
        else:
            self.nodes = nodes

    def __eq__(self, markov):
        return (self.nodes == markov.nodes
                and super().__eq__(markov))

    def replace_state_separator(self, old_separator, new_separator):
        """Replace state separator.

        Parameters
        ----------
        old_separator : `str`
            Old state separator.
        new_separator : `str`
            New state separator.
        """
        self.nodes = dict(
            (k.replace(old_separator, new_separator), v)
            for k, v in self.nodes.items()
        )
        #for node, (nodes, values) in self.nodes.items():
        #    if isinstance(nodes, list):
        #        for i, k in enumerate(nodes):
        #            nodes[i] = k.replace(old_separator, new_separator)
        #    else:
        #        self.nodes[node] = (
        #            nodes.replace(old_separator, new_separator),
        #            values
        #        )

    def links(self, links):
        """Update links.

        Parameters
        ----------
        links : `generator` of (`islice` of `str`, `str`)
            Links to add.
        """
        for src, dst in links:
            src = self.separator.join(src)
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
        try:
            node = self.nodes[self.separator.join(state)]
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

    @classmethod
    def load(cls, fp, override=None):
        """Load a generator.

        Parameters
        ----------
        fp : `file` or `str`
            Input file or file path.
        override : `dict` or `None`, optional
            Changes to loaded data (default: `None`).

        Returns
        -------
        `markovchain.base.MarkovBase`
            Loaded generator.
        """
        if isinstance(fp, str):
            with open(fp, 'r') as fp2:
                return cls.load(fp2, override)

        x = fp.read(1)
        fp.seek(0)

        if isinstance(x, str):
            data = json.load(fp)
        elif ijson is not None:
            try:
                data = next(ijson.items(fp, ''))
            except StopIteration:
                data = {}
        else:
            data = json.loads(fp.read().decode('utf-8'))

        if override is not None:
            extend(data, override)

        return cls(**data)

    def save(self, fp):
        """Save the generator.

        Parameters
        ----------
        fp : `file`
            Output file.
        """
        json.dump(self.get_save_data(), fp, ensure_ascii=False)

    def get_save_data(self):
        """Convert the generator to JSON.

        Returns
        -------
        `dict`
            JSON data.
        """
        data = super().get_save_data()
        data['nodes'] = self.nodes
        return data
