# LPG Unified Planning integrator

## Installation

After cloning this repository run ```pip install up-lpg/```.

This repository incudes the LPG binaries compiled for Linux. The installation has been tested in Ubuntu 20.04.3 LTS.

### Features:
- One shot planning


## Unified Planning Integration
At the moment the integration with the Unified Planning Framework is obtained through manually adding to the environment factory of the unified planning framework the class implemented by this integrator. 
For example the following piece of code is to be invoked before any use of the LPG planner.

```
from unified_planning.environment import get_env
env = get_env()
env.factory.add_solver('lpg', 'up_lpg', 'LPGsolver')
```
