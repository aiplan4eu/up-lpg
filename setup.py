#!/usr/bin/env python3

from setuptools import setup

long_description=\
"""============================================================
    UP_LPG
 ============================================================
"""

setup(name='up_lpg',
      version='0.0.1',
      description='up_lpg',
      author='UNIBS Team',
      author_email='enrico.scala@unibs.it',
      packages=['up_lpg'],
      package_data={
          "": ["lpg"],
      },
      license='APACHE')
