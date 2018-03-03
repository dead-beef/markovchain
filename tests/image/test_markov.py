from unittest.mock import Mock
import pytest
from PIL import Image

from markovchain import Scanner, Parser, LevelParser
from markovchain.image import MarkovImage, ImageScanner, HLines, VLines


def test_markov_image_properties():
    markov = MarkovImage()
    assert isinstance(markov.scanner, ImageScanner)
    assert isinstance(markov.parser, LevelParser)
    assert markov.scanner.levels == markov.levels
    assert markov.parser.levels == markov.levels
    markov.levels = 3
    assert markov.scanner.levels == markov.levels
    assert markov.parser.levels == markov.levels
    with pytest.raises(ValueError):
        markov.levels = -1
    assert markov.scanner.levels == markov.levels
    assert markov.parser.levels == markov.levels
    assert markov.levels == 3

def test_markov_image_generate_error():
    markov = MarkovImage()
    with pytest.raises(KeyError):
        markov(2, 2)

@pytest.mark.parametrize('test,res', [
    ((2, 2), [0, 1, 2, 3]),
    ((4, 2), [0, 1, 2, 3, 0, 1, 2, 3])
])
def test_markov_image_generate(test, res):
    scanner = Scanner(lambda x: x)
    scanner.traversal = [HLines()]
    scanner.levels = 1
    scanner.level_scale = []
    markov = MarkovImage(
        scanner=scanner,
        parser=Parser()
    )
    markov.imgtype.convert = lambda x: [x]
    markov.data([['\x00', '\x01', '\x02', '\x03']])
    assert list(markov(*test).getdata()) == res

@pytest.mark.parametrize('args,kwargs,data,res', [
    ((2, 2), {}, False, KeyError),
    ((2, 2), {'levels': 0}, True, ValueError),
    ((2, 2), {'levels': 3}, True, ValueError),
    ((2, 2), {'levels': 1}, True, [0, 1, 2, 3]),
    (
        (2, 2),
        {},
        True,
        [
            0, 2, 1, 3,
            1, 3, 2, 0,
            2, 0, 3, 1,
            3, 1, 0, 2
        ]
    ),
    (
        (2, 1),
        {'levels': 1, 'start_level': -5, 'start_image': True},
        True,
        [0, 1]
    ),
    (
        (None, None),
        {'levels': 1, 'start_level': 0, 'start_image': True},
        True,
        [1, 3, 2, 0]
    ),
    (
        (None, None),
        {'levels': 1, 'start_level': 2, 'start_image': True},
        True,
        [1]
    ),
    (
        (None, None),
        {'levels': 2, 'start_level': 0, 'start_image': True},
        True,
        ValueError
    ),
])
def test_markov_image_generate_levels(args, kwargs, data, res):
    scanner = Scanner(lambda x: x)
    scanner.traversal = [HLines(), VLines()]
    scanner.levels = 2
    scanner.level_scale = [2]

    markov = MarkovImage(levels=2, scanner=scanner)
    markov.imgtype.convert = lambda x: [x]

    if data:
        markov.data([
            ['\x00', '\x01', '\x02', '\x03'],
            [(Scanner.START, '\x00'), '\x01',
             (Scanner.START, '\x01'), '\x02',
             (Scanner.START, '\x02'), '\x03',
             (Scanner.START, '\x03'), '\x00']
        ])

    if 'start_image' in kwargs:
        img = Image.new('P', (1, 1))
        img.putpixel((0, 0), 1)
        kwargs['start_image'] = img

    if isinstance(res, type):
        with pytest.raises(res):
            markov(*args, **kwargs)
    else:
        assert list(markov(*args, **kwargs).getdata()) == res

def test_markov_image_get_settings_json(mocker):
    get_settings_json = mocker.patch(
        'markovchain.Markov.get_settings_json',
        return_value={'x': 0}
    )
    markov = MarkovImage(
        levels=2,
        imgtype=Mock(save=lambda: 3)
    )
    data = markov.get_settings_json()
    assert data == {
        'x': 0,
        'levels': 2,
        'imgtype': 3
    }
    get_settings_json.assert_called_once_with()

@pytest.mark.parametrize('test,test2,res', [
    ((), (), True),
    ((1,), (2,), False),
    ((1, [8, 4, 8]), (1, [8, 4, 4]), False)
])
def test_markov_image_eq(test, test2, res):
    assert (MarkovImage(*test) == MarkovImage(*test2)) == res
