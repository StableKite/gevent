"""Real child-process delivery on private free-threaded libuv loops."""
# pragma: testrunner-no-monkey-combine
import os
import sys
import threading
import unittest

import gevent
from gevent._compat import IS_FREE_THREADED_BUILD
from gevent import subprocess
from gevent import testing as greentest


@unittest.skipUnless(IS_FREE_THREADED_BUILD and sys.platform != 'win32',
                     'POSIX free-threaded child watchers')
class Test(greentest.TestCase):

    def setUp(self):
        super().setUp()
        self.children = []

    def tearDown(self):
        for process in self.children:
            process.communicate(timeout=5)
        super().tearDown()

    def child(self, code=7, delay=.05):
        program = 'import time; time.sleep(%r); print("child"); raise SystemExit(%r)' % (delay, code)
        process = subprocess.Popen([sys.executable, '-B', '-c', program],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.children.append(process)
        return process

    def test_subprocess_exit_status(self):
        process = self.child()
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(stdout.strip(), b'child')
        self.assertEqual(stderr, b'')
        self.assertEqual(process.returncode, 7)
        self.assertFalse(gevent.get_hub().loop.default)

    def test_multiple_observers_receive_the_same_status(self):
        process = self.child()
        hub = gevent.get_hub()
        with hub.loop.child(process.pid) as first, hub.loop.child(process.pid) as second:
            jobs = [gevent.spawn(hub.wait, first), gevent.spawn(hub.wait, second)]
            gevent.joinall(jobs, timeout=5, raise_error=True)
            self.assertTrue(all(job.dead for job in jobs))
            self.assertEqual((first.rpid, second.rpid), (process.pid, process.pid))
            self.assertEqual(os.waitstatus_to_exitcode(first.rstatus), 7)
            self.assertEqual(first.rstatus, second.rstatus)
        self.assertEqual(process.wait(timeout=5), 7)

    def test_any_child_does_not_steal_specific_observers(self):
        first, second = self.child(3), self.child(4, .08)
        hub = gevent.get_hub()
        with hub.loop.child(0) as watcher:
            hub.wait(watcher)
            self.assertIn(watcher.rpid, (first.pid, second.pid))
            expected = 3 if watcher.rpid == first.pid else 4
            self.assertEqual(os.waitstatus_to_exitcode(watcher.rstatus), expected)
        self.assertEqual(first.wait(timeout=5), 3)
        self.assertEqual(second.wait(timeout=5), 4)

    def test_closing_one_observer_preserves_the_process_owner(self):
        process = self.child()
        watcher = gevent.get_hub().loop.child(process.pid)
        watcher.start(lambda: self.fail('closed watcher received a callback'))
        watcher.stop()
        watcher.close()
        watcher.close()
        self.assertEqual(process.wait(timeout=5), 7)

    def test_independent_native_os_threads(self):
        barrier = threading.Barrier(2)
        errors, identities, results = [], [], []

        def worker():
            try:
                identities.append(threading.get_native_id())
                barrier.wait(timeout=5)
                for unused in range(3):
                    process = subprocess.Popen([sys.executable, '-B', '-c', 'raise SystemExit(9)'])
                    results.append(process.wait(timeout=5))
            except BaseException as error:
                errors.append(error)
            finally:
                gevent.get_hub().destroy(destroy_loop=True)

        threads = [threading.Thread(target=worker) for unused in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(len(set(identities)), 2)
        self.assertEqual(results, [9] * 6)

    def test_native_waiters_keep_their_own_loop(self):
        from gevent.os import waitpid
        process = self.child(11, .2)
        barrier = threading.Barrier(2)
        results, errors = [], []

        def worker():
            try:
                barrier.wait(timeout=5)
                results.append(waitpid(process.pid, 0))
            except BaseException as error:
                errors.append(error)
            finally:
                gevent.get_hub().destroy(destroy_loop=True)

        threads = [threading.Thread(target=worker) for unused in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0][0], process.pid)
        self.assertEqual(os.waitstatus_to_exitcode(results[0][1]), 11)
        self.assertEqual(process.wait(timeout=5), 11)


if __name__ == '__main__':
    greentest.main()
