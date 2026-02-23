# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Package initialization for automatic module discovery and symbol importing.

This module automatically imports all Python modules in the current directory
and exposes their public symbols through __all__. It enables a clean public API
by collecting symbols from submodules either through their __all__ definitions
or by gathering non-underscore names.

Directory Structure:
    package/
    ├── __init__.py (this file)
    ├── base.py (excluded from auto-import)
    ├── command1.py
    └── command2.py

Usage:
    # In module1.py
    class MyClass1: pass

    # In another file
    from package import MyClass1  # Automatically available
"""

import importlib
from pathlib import Path

# Get all .py files in current directory
modules = [
    f.stem
    for f in Path(__file__).parent.glob("*.py")
    if f.stem not in ["__init__", "base"]
]

# Import all modules and add their contents to __all__
__all__ = []
for module in modules:
    imported = importlib.import_module(f".{module}", __package__)
    if hasattr(imported, "__all__"):
        __all__.extend(imported.__all__)
    else:
        # If module doesn't define __all__, add all non-underscore names
        __all__.extend([name for name in dir(imported) if not name.startswith("_")])
