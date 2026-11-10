"""Child notifications for isolated free-threaded POSIX event loops."""
from collections import deque
from _thread import RLock
from operator import index
from os import getpid, register_at_fork, WNOHANG, WIFEXITED, WIFSIGNALED
import os

from gevent.os import _waitpid


_lock = RLock()
_tokens = set()


def _after_fork():
    global _lock, _tokens
    _lock = RLock()
    _tokens = set()


register_at_fork(after_in_child=_after_fork)


class _Token:
    def __init__(self, pid, trace):
        self.pid = pid
        self.trace = trace
        self.events = deque()
        self.finished = False
        self.last_event = None


def _subscribe(pid, trace):
    token = _Token(pid, trace)
    with _lock:
        if pid:
            for observer in _tokens:
                if observer.finished and observer.last_event is not None and observer.last_event[0] == pid:
                    token.events.append(observer.last_event)
                    token.finished = True
                    token.last_event = observer.last_event
                    break
        _tokens.add(token)
    return token


def _unsubscribe(token):
    with _lock:
        _tokens.discard(token)


def _take(token):
    # Native waitpid is nonblocking here. Serialize reaping and retain a copy
    # for every registered observer; no event loop touches another loop.
    with _lock:
        if token.events:
            return token.events.popleft()
        if token.finished:
            return None
        flags = WNOHANG
        if token.trace:
            flags |= getattr(os, 'WUNTRACED', 0) | getattr(os, 'WCONTINUED', 0)
        try:
            pid, status = _waitpid(token.pid or -1, flags)
        except InterruptedError:
            return None
        if not pid:
            return None
        terminal = WIFEXITED(status) or WIFSIGNALED(status)
        for observer in tuple(_tokens):
            if observer.finished or observer.pid not in (0, pid):
                continue
            if not terminal and not observer.trace:
                continue
            observer.events.append((pid, status))
            observer.last_event = (pid, status)
            observer.finished = terminal or observer.pid == 0
        return token.events.popleft() if token.events else None


class child:
    """A per-loop timer observes process state without a shared uv loop."""

    _INTERVAL = .005

    def __init__(self, loop, pid, trace=0, ref=True):
        self.loop = loop
        self._pid = index(pid)
        if self._pid < 0:
            raise ValueError('child watcher pid must be nonnegative')
        self._trace = bool(trace)
        self._owner_pid = getpid()
        self._rpid = None
        self._rstatus = 0
        self._token = None
        self.callback = None
        self.args = None
        self._timer = loop.timer(self._INTERVAL, self._INTERVAL, ref=ref)

    @property
    def pid(self):
        return self._pid

    @property
    def rpid(self):
        return self._rpid

    @property
    def rstatus(self):
        return self._rstatus

    @property
    def active(self):
        return self._token is not None and self._timer.active

    @property
    def pending(self):
        return self._timer.pending

    @property
    def ref(self):
        return self._timer.ref

    @ref.setter
    def ref(self, value):
        self._timer.ref = value

    @property
    def priority(self):
        return self._timer.priority

    @priority.setter
    def priority(self, value):
        self._timer.priority = value

    def start(self, callback, *args):
        if self.loop is None:
            raise ValueError('Closed child watcher')
        if self.active:
            raise ValueError('Child watcher is already active')
        if not callable(callback):
            raise TypeError('child callback must be callable')
        self.callback = callback
        self.args = args
        self._token = _subscribe(self._pid, self._trace)
        try:
            self._timer.start(self._poll)
        except BaseException:
            self.stop()
            raise

    def _poll(self):
        if self._token is None:
            return
        if self._owner_pid != getpid():
            # Inherited observations describe the parent's children.
            self.close()
            return
        event = _take(self._token)
        if event is not None:
            self._rpid, self._rstatus = event
            self.callback(*self.args)

    def stop(self):
        self._timer.stop()
        if self._token is not None:
            _unsubscribe(self._token)
            self._token = None
        self.callback = None
        self.args = None

    def close(self):
        if self.loop is None:
            return
        self.stop()
        self._timer.close()
        self.loop = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()

