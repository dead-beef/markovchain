# markovchain

## Overview

Markov chain generator

## Requirements

- [`Python 3`](https://www.python.org/)

## Installation

```
pip install markovchain
```

```
pip install markovchain[image]
```

```
git clone https://github.com/dead-beef/markovchain
cd markovchain
pip install -e .[dev]
```

## Building

```
./build.sh
```

## Testing

```
./test
```

## Module usage

- [`Module documentation`](https://dead-beef.github.io/markovchain/)

### Examples

#### Text

```python
from markovchain import MarkovBase, MarkovSqliteMixin

class Markov(MarkovSqliteMixin, MarkovBase):
    pass

markov = Markov(db='markov.db')

with open('data.txt') as fp:
    markov.data(fp.read())

with open('data2.txt') as fp:
    for line in fp:
        markov.data(line, True)
markov.data('', False)

words = markov.generate(16) # generator
print(*words)

words = markov.generate(16, start=['sentence', 'start'])
print(*words)

markov.save()

markov = Markov.load('markov.db')
```

#### Image

```python
from PIL import Image

from markovchain import MarkovBase, MarkovJsonMixin
from markovchain.image import MarkovImageMixin

class Markov(MarkovImageMixin, MarkovJsonMixin, MarkovBase):
    pass

markov = Markov()

markov.data(Image.open('data.png'))

width = 32
height = 16
img = markov.image(width, height) # PIL image
with open('generated.png', 'wb') as fp:
    img.save(fp)

with open('markov.json', 'w') as fp:
    markov.save(fp)

markov = Markov.load('markov.json')
```

## CLI usage

```
> markovchain -h
usage: markovchain [-h] {text,image} ...

positional arguments:
  {text,image}

optional arguments:
  -h, --help    show this help message and exit
```

### Data types

| State file  | File type             | Data mixin used   |
|-------------|-----------------------|-------------------|
| stdout      | JSON                  | MarkovJsonMixin   |
| \*.json     | JSON                  | MarkovJsonMixin   |
| \*.json.bz2 | bzip2 compressed JSON | MarkovJsonMixin   |
| Other       | SQLite 3 database     | MarkovSqliteMixin |

### Examples

#### Text

```bash
markovchain text create --output text.db input1.txt input2.txt
markovchain text update text.db input3.txt input4.txt
markovchain text generate text.db
markovchain text generate --sentences 16 --start 'sentence start' text.db
```

#### Image

```bash
markovchain image create --progress --output img.db img1.png img2.png
markovchain image update --progress img.db img3.png img4.png
markovchain image generate --progress --size 64 64 --count 4 img.db img%02d.png
markovchain image filter --progress img.png output.png
```

#### Settings

- [`Text`](https://github.com/dead-beef/markovchain/tree/master/settings/text)
- [`Image`](https://github.com/dead-beef/markovchain/tree/master/settings/image)

### Text

```
> markovchain text -h
usage: markovchain text [-h] {create,update,settings,generate} ...

positional arguments:
  {create,update,settings,generate}

optional arguments:
  -h, --help            show this help message and exit
```

#### create

```
> markovchain text create -h
usage: markovchain text create [-h] [-P] [-s SETTINGS] [-o OUTPUT]
                               [input [input ...]]

positional arguments:
  input                 input file (default: stdin)

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -o OUTPUT, --output OUTPUT
                        output file (default: stdout)
```

#### update

```
> markovchain text update -h
usage: markovchain text update [-h] [-P] [-s SETTINGS] [-o OUTPUT]
                               state [input [input ...]]

positional arguments:
  state                 state file
  input                 input file (default: stdin)

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -o OUTPUT, --output OUTPUT
                        output file (default: rewrite state file)
```

#### generate

```
> markovchain text generate -h
usage: markovchain text generate [-h] [-P] [-s SETTINGS] [-ss STATE_SIZE]
                                 [-st START] [-w WORDS] [-ws WORD_SEPARATOR]
                                 [-S SENTENCES] [-o OUTPUT]
                                 state

positional arguments:
  state                 state file

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -ss STATE_SIZE, --state-size STATE_SIZE
                        generator state size
  -st START, --start START
                        sentence start
  -w WORDS, --words WORDS
                        max sentence size (default: 256)
  -ws WORD_SEPARATOR, --word-separator WORD_SEPARATOR
                        output word separator (default: ' ')
  -S SENTENCES, --sentences SENTENCES
                        number of generated sentences (default: 1)
  -o OUTPUT, --output OUTPUT
                        output file (default: stdout)
```

#### settings

```
> markovchain text settings -h
usage: markovchain text settings [-h] state

positional arguments:
  state       state file

optional arguments:
  -h, --help  show this help message and exit
```

### Image

```
> markovchain image -h
usage: markovchain image [-h]
                         {convert,create,update,settings,generate,filter} ...

positional arguments:
  {convert,create,update,settings,generate,filter}

optional arguments:
  -h, --help            show this help message and exit
```

#### convert

```
> markovchain image convert -h
usage: markovchain image convert [-h] [-p HUES SATURATIONS VALUES] [-c {0,1}]
                                 [-d] [-r WIDTH HEIGHT]
                                 input [input ...]

positional arguments:
  input                 input file

optional arguments:
  -h, --help            show this help message and exit
  -p HUES SATURATIONS VALUES, --palette HUES SATURATIONS VALUES
                        palette color division (default: [8, 4, 8])
  -c {0,1}, --convert-type {0,1}
                        conversion type (default: 1)
  -d, --dither          enable dithering
  -r WIDTH HEIGHT, --resize WIDTH HEIGHT
                        resize images (default: None)
```

#### create

```
> markovchain image create -h
usage: markovchain image create [-h] [-P] [-s SETTINGS] [-o OUTPUT]
                                [input [input ...]]

positional arguments:
  input                 input file

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -o OUTPUT, --output OUTPUT
                        output file (default: stdout)
```

#### update

```
> markovchain image update -h
usage: markovchain image update [-h] [-P] [-s SETTINGS] [-o OUTPUT]
                                state [input [input ...]]

positional arguments:
  state                 state file
  input                 input file

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -o OUTPUT, --output OUTPUT
                        output file (default: rewrite state file)
```

#### generate

```
> markovchain image generate -h
usage: markovchain image generate [-h] [-P] [-s SETTINGS]
                                  [-ss STATE_SIZE [STATE_SIZE ...]]
                                  [-S WIDTH HEIGHT] [-l LEVEL] [-c COUNT]
                                  state output

positional arguments:
  state                 state file
  output                output file name format string

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -ss STATE_SIZE [STATE_SIZE ...], --state-size STATE_SIZE [STATE_SIZE ...]
                        generator state sizes
  -S WIDTH HEIGHT, --size WIDTH HEIGHT
                        image size (default: <scanner.resize>)
  -l LEVEL, --level LEVEL
                        image levels (default: <scanner.levels>)
  -c COUNT, --count COUNT
                        generated image count (default: 1)
```

#### filter

```
> markovchain image filter -h
usage: markovchain image filter [-h] [-P] [-t {json,sqlite}] [-s SETTINGS]
                                [-S STATE] [-ss STATE_SIZE [STATE_SIZE ...]]
                                [-l LEVEL] [-c COUNT]
                                input output

positional arguments:
  input                 input image
  output                output file name format string

optional arguments:
  -h, --help            show this help message and exit
  -P, --progress        show progress bar
  -t {json,sqlite}, --type {json,sqlite}
                        generator type (default: json)
  -s SETTINGS, --settings SETTINGS
                        settings json file
  -S STATE, --state STATE
                        state file
  -ss STATE_SIZE [STATE_SIZE ...], --state-size STATE_SIZE [STATE_SIZE ...]
                        generator state sizes
  -l LEVEL, --level LEVEL
                        filter start level (default: 1)
  -c COUNT, --count COUNT
                        generated image count (default: 1)
```

#### settings

```
> markovchain image settings -h
usage: markovchain image settings [-h] state

positional arguments:
  state       state file

optional arguments:
  -h, --help  show this help message and exit
```

## Licenses

* [`markovchain`](https://github.com/dead-beef/markovchain/blob/master/LICENSE)
