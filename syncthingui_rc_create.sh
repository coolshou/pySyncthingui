#!/bin/sh

if ! [ `which pyrcc5` ]; then
    echo "require pyqt5-dev-tools"
fi
echo pyrcc5 -o syncthingui_rc.py syncthingui.qrc
pyrcc5 -o syncthingui_rc.py syncthingui.qrc
