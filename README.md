# Workflow Orchestrator (WFO) Optical Module

## Project Overview

The WFO Optical Module is a Python module that can be installed as a dependency for
[WFO](https://workfloworchestrator.org) users that want to integrate with their optical equipment. This project is
built on top of [`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core).

## Installation

To use the models and services from this module, you will need to make some changes to your local implementation of the
WFO. Please follow the steps below to install the WFO Optical module, including some file edits:

1. `uv add orchestrator-extra-optical`
2. In your local `migrations.versions` module, add a database migration that depends on the latest revision in this
repo. An example file is given below.
3. In your local `migrations.env.py` import and add the following line after instantiating the Alembic `config`:

```python
add_optical_module_migrations(config)
```



## Development

* Clone this repository
* On your local implementation of the WFO, run `uv add --editable /this/repo` (or `pip install -e /this/repo`).
