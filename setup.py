#!/usr/bin/env python3
import platform
from setuptools import setup, find_packages , Distribution

long_description=\
"""============================================================
    UP_LPG
 ============================================================
"""
arch = (platform.system(), platform.machine())

EXECUTABLES = {
    ("Linux", "x86_64"): "lpg",
    # ("Windows", "x86_64"): "aries_windows_x86_64.exe",
    # ("Windows", "aarch64"): "aries_windows_aarch64.exe",
    # ("Windows", "x86"): "aries_windows_x86.exe",
    # ("Windows", "aarch32"): "aries_windows_aarch32.exe",
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
      version='0.0.2.19',
      description='up_lpg',
      author='UNIBS Team',
      author_email='enrico.scala@unibs.it',
      packages=["up_lpg"],
      package_data={"up_lpg": [executable]},
      distclass=BinaryDistribution,
      include_package_data=True,
      cmdclass={'bdist_wheel': bdist_wheel},
      license='APACHE')
