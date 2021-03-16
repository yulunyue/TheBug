import sys
import os
if len(sys.argv) == 1:
    cmd = 'python -m pytest -v --ignore="c"'
else:
    cmd = 'python -m pytest test/test_%s.py -v --ignore="c"' % sys.argv[1]
print("cmd", cmd)
os.system(cmd)
# import pytest
# pytest.main(['--ignore="c"'])
