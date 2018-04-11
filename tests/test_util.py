import pytest
from enum import IntEnum

from markovchain.util import (
    SaveLoad, ObjectWrapper, const,
    fill, load, extend, to_list, truncate,
    state_size_dataset, level_dataset, int_enum
)


@pytest.fixture
def save_load_test():
    class SaveLoadTest(SaveLoad):
        classes = {}

        def __init__(self, value):
            self.value = value

        def __eq__(self, test):
            return self.value == test.value

        def save(self):
            data = super().save()
            data['value'] = self.value
            return data
    SaveLoadTest.add_class(SaveLoadTest)
    return SaveLoadTest


def test_saveload_add_remove_class(save_load_test):
    assert save_load_test.classes['SaveLoadTest'] is save_load_test
    save_load_test.remove_class(save_load_test)
    save_load_test.remove_class(save_load_test)
    with pytest.raises(KeyError):
        save_load_test.classes['SaveLoadTest']

def test_saveload_save_load(save_load_test):
    test = save_load_test(0)
    saved = test.save()
    loaded = save_load_test.load(saved)
    assert isinstance(loaded, save_load_test)
    assert loaded == test


class ObjectTest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def method(self):
        return self.x + self.y
    def method2(self):
        return self.x - self.y

class ObjectWrapperTest(ObjectWrapper):
    def __init__(self, obj, z):
        super().__init__(obj)
        self.y *= 2
        self.z = z
    def method(self):
        return super().method() + self.z

def test_object_wrapper_wrap():
    obj = ObjectTest(1, 2)
    wrapped = ObjectWrapper(obj)
    assert isinstance(wrapped, ObjectTest)
    assert wrapped.__dict__ == obj.__dict__
    assert wrapped.method() == 3
    assert wrapped.method2() == -1

def test_object_wrapper_override():
    obj = ObjectTest(1, 2)
    wrapped = ObjectWrapperTest(obj, 3)
    assert wrapped.x == 1
    assert wrapped.y == 4
    assert wrapped.z == 3
    assert wrapped.method() == 8
    assert wrapped.method2() == -3


class IntEnumTest(IntEnum):
    X = 0
    Y = 1

@pytest.mark.parametrize('test,res', [
    (0, 0),
    ('Y', 1),
    ('y', 1),
    ('z', ValueError),
    (2, ValueError)
])
def test_int_enum(test, res):
    if isinstance(res, type):
        with pytest.raises(res):
            int_enum(IntEnumTest, test)
    else:
        test = int_enum(IntEnumTest, test)
        assert isinstance(test, IntEnumTest)
        assert test == res


def test_const():
    assert const(0)() == 0
    assert const(1)(1, [2], key=3) == 1


@pytest.mark.parametrize('test,res', [
    ([], []),
    (range(3), list(range(3))),
    (0, [0]),
    ({'x': 0}, [{'x': 0}])
])
def test_to_list(test, res):
    assert to_list(test) == res


def test_fill_error():
    with pytest.raises(ValueError):
        fill([], 1)

@pytest.mark.parametrize('test,res', [
    ((None, -1), []),
    (([], 0), []),
    ((0, 0), []),
    ((1, 1), [1]),
    ((1, 5), [1] * 5),
    ((range(10), 2), [0, 1]),
    ((range(3), 5), [0, 1, 2, 2, 2])
])
def test_fill(test, res):
    assert fill(*test) == res

@pytest.mark.parametrize('lst,size', [
    ([], 0),
    (list(range(3)), 3)
])
def test_fill_no_copy(lst, size):
    assert fill(lst, size) is lst

@pytest.mark.parametrize('lst,size', [
    ([[0], [1]], 4)
])
def test_fill_copy(lst, size):
    res = fill(lst, size, copy=False)
    assert res[-1] is lst[-1]
    res = fill(lst, size, copy=True)
    assert res[-1] is not lst[-1]
    assert res[-1] == lst[-1]


class LoadTest:
    @staticmethod
    def load(data):
        return data['x']

def test_load_efault():
    x = load(None, LoadTest, lambda: 0)
    assert x == 0

def test_load_class():
    x = load({'x': 1}, LoadTest, lambda: 0)
    assert x == 1

def test_load_object():
    obj = object()
    x = load(obj, LoadTest, lambda: 0)
    assert x is obj


@pytest.mark.parametrize('test,res', [
    (({'x': 0}, {'y': 1}), {'x': 0, 'y': 1}),
    (({'x': 0}, {'y': 1}, {'x': 1}), {'x': 1, 'y': 1}),
    (({'x': {'y': 0}}, {'x': {'z': 1}}), {'x': {'y': 0, 'z': 1}}),
    (({'x': {'y': 0}}, {'x': 1}), {'x': 1}),
    (({'x': 1}, {'x': {'y': 0}}), {'x': {'y': 0}}),
    (({}, {'x': {'y': 0}}), {'x': {'y': 0}})
])
def test_extend(test, res):
    assert extend(*test) == res


@pytest.mark.parametrize('test', [
    ('', 3, True),
    ('0', -1, False)
])
def test_truncate_error(test):
    with pytest.raises(ValueError):
        truncate(*test)

@pytest.mark.parametrize('test', [
    ('0', 4, True),
    ('1234', 4, False)
])
def test_truncate_noop(test):
    assert truncate(*test) is test[0]

@pytest.mark.parametrize('test,res', [
    (('1234567', 5), '12...'),
    (('1234567', 5, True), '12...'),
    (('1234567', 5, False), '...67')
])
def test_truncate(test, res):
    assert truncate(*test) == res


@pytest.mark.parametrize('test', range(5))
def test_state_size_dataset(test):
    res = state_size_dataset(test)
    assert isinstance(res, str)
    assert len(res) > 0
    assert res != state_size_dataset(test - 1)

@pytest.mark.parametrize('test', range(5))
def test_level_dataset(test):
    res = level_dataset(test)
    assert isinstance(res, str)
    assert len(res) > 0
    assert res != level_dataset(test - 1)
    assert res != state_size_dataset(test)
