from unittest import TestCase
from PIL import Image

from markovchain import Scanner
from markovchain.image import ImageScanner, HLines, VLines
from markovchain.image.util import palette as default_palette


class TestImageScanner(TestCase):
    @classmethod
    def setUpClass(cls):
        data = b'\x00\x00\x00\xaa\xaa\xaa\xdd\xdd\xdd\x44\x44\x44'
        palette = [
            0x00, 0x00, 0x00,
            0x44, 0x44, 0x44,
            0xaa, 0xaa, 0xaa,
            0xdd, 0xdd, 0xdd
        ]
        palette.extend(0 for _ in range((256 - len(palette)) * 3))
        cls.image = Image.frombytes('RGB', (2, 2), data, 'raw', 'RGB')
        cls.palette = palette

    def test_properties(self):
        scan = ImageScanner()

        self.assertEqual(scan.palette, default_palette(8, 4, 8))
        self.assertIsNotNone(scan.palette_image)
        self.assertIsNotNone(scan.levels)
        self.assertIsNotNone(scan.min_size)
        self.assertIsInstance(scan.level_scale, list)
        self.assertIsInstance(scan.traversal, list)
        self.assertEqual(len(scan.level_scale), scan.levels - 1)
        self.assertEqual(len(scan.traversal), scan.levels)

        scan.palette = self.palette
        self.assertIsNotNone(scan.palette)
        self.assertIsNotNone(scan.palette_image)

        with self.assertRaises(ValueError):
            scan.levels = 0
        scan.levels = 3
        self.assertEqual(len(scan.traversal), scan.levels)

        with self.assertRaises(ValueError):
            scan.level_scale = []
        with self.assertRaises(ValueError):
            scan.level_scale = [1, -1]
        scan.level_scale = range(2, 10)
        self.assertEqual(scan.level_scale, [2, 3])
        self.assertEqual(scan.min_size, 6)
        scan.level_scale = 2
        self.assertEqual(scan.level_scale, [2, 2])
        self.assertEqual(scan.min_size, 4)
        scan.levels = 2
        self.assertEqual(len(scan.traversal), scan.levels)
        self.assertEqual(scan.level_scale, [2])
        self.assertEqual(scan.min_size, 2)
        scan.levels = 1
        self.assertEqual(len(scan.traversal), scan.levels)
        self.assertEqual(scan.level_scale, [])
        self.assertEqual(scan.min_size, 1)

        traversal = [HLines(), VLines()]
        scan.traversal = traversal
        scan.levels = 2
        self.assertIs(scan.traversal, traversal)
        self.assertEqual(scan.level_scale, [2])

    def test_input(self):
        tests = [(1, 1), (4, 1), (1, 4)]
        for test in tests:
            scan = ImageScanner(palette=self.palette, resize=test)
            img = scan.input(self.image)
            self.assertLessEqual(img.size, test)
            self.assertEqual(img.mode, 'RGB')
            img = [scan.level(img, level) for level in range(scan.levels)]
            self.assertEqual(len(img), 1)
            img = img[0]
            self.assertEqual(img.mode, 'P')
            self.assertEqual(img.size, (1, 1))
            self.assertIn(list(img.getdata()), [[0], [1]])

    def test_input_levels(self):
        scan = ImageScanner(palette=self.palette, levels=2, level_scale=2)

        img = scan.input(self.image)
        img = [scan.level(img, level) for level in range(scan.levels)]

        self.assertEqual(len(img), 2)

        self.assertEqual(img[0].mode, 'P')
        self.assertEqual(img[0].size, (1, 1))
        self.assertIn(list(img[0].getdata()), [[0], [1]])

        self.assertEqual(img[1].mode, 'P')
        self.assertEqual(img[1].size, (2, 2))
        self.assertEqual(list(img[1].getdata()), [0, 2, 3, 1])

        scan = ImageScanner(palette=self.palette, levels=3, level_scale=2)
        with self.assertRaises(ValueError):
            scan.input(self.image)

    def test_input_level_scale(self):
        img = Image.new(mode='RGB', size=(48, 48))
        scan = ImageScanner(palette=self.palette,
                            levels=4, level_scale=[2, 3, 4])

        img = scan.input(img)
        size = [scan.level(img, level).size for level in range(scan.levels)]

        self.assertEqual(size, [(2, 2), (4, 4), (12, 12), (48, 48)])

    def test_scan(self):
        scan = ImageScanner(palette=self.palette, traversal=HLines())
        self.assertEqual([list(level) for level in scan(self.image)],
                         [['00', '02', '03', '01', scan.END]])

    def test_scan_levels(self):
        scan = ImageScanner(palette=self.palette,
                            levels=2, level_scale=2,
                            traversal=[HLines(), VLines()])
        self.assertIn(
            [list(level) for level in scan(self.image)],
            [
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
                ],
            ]
        )

    def test_save_load(self):
        tests = [
            (),
            ((4, 4), 0, True, self.palette, 2, 2,
             Image.NEAREST, [HLines(), VLines()])
        ]
        for test in tests:
            scanner = ImageScanner(*test)
            saved = scanner.save()
            loaded = Scanner.load(saved)
            self.assertEqual(scanner, loaded)
