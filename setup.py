from unittest import TestLoader
from setuptools import setup

def tests():
    return TestLoader().discover('test')

setup(name='markovchain',
      version='0.1',
      description='Markov chain generator',
      long_description='',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'License :: OSI Approved :: MIT License'
      ],
      keywords='markov chain generator',
      url='https://github.com/dead-beef/markovchain',
      author='dead-beef',
      author_email='contact@dead-beef.tk',
      license='MIT',
      packages=['markovchain'],
      entry_points={
          'console_scripts': ['markovchain=markovchain.cli:main'],
      },
      package_data={
          '': ['README.md', 'LICENSE'],
      },
      #test_loader='unittest:TestLoader',
      test_suite='setup.tests',
      install_requires=['tqdm', 'ijson'],
      extras_require={
          'image': ['pillow']
      },
      include_package_data=True,
      zip_safe=False)
