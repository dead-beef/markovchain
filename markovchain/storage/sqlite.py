import json
import sqlite3
from random import randint
from itertools import chain, islice, tee

from .base import Storage


class SqliteStorage(Storage):
    """SQLite storage.

    Attributes
    ----------
    db : `sqlite3.Connection`
        Database connection.
    cursor
        Database cursor.
    """
    def __init__(self, db=':memory:', settings=None):
        """SQLite storage constructor.

        Parameters
        ----------
        db : `str` or `sqlite3.Connection`, optional
            Database path or connection (default: ':memory:').
        settings: `dict`, optional
        """
        super().__init__(settings)
        if isinstance(db, str):
            db = sqlite3.connect(db, isolation_level='IMMEDIATE')
        self.db = db
        self.cursor = db.cursor()
        self.create_node_tables()
        self.update_main_table()
        self.cursor.execute('SELECT key, id FROM datasets')
        self.datasets = dict(self.cursor.fetchall())

    def __eq__(self, markov):
        raise NotImplementedError()
        #return super().__eq__(markov)

    def replace_state_separator(self, old_separator, new_separator):
        self.cursor.execute(
            'UPDATE nodes SET value = replace(value, ?, ?)',
            (old_separator, new_separator)
        )

    def get_dataset(self, key, create=False):
        try:
            return self.datasets[key]
        except KeyError:
            if not create:
                raise
            self.cursor.execute(
                'INSERT INTO datasets (key) VALUES (?)',
                (key,)
            )
            ret = self.cursor.lastrowid
            self.datasets[key] = ret
            return ret

    def add_links(self, links, dataset_prefix=''):
        for dataset, src, dst in links:
            src, src2 = tee(src)
            source = self.get_node(self.join_state(src))
            if dst is None:
                target = None
            else:
                target = self.get_node(self.join_state(
                    chain(islice(src2, 1, None), (dst,))
                ))
            dataset = self.get_dataset(dataset_prefix + dataset, True)
            self.cursor.execute(
                '''UPDATE links
                   SET count = count + 1
                   WHERE source=? AND target=? AND dataset=?''',
                (source, target, dataset)
            )
            self.cursor.execute(
                '''INSERT INTO links (dataset, source, target, value)
                   SELECT ?, ?, ?, ?
                   WHERE (SELECT Changes() = 0)''',
                (dataset, source, target, dst)
            )

    def random_link(self, dataset, state):
        if not isinstance(state, int):
            self.cursor.execute(
                'SELECT id FROM nodes WHERE value=?',
                (self.join_state(state),)
            )
            x = state
            state = self.cursor.fetchone()
            if state is None:
                return None, None
            state = state[0]

        self.cursor.execute(
            '''SELECT count, value, target
               FROM links
               WHERE dataset=? AND source=?''',
            (dataset, state)
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
        data = (json.dumps(self.settings),)
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
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                value TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                dataset REFERENCES datasets (id),
                source REFERENCES nodes (id),
                target REFERENCES nodes (id),
                value TEXT,
                count INTEGER NOT NULL DEFAULT 1
            )
        ''')
        self.cursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS node ON nodes (value)'
        )
        self.cursor.execute(
            'CREATE INDEX IF NOT EXISTS link_dataset ON links (dataset)'
        )
        self.cursor.execute(
            'CREATE INDEX IF NOT EXISTS link_source ON links (source)'
        )
        #self.cursor.execute(
        #    'CREATE INDEX IF NOT EXISTS link_target ON links (target)'
        #)

    def do_save(self, fp=None):
        """Save.

        Parameters
        ----------
        fp : `None`, optional
        """
        if fp is not None:
            raise NotImplementedError()
        self.update_main_table()
        self.db.commit()

    @classmethod
    def load(cls, fp):
        if not isinstance(fp, sqlite3.Connection):
            if not isinstance(fp, str):
                fp.close()
                fp = fp.name
            fp = sqlite3.connect(fp, isolation_level='IMMEDIATE')

        cursor = fp.cursor()
        try:
            cursor.execute('SELECT settings FROM main')
            settings = json.loads(cursor.fetchone()[0])
        except sqlite3.OperationalError:
            settings = None

        return cls(fp, settings)
