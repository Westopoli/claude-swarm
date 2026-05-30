---
leaf_id: leaf-01
target_file: src/url_utils/types.py
status: accepted
---

## Proposed change

Replace the stub body of `parse_url` in `src/url_utils/types.py` with a delegation to the implementation module written by leaf-01:

```diff
-def parse_url(url: str) -> ParsedUrl:
-    raise NotImplementedError("AC-1 — implemented by leaf-1")
+def parse_url(url: str) -> ParsedUrl:
+    from url_utils.parse_url import parse_url as _impl
+    return _impl(url)
```

## Why this is required

The umbrella test (`tests/umbrella.py`) imports `parse_url` directly from `url_utils.types`. Spec lines 9-19 require `parse_url` to be callable from that import path. `src/url_utils/types.py` is parent-owned (matches `src/**/types.py`), so leaf-01 cannot edit it directly; without this delegation, the umbrella stays RED on AC-1 even after the leaf is admitted.

## Fallback if rejected

Re-spawn leaf-01 with a revised brief that places the impl directly in `src/url_utils/types.py` after the parent removes the file from `parent_owned`.
