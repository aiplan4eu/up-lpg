# LPG Unified Planning integrator

![LPG Logo](https://github.com/aiplan4eu/up-lpg/blob/master/logoLPG.gif "LPG Logo")

The aim of this project is to make the [LPG](https://lpg.unibs.it)
planning engine available in the [unified_planning
library](https://github.com/aiplan4eu/unified-planning) by the
[AIPlan4EU project](https://www.aiplan4eu-project.eu/). LPG
is one of the most successful planning systems for classical, numerical and temporal planning.


## Installation

We recommend the installation from PyPi because it has pre-built wheels for all common operating systems.

### Installation from Python Package Index PyPi

To automatically get a version that works with your version of the unified planning framework, you can list it as a solver in the pip installation of ```unified_planning```:

```
pip install unified-planning[lpg]
```

If you need several solvers, you can list them all within the brackets.

You can also install the Fast Downward integration separately (in case the current version of unified_planning does not include Fast Downward or you want to add it later to your unified planning installation). After cloning this repository run
```pip install ./up-lpg```.
you get the latest version. 

This repository incudes the LPG binaries compiled for Linux and Windows. The installation has been tested in Ubuntu 20.04.3 LTS and Windows 10 version 22H2.

If you need an older version, you can install it with:

```
pip install up-lpg==<version number>
```


### Features:
- One shot planning
- Anytime planning
- Plan Repairer


##LPG Team

Current members: Alfonso E. Gerevini , Alessandro Saetti and Ivan Serina

Planning group coordinator: Alfonso E. Gerevini

Undergraduate students (now graduated) previously involved: Marco Lazzaroni, Stefano Orlandi, Valerio Lorini, Fabrizio Morbini, Sergio Spinoni, Alberto Bettini, Paolo Toninelli, Fabrizio Bonfadini, Mauro Vallati.

Programmer previouly involved: Maurizio Vitale (for InLPG)
 

