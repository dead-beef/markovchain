#!/bin/sh

rm -rfv build/* dist/* docs/* docsrc/source/* \
    && (sed -r 's/`([^`]+)`/\1/g' README.md \
        | pandoc -f markdown_github -t rst >README.rst) \
    && make -C docsrc apidoc html \
    && python3 setup.py sdist bdist_wheel
