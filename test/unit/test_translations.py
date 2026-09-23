"""Tests for the shipped workflow translations (``translations/en-GB.json``).

Schema of the translations file: it is **not** a flat ``{workflow_name: display_string}``
mapping. It is a JSON object with two top-level keys:

* ``"forms"``: form-layer display strings, unrelated to the shipped workflow names.
* ``"workflow"``: a nested object mapping each shipped workflow or task name to its
  human-readable display string.

The 1:1 relationship therefore holds between the keys of the ``"workflow"`` sub-object
and the shipped names reported by ``discover_shipped_workflows()`` plus
``discover_shipped_tasks()`` (the migration generator's discovery, which itself reads
display strings from this same file). This test locks that relationship so the file
cannot silently gain or lose an entry.
"""

import json
from importlib import resources

from orchestrator.optical.migrations.generate import discover_shipped_tasks, discover_shipped_workflows

_TRANSLATIONS_PATH = resources.files("orchestrator.optical") / "translations" / "en-GB.json"


def _load_translations() -> dict:
    """Load the shipped ``en-GB.json`` from the installed ``orchestrator.optical`` package."""
    return json.loads(_TRANSLATIONS_PATH.read_text(encoding="utf-8"))


def test_workflow_translations_cover_exactly_the_shipped_workflows() -> None:
    """The ``workflow`` translations map exactly the shipped workflow and task names, all with a value."""
    translations = _load_translations()
    workflow_translations = translations["workflow"]

    discovered_names = {workflow.name for workflow in discover_shipped_workflows()}
    discovered_names |= {task.name for task in discover_shipped_tasks()}

    assert set(workflow_translations) == discovered_names
    assert all(isinstance(display, str) and display for display in workflow_translations.values())
