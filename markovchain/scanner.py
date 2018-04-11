from .util import SaveLoad


class Scanner(SaveLoad):
    """Base scanner class.

    Attributes
    ----------
    classes : `dict`
        Scanner class group.
    START
        Sentence start token.
    END
        Sentence end token.

    Examples
    --------
    >>> scan = Scanner(lambda data: data.split())
    >>> scan('a b c')
    ['a', 'b', 'c']
    """

    classes = {}

    END = None
    START = None

    def __init__(self, scan=None):
        """Base scanner constructor.

        Parameters
        ----------
        scan : `function`, optional
        """
        if scan is not None:
            self.do_scan = scan

    def __call__(self, data, part=False):
        """Scan data.

        Parameters
        ----------
        data
            Data to scan.
        part : `bool`, optional
            `True` if data is partial (default: `False`).

        Returns
        -------
        `object`
            self.scan(data)
        """
        if self.do_scan is None:
            return data
        return self.do_scan(data)

    def reset(self):
        """Reset scanner state.
        """
        pass
