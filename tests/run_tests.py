#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

import sys
import os
import nose

from os.path import abspath, dirname


def run_all(argv=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    sys.exitfunc = lambda msg='Process shutting down...': sys.stderr.write(msg + '\n')

    # called by setuptools
    params = ['--with-coverage', '--cover-package=ella_hub', '--cover-erase',
              '--with-xunit', '--nocapture', ]
    if argv is None:
        argv = ['nosetests'] + params
    elif len(argv) == 1:  # only the command itself is in argv
        argv += params
    elif len(argv) > 1:
        argv = argv[:1] + params + argv[1:]

    nose.run_exit(
        argv=argv,
        defaultTest=abspath(dirname(__file__)),
    )

if __name__ == '__main__':
    run_all(sys.argv)
