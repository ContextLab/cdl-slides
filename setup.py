"""Post-install hook to eagerly download marp-cli standalone binary.

Works for source installs (pip install -e . / pip install .).
For wheel installs the lazy download on first compile handles it.
"""

import subprocess
import sys

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def _post_install():
    try:
        subprocess.check_call(
            [sys.executable, "-c", "from cdl_slides.marp_cli import resolve_marp_cli; resolve_marp_cli()"],
            timeout=120,
        )
    except Exception:
        pass


class PostInstall(install):
    def run(self):
        install.run(self)
        _post_install()


class PostDevelop(develop):
    def run(self):
        develop.run(self)
        _post_install()


setup(
    cmdclass={
        "install": PostInstall,
        "develop": PostDevelop,
    }
)
