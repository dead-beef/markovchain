from ..util import SaveLoad, load


class Traversal(SaveLoad):
    classes = {}

    def __call__(self, width, height, ends=True):
        raise NotImplementedError()


class Lines(Traversal): # pylint: disable=abstract-method
    def __init__(self, reverse=0, line_sentences=False):
        super().__init__()
        self.reverse = reverse
        self.line_sentences = line_sentences

    def __eq__(self, t):
        return (self.reverse == t.reverse
                and self.line_sentences == t.line_sentences)

    def save(self):
        data = super().save()
        data['reverse'] = self.reverse
        data['line_sentences'] = self.line_sentences
        return data


class HLines(Lines):
    def __call__(self, width, height, ends=True):
        for y in range(height):
            if self.reverse > 0 and y % self.reverse == 0:
                xs = range(width - 1, -1, -1)
            else:
                xs = range(width)

            for x in xs:
                yield x, y

            if self.line_sentences and ends:
                yield None


class VLines(Lines):
    def __call__(self, width, height, ends=True):
        for x in range(width):
            if self.reverse > 0 and x % self.reverse == 0:
                ys = range(height - 1, -1, -1)
            else:
                ys = range(height)

            for y in ys:
                yield x, y

            if self.line_sentences and ends:
                yield None


class Spiral(Traversal):
        super().__init__()
        self.reverse = reverse

    def __eq__(self, t):
        return self.reverse == t.reverse

    def save(self):
        data = super().save()
        data['reverse'] = self.reverse
        return data

    @staticmethod
    def _rspiral(width, height):
        x0 = 0
        y0 = 0
        x1 = width - 1
        y1 = height - 1

        while x0 < x1 and y0 < y1:
            for x in range(x0, x1):
                yield x, y0
            for y in range(y0, y1):
                yield x1, y
            for x in range(x1, x0, -1):
                yield x, y1
            for y in range(y1, y0, -1):
                yield x0, y

            x0 += 1
            y0 += 1
            x1 -= 1
            y1 -= 1

        if x0 == x1:
            for y in range(y0, y1 + 1):
                yield x0, y
        elif y0 == y1:
            for x in range(x0, x1 + 1):
                yield x, y0

    @staticmethod
    def _spiral(width, height):
        if width == 1:
            for y in range(height - 1, -1, -1):
                yield 0, y
            return
        if height == 1:
            for x in range(width - 1, -1, -1):
                yield x, 0
            return

        if width <= height:
            x0 = width // 2
            if width % 2:
                for y in range(height - 1 - x0, x0 - 1, -1):
                    yield x0, y
            x0 -= 1
            y0 = x0
        else:
            y0 = height // 2
            if height % 2:
                for x in range(width - 1 - y0, y0 - 1, -1):
                    yield x, y0
            y0 -= 1
            x0 = y0

        while x0 >= 0:
            x1 = width - x0 - 1
            y1 = height - y0 - 1

            for y in range(y0 + 1, y1):
                yield x0, y
            for x in range(x0, x1):
                yield x, y1
            for y in range(y1, y0, -1):
                yield x1, y
            for x in range(x1, x0 - 1, -1):
                yield x, y0

            x0 -= 1
            y0 -= 1

    def __call__(self, width, height, ends=True): # pylint: disable=unused-argument
        if self.reverse:
            yield from self._rspiral(width, height)
        else:
            yield from self._spiral(width, height)


class Blocks(Traversal):
    def __init__(self,
                 block_size=(16, 16),
                 block_sentences=False,
                 traverse_image=None,
                 traverse_block=None):
        super().__init__()
        self.block_size = tuple(block_size)
        self.block_sentences = block_sentences
        self.traverse_image = load(traverse_image, Traversal, HLines)
        self.traverse_block = load(traverse_block, Traversal, HLines)

    def __call__(self, width, height, ends=True):
        block_width, block_height = self.block_size
        img_width = width // block_width
        img_height = height // block_height
        for xy in self.traverse_image(img_width, img_height, ends):
            if xy is None:
                yield None
                continue
            x, y = xy
            x, y = x * block_width, y * block_height
            for dx, dy in self.traverse_block(block_width, block_height, False):
                yield x + dx, y + dy
            if self.block_sentences and ends:
                yield None

    def save(self):
        data = super().save()
        data['block_size'] = list(self.block_size)
        data['block_sentences'] = self.block_sentences
        data['traverse_image'] = self.traverse_image.save()
        data['traverse_block'] = self.traverse_block.save()
        return data

    def __eq__(self, t):
        return (self.block_size == t.block_size
                and self.block_sentences == t.block_sentences
                and self.traverse_image == t.traverse_image
                and self.traverse_block == t.traverse_block)
