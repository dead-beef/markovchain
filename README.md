# markovchain

## Overview

Markov chain generator

## Requirements

- [`Python 3`](https://www.python.org/)

## Installation

```
python setup.py install
```

```
pip install -e .[image]
```

## Testing

```
python setup.py test
```

## Usage

```
usage: markovchain [-h] {text,image} ...

positional arguments:
  {text,image}

optional arguments:
  -h, --help    show this help message and exit
```

### Text

```
usage: markovchain text [-h] {create,update,settings,generate} ...

positional arguments:
  {create,update,settings,generate}

optional arguments:
  -h, --help            show this help message and exit
```

#### create

```
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
usage: markovchain text settings [-h] state

positional arguments:
  state       state file

optional arguments:
  -h, --help  show this help message and exit
```

### Image

```
usage: markovchain image [-h]
                         {convert,create,update,settings,generate,filter} ...

positional arguments:
  {convert,create,update,settings,generate,filter}

optional arguments:
  -h, --help            show this help message and exit

```

#### convert

```
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
usage: markovchain image settings [-h] state

positional arguments:
  state       state file

optional arguments:
  -h, --help  show this help message and exit
```

## Licenses

* [`markovchain`](LICENSE)
