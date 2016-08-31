#!/usr/bin/env python
# -*- coding: utf-8 -*-


from distutils.core import setup

setup(
    # Application name:
    name="syncthingui",

    # Version number (initial):
    version="0.0.2",

    # Application author details:
    author="coolshou",
    # author_email="coolshou@addr.ess",

    # Packages
    packages=['images'],
    package_data={'images': ['images/start.svg',
                              'images/stop.svg', 
                              'images/syncthingui.svg']},
    # packages=["syncthingui"],

    # Include additional files into the package
    data_files=[('/usr/share/applications/', ['syncthingui.desktop']),
                ('/usr/share/icons/', ['syncthingui.png'])],
    # Details
    url="https://github.com/coolshou/syncthingui",

    #
    license="LICENSE",
    description="SyncthinGUI Python3 Qt5 GUI for Syncthing",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    requires=[
        "pyqt5",
        "psutil",
    ],
)
