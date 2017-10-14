from unittest import TestCase
from PIL import Image

from markovchain import MarkovBase, MarkovJsonMixin, Scanner, Parser
from markovchain.image import MarkovImageMixin, HLines, VLines


class TestMarkovImage(TestCase):
    class Markov(MarkovImageMixin, MarkovJsonMixin, MarkovBase):
        pass

    @classmethod
    def setUpClass(cls):
        palette = [
            0x00, 0x00, 0x00,
            0x44, 0x44, 0x44,
            0xaa, 0xaa, 0xaa,
            0xdd, 0xdd, 0xdd
        ]
        palette.extend(0 for _ in range((256 - len(palette)) * 3))
        cls.palette = palette

    def test_properties(self):
        m = self.Markov()
        self.assertEqual(m.scanner.levels, m.levels)
        self.assertEqual(m.parser.levels, m.levels)
        m.levels = 3
        self.assertEqual(m.scanner.levels, m.levels)
        self.assertEqual(m.parser.levels, m.levels)
        with self.assertRaises(ValueError):
            m.levels = -1
        self.assertEqual(m.scanner.levels, m.levels)
        self.assertEqual(m.parser.levels, m.levels)
        self.assertEqual(m.levels, 3)

    def test_generate(self):
        scanner = Scanner(lambda x: x)
        scanner.traversal = [HLines()]
        scanner.levels = 1
        scanner.level_scale = []

        m = self.Markov(palette=self.palette, scanner=scanner, parser=Parser())

        with self.assertRaises(RuntimeError):
            m.image(2, 2)

        m.data([['00', '01', '02', '03']])

        data = list(m.image(2, 2).getdata())
        self.assertEqual(data, [0, 1, 2, 3])

        data = list(m.image(4, 2).getdata())
        self.assertEqual(data, [0, 1, 2, 3, 0, 1, 2, 3])

    def test_generate_levels(self):
        scanner = Scanner(lambda x: x)
        scanner.traversal = [HLines(), VLines()]
        scanner.levels = 2
        scanner.level_scale = [2]
        scanner.set_palette = lambda img: img

        m = self.Markov(levels=2, palette=self.palette, scanner=scanner)

        with self.assertRaises(RuntimeError):
            m.image(2, 2)

        m.data([
            ['00', '01', '02', '03',],
            [(Scanner.START, '0000'), '0101',
             (Scanner.START, '0001'), '0102',
             (Scanner.START, '0002'), '0103',
             (Scanner.START, '0003'), '0100',]
        ])

        data = list(m.image(2, 2, levels=1).getdata()) # pylint: disable=no-member
        self.assertEqual(data, [0, 1, 2, 3])

        data = list(m.image(2, 2, levels=2).getdata()) # pylint: disable=no-member
        self.assertEqual(
            data,
            [
                0, 1, 1, 2,
                1, 1, 2, 2,
                2, 3, 3, 0,
                3, 3, 0, 0
            ]
        )

        with self.assertRaises(ValueError):
            m.image(2, 2, levels=3)
        with self.assertRaises(ValueError):
            m.image(2, 2, levels=0)

        img = Image.new('P', (1, 1))
        img.putpalette(self.palette)
        img.putpixel((0, 0), 1)

        data = list(m.image(
            2, 1, levels=1,
            start_level=-5, start_image=img
        ).getdata()) # pylint: disable=no-member
        self.assertEqual(data, [0, 1])

        data = list(m.image(
            None, None, levels=1,
            start_level=0, start_image=img
        ).getdata()) # pylint: disable=no-member
        self.assertEqual(data, [1])

        data = list(m.image(
            None, None, levels=1,
            start_level=2, start_image=img
        ).getdata()) # pylint: disable=no-member
        self.assertEqual(data, [1])

        data = list(m.image(
            None, None, levels=2,
            start_level=0, start_image=img
        ).getdata()) # pylint: disable=no-member
        self.assertEqual(data, [1, 2, 2, 2])

    def test_save_load(self):
        m = self.Markov()
        saved = m.get_save_data()
        loaded = self.Markov(**saved)
        self.assertEqual(m, loaded)
