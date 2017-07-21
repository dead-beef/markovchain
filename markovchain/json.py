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
    def __init__(self, nodes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not nodes:
            self.nodes = {}
        else:
            self.nodes = nodes

    def __eq__(self, markov):
        return (self.nodes == markov.nodes
                and super().__eq__(markov))

    def replace_state_separator(self, old_separator, new_separator):
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
        json.dump(self.get_save_data(), fp, ensure_ascii=False)

    def get_save_data(self):
        data = super().get_save_data()
        data['nodes'] = self.nodes
        return data
