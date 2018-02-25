from itertools import product
import pytest

from markovchain.image.traversal import (
    Traversal, HLines, VLines, Spiral, Hilbert, Blocks
)


@pytest.mark.parametrize('args,test,res', [
    ((0,), (2, 3, False), [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]),
    ((0,), (2, 3, True), [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]),
    ((1,), (2, 3), [(1, 0), (0, 0), (1, 1), (0, 1), (1, 2), (0, 2)]),
    ((2,), (2, 3), [(1, 0), (0, 0), (0, 1), (1, 1), (1, 2), (0, 2)]),
    ((0, True), (2, 3, False),
     [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]),
    ((0, True), (2, 3, True),
     [(0, 0), (1, 0), None, (0, 1), (1, 1), None, (0, 2), (1, 2), None])
])
def test_hlines_traverse(args, test, res):
    assert list(HLines(*args)(*test)) == res

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((1, True), (1, True), True),
    ((0, False), (0, True), False),
    ((0, False), (1, False), False)
])
def test_hlines_eq(test, test2, res):
    assert (HLines(*test) == HLines(*test2)) == res

@pytest.mark.parametrize('test', [
    (0, False), (2, True)
])
def test_hlines_save_load(test):
    test = HLines(*test)
    saved = test.save()
    loaded = Traversal.load(saved)
    assert isinstance(loaded, HLines)
    assert test == loaded


@pytest.mark.parametrize('args,test,res', [
    ((0,), (2, 3, False), [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]),
    ((0,), (2, 3, True), [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]),
    ((1,), (2, 3), [(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]),
    ((2,), (2, 3), [(0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2)]),
    ((0, True), (2, 3, False),
     [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]),
    ((0, True), (2, 3, True),
     [(0, 0), (0, 1), (0, 2), None, (1, 0), (1, 1), (1, 2), None])
])
def test_vlines_traverse(args, test, res):
    assert list(VLines(*args)(*test)) == res

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((1, True), (1, True), True),
    ((0, False), (0, True), False),
    ((0, False), (1, False), False)
])
def test_vlines_eq(test, test2, res):
    assert (VLines(*test) == VLines(*test2)) == res

@pytest.mark.parametrize('test', [
    (0, False), (2, True)
])
def test_vlines_save_load(test):
    test = VLines(*test)
    saved = test.save()
    loaded = Traversal.load(saved)
    assert isinstance(loaded, VLines)
    assert test == loaded


@pytest.mark.parametrize('width,height', product(range(1, 7), range(1, 7)))
def test_spiral_traverse(width, height):
    test = Spiral()
    test.reverse = False
    res = list(test(width, height, False))
    assert sorted(res) == list(product(range(width), range(height)))
    test.reverse = True
    res2 = list(test(width, height, False))
    res.reverse()
    assert res2 == res

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((True,), (False,), False),
    ((True,), (True,), True)
])
def test_spiral_eq(test, test2, res):
    assert (Spiral(*test) == Spiral(*test2)) == res

@pytest.mark.parametrize('test', [
    (False,), (True,)
])
def test_spiral_save_load(test):
    test = Spiral(*test)
    saved = test.save()
    loaded = Traversal.load(saved)
    assert isinstance(loaded, Spiral)
    assert test == loaded


@pytest.mark.parametrize('width,height', product(range(1, 7), range(1, 7)))
def test_hilbert_traverse(width, height):
    test = Hilbert()
    res = list(test(width, height))
    assert sorted(res) == list(product(range(width), range(height)))

def test_hilbert_save_load():
    test = Hilbert()
    saved = test.save()
    loaded = Traversal.load(saved)
    assert isinstance(loaded, Hilbert)
    assert test == loaded


@pytest.mark.parametrize('test,res,res2', [
    (
        (4, 4, False),
        [(0, 0), (0, 1), (2, 0), (2, 1)],
        [(0, 0), (0, 1), (2, 0), (2, 1)]
    ),
    (
        (3, 3, True),
        [(0, 0), (0, 1), None],
        [(0, 0), (0, 1), None, None]
    ),
    (
        (4, 4, True),
        [(0, 0), (0, 1), None, (2, 0), (2, 1)],
        [(0, 0), (0, 1), None, None, (2, 0), (2, 1), None]
    )
])
def test_blocks_traverse(test, res, res2):
    def hline(width, height, ends): # pylint: disable=unused-argument
        for x in range(width):
            yield (x, 0)
            if ends and x == 0:
                yield None

    def vline(width, height, ends): # pylint: disable=unused-argument
        for y in range(height):
            yield (0, y)
            if ends:
                yield None

    traverse = Blocks(block_size=(2, 2),
                      block_sentences=False,
                      traverse_image=hline,
                      traverse_block=vline)
    assert list(traverse(*test)) == res
    traverse.block_sentences = True
    assert list(traverse(*test)) == res2

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    (((8, 8),), ((4, 4),), False),
    (((4, 4), True), ((4, 4), False), False),
    (((4, 4), True, 0), ((4, 4), True, 1), False),
    (((4, 4), True, 0, 0), ((4, 4), True, 0, 1), False)
])
def test_blocks_eq(test, test2, res):
    assert (Blocks(*test) == Blocks(*test2)) == res

@pytest.mark.parametrize('test', [
    ((8, 8), True,
     HLines(reverse=1, line_sentences=True),
     VLines(reverse=2, line_sentences=False))
])
def test_blocks_save_load(test):
    test = Blocks(*test)
    saved = test.save()
    loaded = Traversal.load(saved)
    assert isinstance(loaded, Blocks)
    assert test == loaded
