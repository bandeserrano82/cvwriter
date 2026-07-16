#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


PLUGIN_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "plugins"
    / "cvwriter"
    / "scripts"
    / "validate_cv_workspace.py"
)


if __name__ == "__main__":
    runpy.run_path(str(PLUGIN_SCRIPT), run_name="__main__")
