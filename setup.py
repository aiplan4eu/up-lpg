#!/usr/bin/env python3

from setuptools import setup

long_description=\
"""============================================================
    UP_LPG
 ============================================================
"""
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark us as not a pure python package
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            # We don't link with python ABI, but require python3
            python, abi = 'py3', 'none'
            return python, abi, plat
except ImportError:
    bdist_wheel = None


setup(name='up_lpg',
      version='0.0.2',
      description='up_lpg',
      author='UNIBS Team',
      author_email='enrico.scala@unibs.it',
      packages=['up_lpg'],
      package_data={
          "": ["lpg"],
      },
      cmdclass={
          'bdist_wheel': bdist_wheel,
      },
      license='APACHE')
