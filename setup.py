#!/usr/bin/env python3

import os
from unittest import TestLoader
from setuptools import setup, find_packages

def tests():
    return TestLoader().discover('tests')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(BASE_DIR, 'README.rst')) as fp:
        README = fp.read()
except FileNotFoundError:
    README = ''

setup(name='markovchain',
      version='0.1.2',
      description='Markov chain generator',
      long_description=README,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing',
          'Topic :: Utilities'
      ],
      keywords='markov chain generator',
      url='https://github.com/dead-beef/markovchain',
      author='dead-beef',
      author_email='contact@dead-beef.tk',
      license='MIT',
      packages=find_packages(include=('markovchain*',)),
      entry_points={
          'console_scripts': ['markovchain=markovchain.cli:main'],
      },
      test_suite='setup.tests',
      install_requires=['tqdm', 'ijson'],
      extras_require={
          'image': ['pillow'],
          'dev': [
              'pillow',
              'coverage',
              'sphinx',
              'sphinx_rtd_theme'
          ]
      },
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False)
