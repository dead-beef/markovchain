import pytest
from PIL import Image

from markovchain import Scanner
from markovchain.image import ImageScanner, HLines, VLines
from markovchain.image.util import palette as default_palette


@pytest.fixture
def image_test():
    data = b'\x00\x00\x00\xaa\xaa\xaa\xdd\xdd\xdd\x44\x44\x44'
    palette = [
        0x00, 0x00, 0x00,
        0x44, 0x44, 0x44,
        0xaa, 0xaa, 0xaa,
        0xdd, 0xdd, 0xdd
    ]
    palette.extend(0 for _ in range((256 - len(palette)) * 3))
    image = Image.frombytes('RGB', (2, 2), data, 'raw', 'RGB')
    return image, palette


def test_image_scanner_init():
    scan = ImageScanner()
    assert scan.palette == default_palette(8, 4, 8)
    assert isinstance(scan.palette_image, Image.Image)
    assert scan.levels is not None
    assert scan.min_size is not None
    assert isinstance(scan.level_scale, list)
    assert isinstance(scan.traversal, list)
    assert len(scan.level_scale) == scan.levels - 1
    assert len(scan.traversal) == scan.levels

def test_image_scanner_properties(image_test):
    _, palette = image_test
    scan = ImageScanner()

    scan.palette = palette

    assert scan.palette == palette
    assert isinstance(scan.palette_image, Image.Image)

    with pytest.raises(ValueError):
        scan.levels = 0
    scan.levels = 3
    assert len(scan.traversal) == scan.levels

    with pytest.raises(ValueError):
        scan.level_scale = []
    with pytest.raises(ValueError):
        scan.level_scale = [1, -1]
    scan.level_scale = range(2, 10)
    assert scan.level_scale == [2, 3]
    assert scan.min_size == 6
    scan.level_scale = 2
    assert scan.level_scale == [2, 2]
    assert scan.min_size == 4
    scan.levels = 2
    assert len(scan.traversal) == scan.levels
    assert scan.level_scale == [2]
    assert scan.min_size == 2
    scan.levels = 1
    assert len(scan.traversal) == scan.levels
    assert scan.level_scale == []
    assert scan.min_size == 1

    traversal = [HLines(), VLines()]
    scan.traversal = traversal
    scan.levels = 2
    assert scan.traversal is traversal
    assert scan.level_scale == [2]

@pytest.mark.parametrize('test', [
    (1, 1), (4, 1), (1, 4)
])
def test_image_scanner_input(test, image_test):
    image, palette = image_test
    scan = ImageScanner(palette=palette, resize=test)
    img = scan.input(image)
    assert img.size <= test
    assert img.mode == 'RGB'
    img = [scan.level(img, level) for level in range(scan.levels)]
    assert len(img) == 1
    img = img[0]
    assert img.mode == 'P'
    assert img.size == (1, 1)
    assert list(img.getdata()) in [[0], [1]]

def test_image_scanner_input_error(image_test):
    image, palette = image_test
    scan = ImageScanner(palette=palette, levels=3, level_scale=2)
    with pytest.raises(ValueError):
        scan.input(image)

def test_image_scanner_input_levels(image_test):
    image, palette = image_test
    scan = ImageScanner(palette=palette, levels=2, level_scale=2)

    img = scan.input(image)
    img = [scan.level(img, level) for level in range(scan.levels)]

    assert len(img) == 2

    assert img[0].mode == 'P'
    assert img[0].size == (1, 1)
    assert list(img[0].getdata()) in [[0], [1]]

    assert img[1].mode == 'P'
    assert img[1].size == (2, 2)
    assert list(img[1].getdata()) == [0, 2, 3, 1]

def test_image_scanner_input_level_scale(image_test):
    img = Image.new(mode='RGB', size=(48, 48))
    scan = ImageScanner(palette=image_test[1],
                        levels=4, level_scale=[2, 3, 4])
    img = scan.input(img)
    size = [scan.level(img, level).size for level in range(scan.levels)]
    assert size == [(2, 2), (4, 4), (12, 12), (48, 48)]

def test_image_scanner_scan(image_test):
    image, palette = image_test
    scan = ImageScanner(palette=palette, traversal=HLines())
    assert [list(level) for level in scan(image)] == [
        ['00', '02', '03', '01', scan.END]
    ]

def test_image_scanner_scan_levels(image_test):
    image, palette = image_test
    scan = ImageScanner(palette=palette,
                        levels=2, level_scale=2,
                        traversal=[HLines(), VLines()])
    assert [list(level) for level in scan(image)] in [
        [
            ['00', scan.END],
            [(scan.START, '0000'),
             '0100', '0103', '0102', '0101',
             scan.END]
        ],
        [
            ['01', scan.END],
            [(scan.START, '0001'),
             '0100', '0103', '0102', '0101',
             scan.END]
        ]
    ]

@pytest.mark.parametrize('test', [
    (),
    ((4, 4), 0, True, image_test()[1], 2, 2,
     Image.NEAREST, [HLines(), VLines()])
])
def test_image_scanner_save_load(test):
    scanner = ImageScanner(*test)
    saved = scanner.save()
    loaded = Scanner.load(saved)
    assert isinstance(loaded, ImageScanner)
    assert scanner == loaded
