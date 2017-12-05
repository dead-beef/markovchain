#!/bin/sh

if [ -d env ]; then
    . env/bin/activate
fi

rm -rfv build/* dist/* docs/* docsrc/source/* \
    && make -C docsrc apidoc html \
    && python3 setup.py sdist bdist_wheel
