#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import subprocess

if __name__ == '__main__':
    script = path.join(path.dirname(__file__), 'livemark.py')
    args = [sys.executable, script]
    for arg in sys.argv:
        if arg.startswith('-'):
            args.append(arg)
    p = subprocess.Popen(args)
    print(p.pid, end='')
    sys.exit()
