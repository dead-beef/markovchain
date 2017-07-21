from unittest import TestCase
from unittest.mock import Mock, MagicMock, mock_open, patch

from io import StringIO
from argparse import Namespace
import json
import sys

from markovchain.cli.util import (
    no_tqdm, NoProgressBar,
    pprint,
    load, save, IJSON_MIN_SIZE, IJSON_MIN_COMPRESSED_SIZE,
    set_args, JSON, SQLITE,
    check_output_format,
    infiles, outfiles
)
from markovchain import MarkovBase, MarkovJsonMixin, MarkovSqliteMixin

class TestNoProgressBar(TestCase):
    @patch('sys.stderr', new_callable=StringIO)
    def testWarning(self, stderr):
        p = NoProgressBar()
        self.assertEqual(stderr.getvalue(), '')
        self.assertFalse(p.warning)
        NoProgressBar.print_warning()
        msg = stderr.getvalue()
        self.assertNotEqual(msg, '')
        self.assertTrue(p.warning)
        NoProgressBar.print_warning()
        self.assertEqual(stderr.getvalue(), msg)
        self.assertTrue(p.warning)

    @patch('markovchain.cli.util.NoProgressBar')
    def testNoTqdm(self, no_pbar):
        p = no_tqdm(total=100, leave=False, desc='')
        self.assertIsInstance(p, Mock)
        no_pbar.assert_called_with()
        no_pbar.print_warning.assert_called_with()
        no_pbar.reset_mock()
        it = range(3)
        p = no_tqdm(it)
        self.assertIs(p, it)
        no_pbar.assert_not_called()
        no_pbar.print_warning.assert_called_with()

class TestPPrint(TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def testPPrint(self, stdout):
        tests = [
            {'x': 0, 'y': [{'z': '0'}, {'z': '1'}]},
            [{'x': 0.1, 'y': {'y': False, 'z': None, 'u': 3}}, {'z': 0}]
        ]
        for test in tests:
            stdout.seek(0)
            stdout.truncate(0)
            pprint(test)
            self.assertEqual(
                stdout.getvalue(),
                json.dumps(test, indent=4, sort_keys=True) + '\n'
            )

    @patch('sys.stdout', new_callable=StringIO)
    def testPPrintArray(self, stdout):
        tests = [
            ([], '[]\n'),
            ([0, 1, 2], '[0, 1, 2]\n'),
            ([True, None], '[true, null]\n'),
            ([0, [1, 2], 3], '[\n    0,\n    [1, 2],\n    3\n]\n')
        ]
        for test, res in tests:
            stdout.seek(0)
            stdout.truncate(0)
            pprint(test)
            self.assertEqual(stdout.getvalue(), res)

class TestLoad(TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('bz2.open', new_callable=mock_open)
    @patch('os.path.getsize', return_value=IJSON_MIN_SIZE - 1)
    @patch('sys.stdout', new_callable=StringIO)
    def testOpen(self, stdout, getsize, bz2op, op):
        class Test:
            pass
        Test.load = MagicMock(return_value=0)
        markov = Test
        fname = 'test'
        args = Namespace(progress=False, settings={})

        self.assertEqual(load(markov, fname, args), 0)
        self.assertFalse(getsize.called)
        self.assertFalse(op.called)
        self.assertFalse(bz2op.called)
        markov.load.assert_called_with(fname, args.settings)

        class Test2(MarkovJsonMixin):
            pass
        Test2.load = MagicMock(return_value=0)
        markov = Test2

        self.assertEqual(load(markov, fname, args), 0)
        getsize.assert_called_with(fname)
        op.assert_called_with(fname, 'rt')
        self.assertFalse(bz2op.called)

        getsize.return_value = IJSON_MIN_SIZE + 1
        self.assertEqual(load(markov, fname, args), 0)
        op.assert_called_with(fname, 'rb')
        self.assertFalse(bz2op.called)

        fname = '.bz2'
        getsize.return_value = IJSON_MIN_COMPRESSED_SIZE - 1
        op.called = False
        self.assertEqual(load(markov, fname, args), 0)
        bz2op.assert_called_with(fname, 'rt')
        self.assertFalse(op.called)

        getsize.return_value = IJSON_MIN_COMPRESSED_SIZE + 1
        self.assertEqual(load(markov, fname, args), 0)
        bz2op.assert_called_with(fname, 'rb')
        self.assertFalse(op.called)

        self.assertEqual(stdout.getvalue(), '')

    @patch('builtins.open', new_callable=mock_open)
    @patch('bz2.open', new_callable=mock_open)
    @patch('os.path.getsize', return_value=IJSON_MIN_SIZE - 1)
    @patch('sys.stdout', new_callable=StringIO)
    def testProgress(self, stdout, getsize, bz2op, op): # pylint:disable=unused-argument
        class Test(MarkovJsonMixin):
            pass
        Test.load = MagicMock(return_value=0)
        markov = Test
        fname = 'test'
        args = Namespace(progress=True, settings={})

        self.assertEqual(load(markov, fname, args), 0)
        self.assertNotEqual(stdout.getvalue(), '')

        class Test2():
            pass
        Test2.load = MagicMock(return_value=0)
        markov = Test2
        stdout.seek(0)
        stdout.truncate(0)
        self.assertEqual(load(markov, fname, args), 0)
        self.assertEqual(stdout.getvalue(), '')


class TestSave(TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('bz2.open', new_callable=mock_open)
    @patch('sys.stdout', new_callable=StringIO)
    def testOpen(self, stdout, bz2op, op):
        markov = MagicMock()
        fname = 'test'
        args = Namespace(progress=False)

        save(markov, fname, args)
        self.assertFalse(op.called)
        self.assertFalse(bz2op.called)
        markov.save.assert_called_with()

        markov = MagicMock(spec=MarkovJsonMixin)
        save(markov, fname, args)
        op.assert_called_with(fname, 'wt')
        self.assertFalse(bz2op.called)
        self.assertTrue(markov.save.called)

        markov.save.reset_mock()
        op.called = False
        save(markov, None, args)
        self.assertFalse(op.called)
        self.assertFalse(bz2op.called)
        markov.save.assert_called_with(stdout)

        fname = '.bz2'
        op.called = False
        markov.save.reset_mock()
        save(markov, fname, args)
        bz2op.assert_called_with(fname, 'wt')
        self.assertFalse(op.called)
        self.assertTrue(markov.save.called)

        self.assertEqual(stdout.getvalue(), '')

    @patch('builtins.open', new_callable=mock_open)
    @patch('bz2.open', new_callable=mock_open)
    @patch('sys.stdout', new_callable=StringIO)
    def testProgress(self, stdout, bz2op, op): # pylint:disable=unused-argument
        markov = MagicMock(spec=MarkovJsonMixin)
        fname = 'test'
        args = Namespace(progress=True)

        save(markov, fname, args)
        self.assertNotEqual(stdout.getvalue(), '')

        stdout.seek(0)
        stdout.truncate(0)
        save(markov, None, args)
        self.assertEqual(stdout.getvalue(), '')

        markov = MagicMock()
        save(markov, fname, args)
        self.assertEqual(stdout.getvalue(), '')


class TestSetArgs(TestCase):
    def testErrors(self):
        args = Namespace(output=sys.stdout, progress=True)
        with self.assertRaises(ValueError):
            set_args(args, ())

    def testType(self):
        args = Namespace()
        set_args(args, ())
        self.assertEqual(args.type, JSON)
        self.assertTrue(issubclass(args.markov, MarkovBase))
        self.assertTrue(issubclass(args.markov, MarkovJsonMixin))

        args = Namespace()
        set_args(args, (Mock,))
        self.assertEqual(args.type, JSON)
        self.assertTrue(issubclass(args.markov, Mock))
        self.assertTrue(issubclass(args.markov, MarkovBase))
        self.assertTrue(issubclass(args.markov, MarkovJsonMixin))

        args = Namespace(output='.db')
        set_args(args, ())
        self.assertEqual(args.type, SQLITE)
        self.assertTrue(issubclass(args.markov, MarkovBase))
        self.assertTrue(issubclass(args.markov, MarkovSqliteMixin))

        args = Namespace(output='.db', state='.json.bz2')
        set_args(args, ())
        self.assertEqual(args.type, JSON)

        args = Namespace(output='.db', state='.json.bz2', type='sqlite')
        set_args(args, ())
        self.assertEqual(args.type, SQLITE)

        args = Namespace(output='.db', state='.json.bz2', type='json')
        set_args(args, ())
        self.assertEqual(args.type, JSON)

    @patch('json.load', new=lambda x: x())
    def testSettings(self):
        args = Namespace()
        set_args(args, ())
        self.assertIsNone(args.settings)

        args = Namespace(settings=None)
        set_args(args, ())
        self.assertEqual(args.settings, {})

        s = list(range(3))
        mock = MagicMock(return_value=s)
        args = Namespace(settings=mock)
        set_args(args, ())
        self.assertEqual(args.settings, s)
        mock.close.assert_called_with()

class TestCheckOutputFormat(TestCase):
    def testError(self):
        tests = [
            ('test', -1),
            ('test', 0),
            ('test', 2),
            ('test%d%d', 2)
        ]
        for test in tests:
            with self.assertRaises(ValueError):
                check_output_format(*test)

    def testNoError(self): # pylint: disable=no-self-use
        tests = [
            ('test', 1),
            ('test%d', 2)
        ]
        for test in tests:
            check_output_format(*test)


class TestInFiles(TestCase):
    @patch('markovchain.cli.util.tqdm')
    def testNoProgress(self, tqdm):
        tests = [
            ([], True),
            (list(range(3)), False)
        ]
        for test in tests:
            with infiles(*test) as it:
                self.assertFalse(tqdm.called)
                self.assertIs(it, test[0])

    @patch('markovchain.cli.util.tqdm')
    def testProgress(self, tqdm):
        test = list(range(3))
        with infiles(test, True) as pbar:
            self.assertTrue(tqdm.called)
            self.assertTrue((test,) in tqdm.call_args)
            self.assertIsInstance(pbar, Mock)
        pbar.close.assert_called_with()


class TestOutFiles(TestCase):
    def testError(self):
        tests = [
            ('', -1, False),
            ('', 0, False)
        ]
        for test in tests:
            with self.assertRaises(ValueError), outfiles(*test):
                pass

    @patch('markovchain.cli.util.tqdm')
    def testNoProgress(self, tqdm):
        tests = [
            (('', 1, False), ['']),
            (('%d', 2, False), ['0', '1'])
        ]
        for test, res in tests:
            with outfiles(*test) as it:
                it = list(it)
                self.assertFalse(tqdm.called)
                self.assertEqual(it, res)

    @patch('markovchain.cli.util.tqdm')
    def testProgress(self, tqdm):
        test = ('%d', 3, True)
        res = ['0', '1', '2']
        with outfiles(*test) as pbar:
            self.assertTrue(tqdm.called)
            self.assertEqual(list(tqdm.call_args[0][0]), res)
            self.assertIsInstance(pbar, Mock)
        pbar.close.assert_called_with()
