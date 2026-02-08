# canary rest-api

A minimal rest api that hooks into the hpc-runner for the flash demo. Some very important notes are currently there is no long term state management or data storage, so the run test info will only persist until a page reload. Also the fetch requests all specify "localhost" and so the frontend must be modified if you wanted to deploy the frontend somewhere remote. This prototype also requires that you manually install the hpc runner module.


## Requirements

- **Python** 3.10 or newer  
- **uv** (https://github.com/astral-sh/uv)  
- POSIX shell for helper scripts
- installation of hpc-runner module in uv venv

## Quickstart Local

Clone and cd into the main directory

``` bash
git clone git@github.berkeley.edu:Chem-283/DOW-1-26.git
cd DOW-1-26
```

Next follow the installation procedure for the hpc-runner and be sure to build:

```bash

# From the project root (recommended for workspace aware commands)
# 1. Clean previous artifacts
scripts/clean.sh

# 2. Create or sync the uv environment for the subproject
uv --directory prototypes/hpc-runner sync

# 3. Install the package in editable mode for development
uv --directory prototypes/hpc-runner run python -m pip install -e .

# 4. Run tests inside the project environment
uv --directory prototypes/hpc-runner run python -m pytest

# 5. Invoke the runner using the module form
uv --directory prototypes/hpc-runner run python -m hpc_regression.runner configs/runners.yaml

# Or invoke the console script after installation
uv --directory prototypes/hpc-runner run hpc-runner configs/runners.yaml
```

```bash
# From inside the project directory prototypes/hpc-runner
cd prototypes/hpc-runner
# 1. Sync environment
uv sync

# 2. Install editable
uv run python -m pip install -e .

# 3. Run tests
uv run python -m pytest

# 4. Run the runner
uv run python -m hpc_regression.runner configs/runners.yaml

# From the project directory
uv sync
uv build

# Inspect wheel contents
unzip -l dist/*.whl | sed -n '1,200p'
```

Next you need to install the uv requirements as well as the build for the hpc_runner

```bash
cd ../basic_restapi
uv sync
source .venv/bin/activate
uv --directory ../hpc-runner pip install ../hpc-runner/dist/hpc_regression-0.1.0-py3-none-any.whl
```

Finally, run the development server and navigate to the link in your browser

``` bash
flask --app app run
# This will run a terminal process, navigate to http://localhost:5000 in a browser to use the demo
```


# Running in termianl sesshion

Remember to activate the python environment when rerunning the terminal session. also note that you may need to reinstall the hpc-regression module manually until we get a build/release system up and running for working CI/CD

``` bash
# from prototypes/basic_restapi
source .venv/bin/activate
flask --app app run --host localhost --port 5000
# This will run a terminal process, navigate to http://localhost:5000 in a browser to use the demo
```

## A note on the front end

I edited the front end in an extremely janky fashion, since it was compiled REACT js that i dont have the source code for. If you need to review the changes, go to `prototypes/basic_restapi/static/js/index.js` and review the `runMainTestRunner` function first to get an idea of what the fetch request is doing.
