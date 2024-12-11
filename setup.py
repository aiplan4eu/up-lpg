#!/usr/bin/env python3
import platform
from setuptools import setup, find_packages , Distribution, Extension

long_description=\
"""============================================================
    UP_LPG
 ============================================================
"""
arch = (platform.system(), platform.machine())

EXECUTABLES = {
    ("Linux", "x86_64"): "lpg",
    ("Windows", "x86_64"): "winlpg.exe",
    ("Windows", "AMD64"): "winlpg.exe",
}

executable = EXECUTABLES[arch]

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

except ImportError:
    bdist_wheel = None


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self):
        return True

    def is_pure(self):
        return False

setup(name='up_lpg',
      version='0.0.8',
      description='up_lpg',
      long_description=long_description,
      long_description_content_type ="text/markdown",
      author='UNIBS Team',
      author_email="ivan.serina@unibs.it",
      packages=["up_lpg"],
      package_data={"up_lpg": [executable]},
      distclass=BinaryDistribution,
      include_package_data=True,
      data_files=[('platlib', [f'up_lpg/{executable}'])],
      cmdclass={'bdist_wheel': bdist_wheel},
      license='APACHE')
