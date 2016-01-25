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


setup(
    name="rhs-usage",
    version="0.3",
    description="Monitor capacity utilisation of ceph or gluster clusters",
    long_description=long_description,
    author="Paul Cuzner",
    author_email="pcuzner@redhat.com",
    url="https://github.com/pcuzner/ccsp",
    license="GPLv3",
    data_files=[("/etc", ["rhs-usage.conf"]),
                # ("/etc/init", ["startup/rhs-usage.conf"]),
                ("/var/www/ccsp/css", ["www/css/rhs-usage.css"]),
                ("/var/www/ccsp/images", ["www/images/logo.png",
                                          "www/images/redhat.ico",
                                          "www/images/usage_chart.png"]),
                ("/var/www/ccsp/js", ["www/js/page_ready.js",
                                      "www/js/update_details.js",
                                      "www/js/update_mode.js"]),
                ("/var/www/ccsp", ["www/index.html"])],
    packages=[
        "rhsusage",
        "rhsusage.collectors",
        "rhsusage.tasks"
    ],
    scripts=["rhs_usage.py", "rhsextract.py"],
    cmdclass={
        "install_scripts": StripExtention
    }
)
