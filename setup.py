import os

from setuptools import find_packages, setup

setup(name='mbtest',
      zip_safe=False,
      version='0.1.0',
      description='Python wrapper & utils for the Mountebank over the wire test double tool.',
      long_description=open(
          os.path.join(
              os.path.dirname(__file__),
              'README.md'
          )
      ).read(),
      author='Simon Brunning',
      author_email='simon@brunningonline.net',
      url='https://github.com/brunns/mbtest/',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Utilities'],
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
      install_requires=[
          'requests',
          'furl',
          'attrs',
          'more_itertools',
          'pyhamcrest',
          'pytest',
      ],
      )
