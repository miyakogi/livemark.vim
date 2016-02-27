#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import time
import subprocess

if __name__ == '__main__':
    script = path.join(path.dirname(__file__), 'livemark/livemark.py')
    args = [sys.executable, script] + sys.argv[1:]
    p = subprocess.Popen(args, stderr=subprocess.PIPE)
    time.sleep(1)  # Wait for server startup
    status = p.poll()
    if status is None:
        print(p.pid, end='')
    else:
        print(p.stderr.read())
    sys.exit()
