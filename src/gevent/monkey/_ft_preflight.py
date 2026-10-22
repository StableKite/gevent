# Copyright (c) 2026 StableKite. Licensed under the gevent LICENSE.
"""FT-CPython early stdlib monkey-patching preflight.

This detects a violated *early patching* contract; it cannot make an
arbitrary global stdlib mutation atomic with unrelated native threads.
"""

import sys
import sysconfig


def require_single_native_thread(*, require_main_thread: bool = True) -> None:
    """Require no other Python OS threads before changing stdlib globals.

    Called before patching thread-related stdlib primitives, and again
    before a public multi-item patch. Already-running native threads
    cannot be safely converted to cooperative threading primitives.
    """
    if sysconfig.get_config_var('Py_GIL_DISABLED') != 1:
        return
    # The GIL-free build must not use a mere threading.active_count()
    # check: a low-level _thread thread may not yet be registered there.
    if len(sys._current_frames()) != 1:  # pyright: ignore[reportPrivateUsage]
        raise RuntimeError(
            'Free-threaded monkey-patching must occur before native OS threads are started'
        )
    if require_main_thread:
        import threading
        if (threading.current_thread() is not threading.main_thread()
                or threading.active_count() != 1):
            raise RuntimeError(
                'Free-threaded monkey-patching requires the main native Python thread'
            )
