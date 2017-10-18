import json
import sqlite3
from random import randint
from itertools import chain, islice

from .util import extend

class MarkovSqliteMixin:
    """Markov chain SQLite data mixin.

    Attributes
    ----------
    db : `sqlite3.Connection`
        Database connection.
    cursor
        Database cursor.
    """
    def __init__(self, db=':memory:', *args, **kwargs):
        """Markov chain SQLite data constructor.

        Parameters
        ----------
        db : `str` or `sqlite3.Connection`, optional
            Database path or connection (default: ':memory:').
        """
        super().__init__(*args, **kwargs)
        if isinstance(db, str):
            db = sqlite3.connect(db, isolation_level='IMMEDIATE')
        self.db = db
        self.cursor = db.cursor()
        self.create_node_tables()

    def __eq__(self, markov):
        return super().__eq__(markov)

    def replace_state_separator(self, old_separator, new_separator):
        """Replace state separator.

        Parameters
        ----------
        old_separator : `str`
            Old state separator.
        new_separator : `str`
            New state separator.
        """
        self.cursor.execute(
            'UPDATE nodes SET value = replace(value, ?, ?)',
            (old_separator, new_separator)
        )

    def links(self, links):
        """Update links.

        Parameters
        ----------
        links : `generator` of (`islice` of `str`, `str`)
            Links to add.
        """
        for src, dst in links:
            src = list(src)
            source = self.get_node(self.separator.join(src))
            target = self.get_node(self.separator.join(
                chain(islice(src, 1, None), (dst,))
            ))
            self.cursor.execute(
                'UPDATE links SET count = count + 1 WHERE source=? AND target=?',
                (source, target)
            )
            self.cursor.execute(
                '''INSERT INTO links (source, target, value)
                   SELECT ?, ?, ?
                   WHERE (SELECT Changes() = 0)''',
                (source, target, dst)
            )

    def random_link(self, state):
        """Get a random link.

        Parameters
        ----------
        state : `int` or `deque` of `str`
            Link source ID or name.

        Returns
        -------
        (`str`, `int`)
            Link value and next source ID.
        """
        if not isinstance(state, int):
            self.cursor.execute(
                'SELECT id FROM nodes WHERE value=?',
                (self.separator.join(state),)
            )
            x = state
            state = self.cursor.fetchone()
            if state is None:
                return None, None
            state = state[0]

        self.cursor.execute(
            'SELECT count, value, target FROM links WHERE source=?',
            (state,)
        )
        links = self.cursor.fetchall()
        if not links:
            return None, None
        count = sum(link[0] for link in links)
        x = randint(0, count - 1)
        for count, value, target in links:
            if x < count:
                return value, target
            x -= count
        raise RuntimeError('no link')

    def get_tables(self):
        """Get all table names.

        Returns
        -------
        `set` of `str`
        """
        self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table"'
        )
        return set(x[0] for x in self.cursor.fetchall())

    def get_node(self, value):
        """Get node ID by value.

        If a node with the specified value does not exist,
        create it and return its ID.

        Parameters
        ----------
        value : `str`
            Node value.

        Returns
        -------
        `int`
            Node ID.
        """
        while True:
            self.cursor.execute(
                'SELECT id FROM nodes WHERE value=?',
                (value,)
            )
            node = self.cursor.fetchone()
            if node is not None:
                return node[0]
            self.cursor.execute(
                'INSERT INTO nodes (value) VALUES (?)',
                (value,)
            )

    def update_main_table(self):
        """Write generator settings to database.
        """
        data = (json.dumps(self.get_save_data()),)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS main (
                settings TEXT NOT NULL DEFAULT "{}"
            )
        ''')
        self.cursor.execute('SELECT * FROM main')
        if self.cursor.fetchall() == []:
            self.cursor.execute('INSERT INTO main (settings) VALUES (?)', data)
        else:
            self.cursor.execute('UPDATE main SET settings=?', data)

    def create_node_tables(self):
        """Create node and link tables if they don't exist.
        """
        self.cursor.execute('PRAGMA foreign_keys=1')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                value TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                source REFERENCES nodes (id),
                target REFERENCES nodes (id),
                value TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 1
            )
        ''')
        self.cursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS node ON nodes (value)'
        )
        self.cursor.execute(
            'CREATE INDEX IF NOT EXISTS link_source ON links (source)'
        )
        #self.cursor.execute(
        #    'CREATE INDEX IF NOT EXISTS link_target ON links (target)'
        #)

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
        Loaded generator.
        """
        if not isinstance(fp, str):
            fp.close()
            fp = fp.name

        db = sqlite3.connect(fp)

        try:
            cursor = db.cursor()
            cursor.execute('SELECT settings FROM main')
            args = json.loads(cursor.fetchone()[0])
        except sqlite3.OperationalError:
            args = {}
            raise

        if override is not None:
            extend(args, override)

        args['db'] = db

        return cls(**args)

    def save(self):
        """Save the generator.
        """
        self.update_main_table()
        self.db.commit()
