import io
import pytest


class MockCLI:
    class Exit(Exception):
        def __init__(self, status=0):
            super().__init__('Command exited with status %s' % status)
            self.status = status

    @classmethod
    def mock_exit(cls, status=0):
        raise cls.Exit(status)

    def __init__(self, tmpdir):
        self.dir = str(tmpdir)
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.exit = None

    def __call__(self, mocker):
        self.stdin = mocker.patch('sys.stdin', new_callable=io.StringIO)
        self.stdout = mocker.patch('sys.stdout', new_callable=io.StringIO)
        self.stderr = mocker.patch('sys.stderr', new_callable=io.StringIO)
        self.exit = mocker.patch('sys.exit', wraps=self.mock_exit)

    def run(self, cmd, *args, **kwargs):
        try:
            cmd(*args, **kwargs)
        except self.Exit:
            pass

    def reset(self):
        for fp in (self.stdin, self.stdout, self.stderr):
            fp.seek(0)
            fp.truncate()
        self.exit.reset_mock()

    def assert_output(self, stdout, stderr=None, exit_status=None):
        if stdout is not None:
            assert self.stdout.getvalue() == stdout
        if stderr is not None:
            assert self.stderr.getvalue() == stderr
        if exit_status is None:
            assert self.exit.call_count == 0
        else:
            self.exit.assert_called_once_with(exit_status)


@pytest.fixture
def mock_cli(tmpdir):
    return MockCLI(tmpdir)
