from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any


def import_solution(path: Path) -> ModuleType:
    if not path.exists():
        raise FileNotFoundError(path)
    module_name = f"_qamomile_solution_{path.stem}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import solution from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


def load_solve(path: Path) -> Any:
    module = import_solution(path)
    solve = getattr(module, "solve", None)
    if solve is None:
        raise AttributeError("Solution module must define a top-level qamomile @qmc.qkernel named solve.")
    return solve
