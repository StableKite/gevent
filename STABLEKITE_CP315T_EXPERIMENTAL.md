# StableKite gevent 26.9.0 CPython 3.15t — EXPERIMENTAL CFFI subset

This branch is an **experimental fork**, not an upstream-equivalent or production-approved gevent release.

Base: upstream gevent/gevent annotated tag 26.9.0 (tag object 38bc046d84dbf0d07117ac7f501821ee3f6dc524), commit 003c77a6f3da41c014dd415022fb61f9d91fc95d.
Sources: seven SHA-256 pinned A263 source overlays, with A267 **source-only proposed** `GEVENT_LOOP` CFFI-safe environment selector in `_config.py`.
The accepted previous A264 wheels contained A263, **not A267**. This new Git branch requires fresh Windows/Linux CPython 3.15t native pip-git install and runtime testing; its source files are not substitutes for previously accepted binary artifacts.

FT CPython: only explicitly selected CFFI libuv/libev backends; no non-audited Cython extension. `gevent.monkey.patch_all()` and native `gevent.ares` are **intentionally unavailable/fail-closed** even when `-X gil=1`. `GEVENT_LOOP` A267 behavior is provisional. Do not interpret fail-closed as positive API coverage.

No deployed StableKite consumer requirements, transitive closure, complete external DNS/ares, hours-long memory/handles stress or feature-owner scope approval have been demonstrated. **Full release STRICT NO-GO**.

Install **only in an isolated CPython 3.15t environment** using an exact reviewed commit SHA after GitHub publishing, for example:

```shell
python -m pip install "gevent @ git+https://github.com/StableKite/gevent.git@<REVIEWED_COMMIT_SHA>"
```

Do not install this branch by name in production. Verify `sys._is_gil_enabled()` before/after imports/Hub under normal and `-X gil=0`, and check `Py_GIL_DISABLED == 1`, the git direct URL commit, and the absence of excluded `.pyd`/`.so` extensions.
