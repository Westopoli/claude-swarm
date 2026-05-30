import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Ensure leaf impl modules are imported so their monkey-patches against
# url_utils.types apply before any test resolves `from url_utils.types import ...`.
# Guarded — missing leaves are fine (they may not be admitted yet).
try:
    import url_utils.parse_url  # noqa: F401
except Exception:
    pass
try:
    import url_utils.is_safe_url  # noqa: F401
except Exception:
    pass
