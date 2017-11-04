# School Timetable Optimizer
Basic optimization problem to generate the timetable for students and teachers, under certain requirements and constraints, solved using [http://www.gurobi.com/](http://www.gurobi.com/), [Coin/CBC](https://projects.coin-or.org/Cbc) or [GLPK](https://www.gnu.org/software/glpk/).

For a more detailed explanation of the problem, please read the model file in the docs.

## Installation
You can either use the `model.py` or the `model_pulp.py` scripts. `model.py` uses [gurobipy](http://www.gurobi.com/documentation/7.5/quickstart_mac/the_gurobi_python_interfac.html) and `model_pulp.py` uses [PulP](https://www.coin-or.org/PuLP/) to model the problem.

The model using gurobipy is a lot faster, but requires you to have a license for gurobi and gurobi installed, and the model using PulP, allows you to switch between different solvers.

To install Gurobi and gurobipy, follow the instructions in [Gurobi's documentation](http://www.gurobi.com/documentation/7.5/) to install Gurobi, and then the [gurobipy's installation instructions](http://www.gurobi.com/documentation/7.5/quickstart_mac/the_gurobi_python_interfac.html).

To install PulP, simply run in the root of the project:
```
pip install -r requirements.txt
```

Then, inside the model, you can switch between different solvers on the `model.solve()` call. To check which solvers you can use with your current installation, open a python interface and run:

```
import pulp
pulp.pulpTestAll()
```

The solvers that you can use will be marked as enabled. For a deeper insight of the solvers that you can use with PulP, please, check [this section from the documentation](https://www.coin-or.org/PuLP/solvers.html).

PulP can use `PULP_CBC_CMD` out of the box, then, if you followed the Gurobi installation instructions, you should also be able to use `GUROBI_CMD`. 

Follow [this link](https://projects.coin-or.org/Cbc) to download and install `COIN/CBC`, if you're running in OSX, you might have some troubles to install this solvers using brew, to solve this create the following environment variables:

```
export PKG_CONFIG=/usr/local/bin/pkg-config
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/
```

## Usage

To know how to model using PulP, check [it's repo](https://github.com/coin-or/pulp), to model using gurobipy, read [gurobipy's docs](http://www.gurobi.com/documentation/7.5/quickstart_mac/the_gurobi_python_interfac.html).
