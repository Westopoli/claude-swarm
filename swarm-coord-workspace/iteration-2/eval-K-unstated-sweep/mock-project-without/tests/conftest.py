"""Pytest conftest — ensures the project root is on sys.path so
`from src.types import ...` works without an installed package.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
