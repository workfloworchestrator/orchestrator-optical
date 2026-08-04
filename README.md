# Workflow Orchestrator (WFO) Optical Module

## Project Overview

The WFO Optical Module is a Python module that can be installed as a dependency for
[WFO](https://workfloworchestrator.org) users that want to integrate with their optical equipment. This project is
built on top of [`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core).

## Installation

To use the models and services from this module, you will need to make some changes to your local implementation of the
WFO. Please follow the steps below to install the WFO Optical module, including some file edits:

1. `uv add orchestrator-extra-optical`
2. Generate a database migration for this module in your local `migrations` setup (e.g. via the orchestrator-core
shell commands). This package no longer ships a migrations module, so no module hook needs to be added.
3. Subclass some of the models given in this module that contain properties or methods that are not implemented.
> Tip: These are marked with `#FIXME` comments.


## Development

* Clone this repository
* On your local implementation of the WFO, run `uv add --editable /this/repo` (or `pip install -e /this/repo`).
