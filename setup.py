#!/usr/bin/env python

from setuptools import setup

long_description = """
=======
SEGYVIEWER
=======

Segyviewer is a small LGPL licensed python library for easy viewing of SEG-Y
files. It uses the segyio library for reading files.


"""

version = {}
with open('src/segyviewlib/version.py') as f:
    exec(f.read(), version)

setup(name='segyviewlib',
      version=version['__version__'],
      description='Simple viewer for SEG-Y files',
      long_description=long_description,
      author='Statoil ASA',
      author_email='ert@statoil.com',
      url='https://github.com/Statoil/segyviewer',
      packages=['segyviewlib'],
      package_dir={'segyviewlib': 'src/segyviewlib'},
      package_data={'':
                        ['LICENSE',
                         'README.md',
                         'resources/img/350px-SEGYIO.png',
                         'resources/img/cog.png',
                         'resources/img/layouts_four_grid.png',
                         'resources/img/layouts_three_bottom_grid.png',
                         'resources/img/layouts_three_left_grid.png',
                         'resources/img/layouts_three_top_grid.png',
                         'resources/img/layouts_two_horizontal_grid.png',
                         'resources/img/folder.png',
                         'resources/img/layouts_single.png',
                         'resources/img/layouts_three_horizontal_grid.png',
                         'resources/img/layouts_three_right_grid.png',
                         'resources/img/layouts_three_vertical_grid.png',
                         'resources/img/layouts_two_vertical_grid.png',
                         'resources/img/table_export.png',
                         'resources/img/readme.txt'
                         ]},
      scripts=['applications/segyviewer', 'applications/segyviewer'],
      license='LGPL-3.0',
      platforms='any',
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      requires=['segyio', 'matplotlib'],
      install_requires=['segyio', 'matplotlib'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities'
      ]
      )
