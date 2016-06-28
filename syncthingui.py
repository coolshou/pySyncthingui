#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:OK, LINT:OK, PY3:OK

# imports
import os
import sys
from ctypes import byref, cdll, create_string_buffer
from getopt import getopt
from subprocess import call, getoutput
from urllib import request
from webbrowser import open_new_tab

from PyQt5.QtCore import QProcess, Qt, QTextStream, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QNetworkRequest
# ubuntu require: python3-pyqt5.qtwebkit
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import (QApplication, QCheckBox, QInputDialog,
                             QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
                             QShortcut, QSystemTrayIcon)

# metadata
"""SyncthinGUI."""
__package__ = "syncthingui"
__version__ = ' 0.0.2 '
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = 'coolshou '
__author_org__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/coolshou/syncthingui#syncthingui'
__source__ = ('https://github.com/coolshou/syncthingui/releases')


URL, SYNCTHING = "http://127.0.0.1:8384", "syncthing"
HELP_URL_0 = "http://forum.syncthing.net"
HELP_URL_1 = "https://github.com/syncthing/syncthing/releases"
HELP_URL_2 = "http://docs.syncthing.net"
HELP_URL_3 = "https://github.com/syncthing/syncthing/issues"
HELP_URL_4 = "https://github.com/syncthing/syncthing"
SHORTCUTS = """<b>Quit = CTRL + Q<br>Zoom Up = CTRL + +<br>
               Zoom Down = CTRL + -<br>Zoom Reset = CTRL + 0"""
HELPMSG = """<h3>SyncthinGUI</h3>Python3 Qt5 GUI for Syncthing,GPLv3+LGPLv3<hr>
<i>KISS DRY SingleFile Async CrossDesktop CrossDistro SelfUpdating</i><br><br>
DEV: <a href=https://github.com/coolshou/syncthingui>Coolshou</a><br>
Original DEV: <a href=https://github.com/juancarlospaco>JuanCarlos</a><br>
<br>
""" + getoutput(SYNCTHING + ' --version')
BASE_JS = """var custom_css = document.createElement("style");
custom_css.textContent = '*{font-family:Oxygen}';
custom_css.textContent += 'body{background-color:lightgray}';
custom_css.textContent += '.navbar-fixed-bottom{display:none}';
document.querySelector("head").appendChild(custom_css);"""


###############################################################################


class MainWindow(QMainWindow):

    """Main window class."""

    def __init__(self):
        """Init class."""
        super(MainWindow, self).__init__()
        self.statusBar().showMessage(getoutput(SYNCTHING + ' --version'))
        self.setWindowTitle(__doc__.strip().capitalize())
        self.setMinimumSize(900, 600)
        self.setMaximumSize(1280, 1024)
        self.resize(self.minimumSize())
        self.setWindowIcon(QIcon.fromTheme("text-x-python"))
        self.center()
        self.view = QWebView(self)
        self.view.loadFinished.connect(self.finishLoading)
        self.view.page().linkHovered.connect(
            lambda link_txt: self.statusBar().showMessage(link_txt[:99], 3000))
        QShortcut("Ctrl++", self, activated=lambda:
                  self.view.setZoomFactor(self.view.zoomFactor() + 0.2))
        QShortcut("Ctrl+-", self, activated=lambda:
                  self.view.setZoomFactor(self.view.zoomFactor() - 0.2))
        QShortcut("Ctrl+0", self, activated=lambda: self.view.setZoomFactor(1))
        QShortcut("Ctrl+q", self, activated=lambda: self.close())
        self.menuBar().addMenu("File").addAction("Exit", lambda: self.close())
        syncMenu = self.menuBar().addMenu("Sync")
        syncMenu.addAction("Stop Syncronization", lambda: self.process.kill())
        syncMenu.addAction("Start Syncronization", lambda: self.run())
        viewMenu = self.menuBar().addMenu("View")
        viewMenu.addAction(
            "Zoom In",
            lambda: self.view.setZoomFactor(self.view.zoomFactor() + .2))
        viewMenu.addAction(
            "Zoom Out",
            lambda: self.view.setZoomFactor(self.view.zoomFactor() - .2))
        viewMenu.addAction(
            "Zoom To...", lambda: self.view.setZoomFactor(QInputDialog.getInt(
                self, __doc__, "<b>Zoom factor ?:", 1, 1, 9)[0]))
        viewMenu.addAction("Zoom Reset", lambda: self.view.setZoomFactor(1))
        viewMenu.addSeparator()
        viewMenu.addAction("Page Source", self.viewSource)
        viewMenu.addAction("Open Web", lambda: open_new_tab(URL))
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("Top-Left", lambda: self.move(0, 0))
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        windowMenu.addAction("Fullscreen", lambda: self.showFullScreen())
        windowMenu.addSeparator()
        windowMenu.addAction("Increase size", lambda: self.resize(
            self.size().width() * 1.2, self.size().height() * 1.2))
        windowMenu.addAction("Decrease size", lambda: self.resize(
            self.size().width() // 1.2, self.size().height() // 1.2))
        windowMenu.addAction("Minimum size", lambda:
                             self.resize(self.minimumSize()))
        windowMenu.addAction("Maximum size", lambda:
                             self.resize(self.maximumSize()))
        windowMenu.addAction("Horizontal Wide", lambda: self.resize(
            self.maximumSize().width(), self.minimumSize().height()))
        windowMenu.addAction("Vertical Tall", lambda: self.resize(
            self.minimumSize().width(), self.maximumSize().height()))
        windowMenu.addSeparator()
        windowMenu.addAction("Disable Resize",
                             lambda: self.setFixedSize(self.size()))
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("Support Forum", lambda: open_new_tab(HELP_URL_0))
        helpMenu.addAction("Lastest Release", lambda: open_new_tab(HELP_URL_1))
        helpMenu.addAction("Documentation", lambda: open_new_tab(HELP_URL_2))
        helpMenu.addAction("Bugs", lambda: open_new_tab(HELP_URL_3))
        helpMenu.addAction("Source Code", lambda: open_new_tab(HELP_URL_4))
        helpMenu.addSeparator()
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3",
                           lambda: open_new_tab('https://www.python.org'))
        helpMenu.addAction("About " + __doc__,
                           lambda: QMessageBox.about(self, __doc__, HELPMSG))
        helpMenu.addSeparator()
        helpMenu.addAction("Keyboard Shortcuts", lambda:
                           QMessageBox.information(self, __doc__, SHORTCUTS))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        if not sys.platform.startswith("win"):
            helpMenu.addAction("Show Source Code", lambda: call(
                ('xdg-open ' if sys.platform.startswith("linux") else 'open ')
                + __file__, shell=True))
        helpMenu.addSeparator()
        helpMenu.addAction("Check Updates", lambda: self.check_for_updates())
        # process
        self.process = QProcess()
        self.process.error.connect(self._process_failed)
        # backend options
        self.chrt = QCheckBox("Smooth CPU ", checked=True)
        self.ionice = QCheckBox("Smooth HDD ", checked=True)
        self.chrt.setToolTip("Use Smooth CPUs priority (recommended)")
        self.ionice.setToolTip("Use Smooth HDDs priority (recommended)")
        self.chrt.setStatusTip(self.chrt.toolTip())
        self.ionice.setStatusTip(self.ionice.toolTip())
        # main toolbar
        self.toolbar = self.addToolBar("SyncthinGUI Toolbar")
        self.toolbar.addAction(QIcon.fromTheme("media-playback-stop"),
                               "Stop Sync", lambda: self.process.kill())
        self.toolbar.addAction(QIcon.fromTheme("media-playback-start"),
                               "Restart Sync", lambda: self.run())
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.chrt)
        self.toolbar.addWidget(self.ionice)
        self.setCentralWidget(self.view)
        # Tray Icon
        # tray = QSystemTrayIcon(QIcon.fromTheme("text-x-python"), self)
        icon = QIcon("syncthingui.png")
        self.setWindowIcon(icon)
        # icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/file/actions/view-right-new-2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # tray = QSystemTrayIcon(QIcon("syncthingui.png"), self)
        tray = QSystemTrayIcon(icon, self)
        tray.setToolTip(__doc__.strip().capitalize())
        traymenu = QMenu(self)
        traymenu.addAction(__doc__).setDisabled(True)
        traymenu.addSeparator()
        traymenu.addAction("Stop Sync", lambda: self.process.kill())
        traymenu.addAction("Restart Sync", lambda: self.run())
        traymenu.addSeparator()
        traymenu.addAction("Show", lambda: self.show_gui())
        traymenu.addAction("Hide", lambda: self.hide())
        traymenu.addSeparator()
        traymenu.addAction("Open Web", lambda: open_new_tab(URL))
        traymenu.addAction("Quit All", lambda: self.close())
        tray.setContextMenu(traymenu)
        tray.show()
        self.run()

    def show_gui(self):
        """
        Helper method to show UI, this should not be needed, but I discovered.

        loading WebUI increase >250Mb RAM!,go blame AngularJS/JQuery2 not me.
        """
        print(" INFO: Loading Web UI increases >250Mb RAM!.")
        self.showNormal()
        self.view.load(QUrl(URL))

    def run(self):
        """Run bitch run!."""
        self.process.kill()
        command_to_run_syncthing = " ".join((
            "ionice --ignore --class 3" if self.ionice.isChecked() else "",
            "chrt --verbose --idle 0" if self.chrt.isChecked() else "",
            SYNCTHING, "-no-browser"))
        print(command_to_run_syncthing)
        self.process.start(command_to_run_syncthing)
        if not self.process.waitForStarted():
            self._process_failed()

    def _process_failed(self):
        """Read and return errors."""
        self.statusBar().showMessage("ERROR:Fail:Syncthing blow up in pieces!")
        print("ERROR:Fail:Syncthing blow up in pieces! Wheres your God now ?")
        return str(self.process.readAllStandardError()).strip().lower()

    def center(self):
        """Center Window on the Current Screen,with Multi-Monitor support."""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerPoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position."""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def viewSource(self):
        """Call methods to load and display page source code."""
        accessManager = self.view.page().networkAccessManager()
        reply = accessManager.get(QNetworkRequest(self.view.url()))
        reply.finished.connect(self.slotSourceDownloaded)

    def slotSourceDownloaded(self):
        """Show actual page source code."""
        reply = self.sender()
        self.textEdit = QPlainTextEdit()
        self.textEdit.setAttribute(Qt.WA_DeleteOnClose)
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlainText(QTextStream(reply).readAll())
        self.textEdit.show()
        reply.deleteLater()

    def finishLoading(self):
        """Finished loading content."""
        self.setWindowTitle(self.view.title()[:99])
        self.view.settings().clearMemoryCaches()
        self.view.settings().clearIconDatabase()
        self.view.page().mainFrame().evaluateJavaScript(BASE_JS)

    def check_for_updates(self):
        """Method to check for updates from Git repo versus this version."""
        print("TODO: https://github.com/coolshou/syncthingui/releases")
        '''
        this_version = str(open(__file__).read())
        last_version = str(request.urlopen(__source__).read().decode("utf8"))
        if this_version != last_version:
            m = "Theres new Version available!<br>Download update from the web"
        else:
            m = "No new updates!<br>You have the lastest version of" + __doc__
        return QMessageBox.information(self, __doc__.title(), "<b>" + m)
        '''
    def closeEvent(self, event):
        """Ask to Quit."""
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit ?.', QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        event.accept() if the_conditional_is_true else event.ignore()


###############################################################################


def main():
    """Main Loop."""
    APPNAME = str(__package__ or __doc__)[:99].lower().strip().replace(" ", "")
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary('libc.so.6')  # set process name
        buff = create_string_buffer(len(APPNAME) + 1)
        buff.value = bytes(APPNAME.encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception as reason:
        print(reason)
    app = QApplication(sys.argv)
    app.setApplicationName(__doc__.strip().lower())
    app.setOrganizationName(__doc__.strip().lower())
    app.setOrganizationDomain(__doc__.strip())
    app.setWindowIcon(QIcon.fromTheme("text-x-python"))
    web = MainWindow()
    app.aboutToQuit.connect(web.process.kill)
    try:
        opts, args = getopt(sys.argv[1:], 'hv', ('version', 'help'))
    except:
        pass
    for o, v in opts:
        if o in ('-h', '--help'):
            print(''' Usage:
                  -h, --help        Show help informations and exit.
                  -v, --version     Show version information and exit.''')
            return sys.exit(1)
        elif o in ('-v', '--version'):
            print(__version__)
            return sys.exit(1)
    # web.show()  # comment out to hide/show main window, normally dont needed
    sys.exit(app.exec_())


if __name__ in '__main__':
    main()
