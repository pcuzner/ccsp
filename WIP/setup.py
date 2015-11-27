#!/usr/bin/python

__author__ = 'paul'

from setuptools import setup
import distutils.command.install_scripts
import shutil
import os

# Use any provided README as the long description for the package
if os.path.exists('README'):
    with open('README') as f:
        long_description = f.read().strip()
else:
    long_description = ''


# idea from http://stackoverflow.com/a/11400431/2139420
class StripExtention(distutils.command.install_scripts.install_scripts):
    def run(self):
        distutils.command.install_scripts.install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                shutil.move(script, script[:-3])

conf_path = '/etc/'

setup(
    name="rhs-usage",
    version="0.1",
    description="Monitor capacity utilisation of ceph or gluster clusters",
    long_description=long_description,
    author="Paul Cuzner",
    author_email="pcuzner@redhat.com",
    url="https://github.com/pcuzner/bla",
    license="GPLv3",
    data_files=[(conf_path, 'rhs-usage.conf')],
    packages=[
        "rhsusage",
        "rhsusage.collectors",
        "rhsusage.tasks"
        ],
    scripts=["rhs-usage.py"],
    cmdclass={
        "install_scripts": StripExtention
    }
)
