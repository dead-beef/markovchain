#!/usr/bin/env python3

import os
from setuptools import setup, find_packages


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(BASE_DIR, 'README.rst')) as fp:
        README = fp.read()
except IOError:
    README = ''

setup(name='markovchain',
      version='0.2.4',
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
      license='MIT',
      packages=find_packages(include=('markovchain*',)),
      entry_points={
          'console_scripts': ['markovchain=markovchain.cli:main'],
      },
      install_requires=['enum34', 'tqdm', 'custom_inherit'],
      extras_require={
          'image': ['pillow'],
          'dev': [
              'pillow',
              'pytest',
              'pytest-mock',
              'coverage',
              'sphinx',
              'sphinx_rtd_theme',
              'twine',
              'wheel'
          ]
      },
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False)
