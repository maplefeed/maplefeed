# encoding: utf-8
# =======================================
# = This is a "scenario" for doit tool  =
# = http://python-doit.sourceforge.net/ =
# =======================================

import glob
import os
import re
import sys
from pipes import quote

from doit import get_var


DOIT_CONFIG = {
    "reporter": "executed-only",
    "default_tasks": ["default"]
}

CWD = os.getcwd()

PREFIX = "%s/_env" % (CWD)
E_PIP = "%s/bin/pip" % (PREFIX)
E_PYTHON = "%s/bin/python" % (PREFIX)
E_IPYTHON = "%s/bin/ipython" % (PREFIX)
E_PEP8 = "%s/bin/pep8" % (PREFIX)


# prepending env to PYTHONPATH
if os.path.exists(PREFIX):
    activate_this = "%s/bin/activate_this.py" % PREFIX
    if os.path.exists(activate_this):
        execfile(activate_this, dict(__file__=activate_this))
    else:
        print >> sys.stderr, 'env seems to be broken'

# prepending our local sources to PYTHONPATH
sys.path = ["%s/src" % CWD] + sys.path


# helpers
def app_path(app):
    for path in os.getenv('PATH').split(':'):
        app_path = "%s/%s" % (path, app)
        if os.path.exists(app_path):
            return app_path

    return None


def app_in_path(app):
    if app_path(app) is None:
        return False

    return True


def fixed_env(pypath="%s/src" % CWD):
    import copy
    new_env = copy.copy(os.environ)
    new_env['PYTHONPATH'] = pypath

    return new_env


def run_interactive(cmd, env=None):
    if env is None:
        env = fixed_env()

    import subprocess

    return 0 == subprocess.call(cmd, stdout=None, stderr=None, env=env)


FIND = app_path('gfind') or app_path('find')
XARGS = app_path('gxargs') or app_path('xargs')


# tasks
def task_default():
    return {"actions": ['echo run "doit list" to get list of targets'], "verbosity": 2}


def task_install_virtualenv():
    """Install "virtualenv" tool system-wide"""
    return {
        "uptodate": [app_in_path('virtualenv')],
        "actions": ["sudo pip install -q virtualenv"],
        "verbosity": 1
    }


def task_env():
    """Setup "virtual" environment for project"""
    return {
        "uptodate": [os.path.exists(PREFIX)],
        "actions": ["virtualenv --no-site-packages %s" % quote(PREFIX)],
        "task_dep": ["install_virtualenv"]
    }


def task_deps():
    """Install py-dependencies into "virtual" environment"""
    packages = [
        "pep8",
        "ipython",
        "tornado",
        "asyncmongo",
    ]

    for pkg in packages:
        yield {
            "name": pkg,
            "actions": ["%s -q -E %s install %s" % (quote(E_PIP), quote(PREFIX), quote(pkg))],
            "task_dep": ["env"]
        }

def task_clear():
    """remove logs and python's bytecodes"""
    return {
        "actions": [
            "%s . -name '*.pyc' -delete" % FIND,
            "%s . -name '*.log' -delete" % FIND
        ]
    }


def task_python_console():
    """run IPython console"""
    def run_ipython():
        return run_interactive([E_IPYTHON])

    return {
        "task_dep": ["env"],
        "actions": [run_ipython]
    }
