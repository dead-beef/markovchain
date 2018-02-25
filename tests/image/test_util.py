from collections import Counter
from itertools import islice
import pytest

from markovchain.image.util import palette


@pytest.mark.parametrize('test', [
    (8, 8, 5),
    (0, 4, 4),
    (4, 0, 4),
    (4, 4, 0),
    (8, -4, 8),
    (-8, 4, -8)
])
def test_palette_errors(test):
    with pytest.raises(ValueError):
        palette(*test)

@pytest.mark.parametrize('test', [
    (8, 4, 8),
    (2, 2, 2),
    (16, 1, 1)
])
def test_palette(test):
    res = palette(*test)
    assert len(res) == 768
    res = list(zip(islice(res, 0, None, 3),
                   islice(res, 1, None, 3),
                   islice(res, 2, None, 3)))
    counter = Counter(res)
    size = test[0] * test[1] * test[2]
    assert len(counter.items()) == min(256, size + 1)
    assert counter[(0, 0, 0)] == 256 - size

@pytest.mark.parametrize('test', [
    (1, 1, 1),
    (1, 1, 2),
    (1, 1, 256)
])
def test_palette_grayscale(test):
    res = palette(*test)
    assert len(res) == 768
    res = list(zip(islice(res, 0, None, 3),
                   islice(res, 1, None, 3),
                   islice(res, 2, None, 3)))
    assert all(r == g and g == b for r, g, b in res)
    counter = Counter(res)
    size = test[0] * test[1] * test[2]
    assert len(counter.items()) == size
    assert counter[(0, 0, 0)] == 256 - size + 1
    if size > 1:
        assert counter[(255, 255, 255)] == 1
