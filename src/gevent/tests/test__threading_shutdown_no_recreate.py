"""Finalization must not recreate an explicitly disposed event loop."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import skipIf

from gevent import testing as greentest


PROGRAM = r'''
import sys
from gevent.hub import Hub
from gevent import monkey
import gevent

constructor = Hub.__init__.__code__
path = sys.argv[1]

def record_hub(frame, event, _arg):
    if event == 'call' and frame.f_code is constructor:
        with open(path, 'a', encoding='ascii') as stream:
            stream.write('hub\n')

sys.setprofile(record_hub)
monkey.patch_all()
gevent.sleep(.01)
gevent.get_hub().destroy(destroy_loop=True)
print('HUB_DISPOSED', flush=True)
'''


@skipIf(sys.version_info < (3, 13), 'Python 3.13 thread-handle shutdown')
class Test(greentest.TestCase):

    def test_no_recreation_during_shutdown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'hubs.txt'
            environment = os.environ.copy()
            environment.pop('PYTHON_GIL', None)
            result = subprocess.run(
                [sys.executable, '-B', '-c', PROGRAM, str(path)],
                env=environment, capture_output=True, text=True, timeout=15,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('HUB_DISPOSED', result.stdout)
            self.assertEqual(path.read_text(encoding='ascii').splitlines(), ['hub'])


if __name__ == '__main__':
    greentest.main()
