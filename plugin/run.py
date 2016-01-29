#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import subprocess

if __name__ == '__main__':
    script = path.join(path.dirname(__file__), 'livemark.py')
    p = subprocess.Popen([sys.executable, script])
    print(p.pid)
    sys.exit()
