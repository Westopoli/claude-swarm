---
leaf_id: leaf-02
target_file: src/url_utils/types.py
status: accepted
---

## Proposed change

Replace the stub body of `is_safe_url` in `src/url_utils/types.py` with a delegation to the implementation module written by leaf-02:

```diff
-def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
-    raise NotImplementedError("AC-2 — implemented by leaf-2")
+def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
+    from url_utils.is_safe_url import is_safe_url as _impl
+    return _impl(url, allowed_hosts)
```

## Why this is required

The umbrella test imports `is_safe_url` directly from `url_utils.types`. Spec lines 21-30 require `is_safe_url` to be callable from that import path. `src/url_utils/types.py` is parent-owned; leaf-02 cannot edit it directly.

## Fallback if rejected

Re-spawn leaf-02 with a revised brief that places the impl directly in `src/url_utils/types.py` after the parent removes the file from `parent_owned`.
