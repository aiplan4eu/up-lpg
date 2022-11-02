#!/usr/bin/env python3
import platform
from setuptools import setup

long_description=\
"""============================================================
    UP_LPG
 ============================================================
"""
arch = (platform.system(), platform.machine())

EXECUTABLES = {
    ("Linux", "x86_64"): "lpg.exe",
    # ("Windows", "x86_64"): "aries_windows_x86_64.exe",
    # ("Windows", "aarch64"): "aries_windows_aarch64.exe",
    # ("Windows", "x86"): "aries_windows_x86.exe",
    # ("Windows", "aarch32"): "aries_windows_aarch32.exe",
}

executable = EXECUTABLES[arch]


setup(name='up_lpg',
      version='0.0.2',
      description='up_lpg',
      author='UNIBS Team',
      author_email='enrico.scala@unibs.it',
      packages=['up_lpg'],
      package_data={"": [executable]},
      include_package_data=True,
    
      license='APACHE')
