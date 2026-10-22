"""Backwards compatibility alias for :mod:`gevent.resolver.cares`.

.. deprecated:: 1.3
   Use :mod:`gevent.resolver.cares`
"""
# New A262 series: C-ares native resolver safety is not audited on CP315t.
# pylint:disable=no-name-in-module,import-error
from gevent.resolver.cares import * # pylint:disable=wildcard-import,unused-wildcard-import,
import gevent.resolver.cares as _cares
__all__ = _cares.__all__ # pylint:disable=c-extension-no-member
del _cares
