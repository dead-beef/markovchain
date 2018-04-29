markovchain
===========

.. image:: https://img.shields.io/pypi/v/markovchain.svg
   :target: https://pypi.python.org/pypi/markovchain
.. image:: https://img.shields.io/pypi/status/markovchain.svg
   :target: https://pypi.python.org/pypi/markovchain
.. image:: https://img.shields.io/pypi/format/markovchain.svg
   :target: https://pypi.python.org/pypi/markovchain
.. image:: https://img.shields.io/librariesio/github/dead-beef/markovchain.svg
   :target: https://libraries.io/pypi/markovchain
.. image:: https://img.shields.io/pypi/pyversions/markovchain.svg
   :target: https://python.org
.. image:: https://img.shields.io/pypi/l/markovchain.svg
   :target: https://github.com/dead-beef/markovchain/blob/master/LICENSE

Overview
--------

Markov chain generator

Requirements
------------

-  `Python 3 <https://www.python.org/>`__

Installation
------------

.. code:: bash

    pip install markovchain

.. code:: bash

    pip install markovchain[image]

.. code:: bash

    git clone https://github.com/dead-beef/markovchain
    cd markovchain
    pip install -e .[dev]

Building
--------

.. code:: bash

    ./build.sh

Testing
-------

.. code:: bash

    ./test

Module usage
------------

-  `Module documentation <https://dead-beef.github.io/markovchain/>`__

Examples
~~~~~~~~

Text
^^^^

.. code:: python

    from markovchain import JsonStorage
    from markovchain.text import MarkovText, ReplyMode

    markov = MarkovText()

    with open('data.txt') as fp:
        markov.data(fp.read())

    with open('data2.txt') as fp:
        for line in fp:
            markov.data(line, part=True)
    markov.data('', part=False)

    print(markov())
    print(markov(max_length=16, reply_to='sentence start', reply_mode=ReplyMode.END))

    markov.save('markov.json')

    markov = MarkovText.from_file('markov.json')

Image
^^^^^

.. code:: python

    from PIL import Image
    from markovchain import JsonStorage
    from markovchain.image import MarkovImage

    markov = MarkovImage()

    markov.data(Image.open('input.png'))

    width = 32
    height = 16
    img = markov(width, height)
    with open('output.png', 'wb') as fp:
        img.save(fp)

    markov.save('markov.json')

    markov = MarkovImage.from_file('markov.json')

CLI usage
---------

::

    > markovchain -h
    usage: markovchain [-h] [-v] {text,image} ...

    positional arguments:
      {text,image}

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit

Data types
~~~~~~~~~~

+----------------+-------------------------+---------------------+
| File name      | File type               | Storage class       |
+================+=========================+=====================+
| None (stdout)  | JSON                    | JsonStorage         |
+----------------+-------------------------+---------------------+
| \*.json        | JSON                    | JsonStorage         |
+----------------+-------------------------+---------------------+
| \*.json.bz2    | bzip2 compressed JSON   | JsonStorage         |
+----------------+-------------------------+---------------------+
| Other          | SQLite 3 database       | SqliteStorage       |
+----------------+-------------------------+---------------------+

Examples
~~~~~~~~

Text
^^^^

.. code:: bash

    markovchain text create --output text.db input1.txt input2.txt
    markovchain text update text.db input3.txt input4.txt
    markovchain text generate text.db
    markovchain text generate --count 16 --start 'sentence start' text.db

Image
^^^^^

.. code:: bash

    markovchain image create --progress --output img.db img1.png img2.png
    markovchain image update --progress img.db img3.png img4.png
    markovchain image generate --progress --size 64 64 --count 4 img.db img%02d.png
    markovchain image filter --progress img.png output.png

Settings
^^^^^^^^

-  `Text <https://github.com/dead-beef/markovchain/tree/master/settings/text>`__
-  `Image <https://github.com/dead-beef/markovchain/tree/master/settings/image>`__

Text
~~~~

::

    > markovchain text -h
    usage: markovchain text [-h] {create,update,settings,generate} ...

    positional arguments:
      {create,update,settings,generate}

    optional arguments:
      -h, --help            show this help message and exit

create
^^^^^^

::

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

update
^^^^^^

::

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

generate
^^^^^^^^

::

    > markovchain text generate -h
    usage: markovchain text generate [-h] [-P] [-nf]
                                     [-s SETTINGS] [-ss STATE_SIZE]
                                     [-S START] [-E END] [-R REPLY]
                                     [-w WORDS] [-c COUNT] [-o OUTPUT]
                                     state

    positional arguments:
      state                 state file

    optional arguments:
      -h, --help            show this help message and exit
      -P, --progress        show progress bar
      -nf, --no-format      do not format text
      -s SETTINGS, --settings SETTINGS
                            settings json file
      -ss STATE_SIZE, --state-size STATE_SIZE
                            generator state size
      -S START, --start START
                            text start
      -E END, --end END     text end
      -R REPLY, --reply REPLY
                            reply to text
      -w WORDS, --words WORDS
                            max text size (default: 256)
      -c COUNT, --count COUNT
                            number of generated texts (default: 1)
      -o OUTPUT, --output OUTPUT
                        output file (default: stdout)

settings
^^^^^^^^

::

    > markovchain text settings -h
    usage: markovchain text settings [-h] state

    positional arguments:
      state       state file

    optional arguments:
      -h, --help  show this help message and exit

Image
~~~~~

::

    > markovchain image -h
    usage: markovchain image [-h]
                             {create,update,settings,generate,filter} ...

    positional arguments:
      {create,update,settings,generate,filter}

    optional arguments:
      -h, --help            show this help message and exit

create
^^^^^^

::

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

update
^^^^^^

::

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

generate
^^^^^^^^

::

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

filter
^^^^^^

::

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

settings
^^^^^^^^

::

    > markovchain image settings -h
    usage: markovchain image settings [-h] state

    positional arguments:
      state       state file

    optional arguments:
      -h, --help  show this help message and exit

Licenses
--------

-  `markovchain <https://github.com/dead-beef/markovchain/blob/master/LICENSE>`__

