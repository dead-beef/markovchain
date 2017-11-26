#!/bin/sh

rm -rfv build/* dist/* docs/* docsrc/source/* \
    && make -C docsrc apidoc html \
    && python3 setup.py sdist bdist_wheel
