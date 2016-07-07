#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:OK, LINT:OK, PY3:OK
# metadata

'''SyncthinGUI.'''

'''
require: pyqt5 (5.6)
    pip3 install pyqt5
    cp  /usr/local/lib/python3.5/dist-packages/PyQt5/Qt/resources/* /usr/local/lib/python3.5/dist-packages/PyQt5/Qt/libexec/
    cp -R /usr/local/lib/python3.5/dist-packages/PyQt5/Qt/resources/ /usr/local/lib/python3.5/dist-packages/PyQt5/Qt/libexec/qtwebengine_locales/
'''

# imports
import os
import sys
import signal
from datetime import datetime
from ctypes import byref, cdll, create_string_buffer
from getopt import getopt
from subprocess import call, getoutput
from urllib import request
from webbrowser import open_new_tab

# require python3-pyqt5
from PyQt5.QtCore import (QProcess, Qt, QTextStream, QUrl, pyqtSlot, QSize)
from PyQt5.QtGui import QIcon, QTextOption
from PyQt5.QtNetwork import QNetworkRequest
# ubuntu require: python3-pyqt5.qtwebkit
# WebKit1 based
#from PyQt5.QtWebKitWidgets import QWebView as QWebEngineView
# new in python3
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QCheckBox, QInputDialog,
                             QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
                             QTextEdit,
                             QShortcut, QSystemTrayIcon, QProgressBar,
                             QSplitter, QWidget, QFormLayout)

import syncthingui_rc

# metadata
__package__ = "syncthingui"
__version__ = ' 0.0.2 '
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = 'coolshou '
__author_org__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/coolshou/syncthingui#syncthingui'
__source__ = ('https://github.com/coolshou/syncthingui/releases/latest')


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

        self.init_gui()
        self.init_menu()
        self.init_systray()

        self.run()

    def init_gui(self):
        """init gui setup"""
        self.progressbar = QProgressBar()
        self.statusBar().showMessage(getoutput(SYNCTHING + ' --version'))
        self.statusBar().addPermanentWidget(self.progressbar)
        self.setWindowTitle(__doc__.strip().capitalize())
        self.setMinimumSize(900, 600)
        self.setMaximumSize(1280, 1024)
        self.resize(self.minimumSize())
        self.setWindowIcon(QIcon.fromTheme("text-x-python"))
        self.center()

        # QWebView
        # self.view = QWebView(self)
        self.view = QWebEngineView(self)
        self.view.loadStarted.connect(self.start_loading)
        self.view.loadFinished.connect(self.finish_loading)
        self.view.loadProgress.connect(self.loading)
        self.view.titleChanged.connect(self.set_title)
        self.view.page().linkHovered.connect(
            lambda link_txt: self.statusBar().showMessage(link_txt[:99], 3000))
        QShortcut("Ctrl++", self, activated=lambda:
                  self.view.setZoomFactor(self.view.zoomFactor() + 0.2))
        QShortcut("Ctrl+-", self, activated=lambda:
                  self.view.setZoomFactor(self.view.zoomFactor() - 0.2))
        QShortcut("Ctrl+0", self, activated=lambda: self.view.setZoomFactor(1))
        QShortcut("Ctrl+q", self, activated=lambda: self.close())

        # syncthing console
        self.consolewidget = QWidget(self)
        # TODO: start at specify (w,h)
        self.consolewidget.setMinimumSize(QSize(200, 100))
        # TODO: setStyleSheet
        # self.consolewidget.setStyleSheet("margin:0px; padding: 0px; \
        # border:1px solid rgb(0, 0, 0);")
        # border-radius: 40px;")
        # TODO read syncthing console visible from setting
        # self.consolewidget.setVisible(False)
        # self.consolewidget.showEvent
        # self.consoletextedit = QPlainTextEdit(parent=self.consolewidget)
        self.consoletextedit = QTextEdit(parent=self.consolewidget)
        self.consoletextedit.setWordWrapMode(QTextOption.NoWrap)
        # self.consoletextedit.setStyleSheet("margin:0px; padding: 0px;")
        layout = QFormLayout()
        # layout.setSpacing(0)
        layout.addRow(self.consoletextedit)
        self.consolewidget.setLayout(layout)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.consolewidget)

        # process
        self.process = QProcess()
        self.process.error.connect(self._process_failed)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self._process_dataReady)
        # Just to prevent accidentally running multiple times
    # Disable the button when process starts, and enable it when it finishes
    # self.process.started.connect(lambda: self.runButton.setEnabled(False))
    # self.process.finished.connect(lambda: self.runButton.setEnabled(True))

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
        self.toolbar.addSeparator()
        # TODO: test event API


        # final gui setup
        self.setCentralWidget(self.splitter)

    def init_menu(self):
        """init menu setup"""
        # file menu
        file_menu = self.menuBar().addMenu("File")
        # TODO: setting menu item
        file_menu.addAction("Exit", lambda: self.close())
        # Syncthing menu
        sync_menu = self.menuBar().addMenu("Syncthing")
        sync_menu.addAction("Start Syncronization", lambda: self.run())
        sync_menu.addAction("Stop Syncronization", lambda: self.process.kill())
        # TODO: restart
        # TODO: reflash F5
        sync_menu.addAction("Open in external browser",
                            lambda: open_new_tab(URL))

        # view menu
        view_menu = self.menuBar().addMenu("View")
        # TODO: syncthing console menu
        view_menu.addAction("syncthing console", lambda: self.show_console)
        #
        zoom_menu = view_menu.addMenu("Zoom browser")
        zoom_menu.addAction(
            "Zoom In",
            lambda: self.view.setZoomFactor(self.view.zoomFactor() + .2))
        zoom_menu.addAction(
            "Zoom Out",
            lambda: self.view.setZoomFactor(self.view.zoomFactor() - .2))
        zoom_menu.addAction(
            "Zoom To...", lambda: self.view.setZoomFactor(QInputDialog.getInt(
                self, __doc__, "<b>Zoom factor ?:", 1, 1, 9)[0]))
        zoom_menu.addAction("Zoom Reset", lambda: self.view.setZoomFactor(1))
        view_menu.addSeparator()
        view_menu.addAction("View Page Source", lambda: self.view_source)

        # window menu
        window_menu = self.menuBar().addMenu("&Window")
        window_menu.addAction("Minimize", lambda: self.showMinimized())
        window_menu.addAction("Maximize", lambda: self.showMaximized())
        window_menu.addAction("Restore", lambda: self.showNormal())
        window_menu.addAction("Center", lambda: self.center())
        window_menu.addAction("Top-Left", lambda: self.move(0, 0))
        window_menu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        window_menu.addAction("Fullscreen", lambda: self.showFullScreen())
        window_menu.addSeparator()
        window_menu.addAction("Increase size", lambda: self.resize(
            self.size().width() * 1.2, self.size().height() * 1.2))
        window_menu.addAction("Decrease size", lambda: self.resize(
            self.size().width() // 1.2, self.size().height() // 1.2))
        window_menu.addAction("Minimum size", lambda:
                              self.resize(self.minimumSize()))
        window_menu.addAction("Maximum size", lambda:
                              self.resize(self.maximumSize()))
        window_menu.addAction("Horizontal Wide", lambda: self.resize(
            self.maximumSize().width(), self.minimumSize().height()))
        window_menu.addAction("Vertical Tall", lambda: self.resize(
            self.minimumSize().width(), self.maximumSize().height()))
        window_menu.addSeparator()
        window_menu.addAction("Disable Resize",
                              lambda: self.setFixedSize(self.size()))
        # help menu
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction("Support Forum", lambda: open_new_tab(HELP_URL_0))
        help_menu.addAction("Lastest Release", lambda: open_new_tab(HELP_URL_1))
        help_menu.addAction("Documentation", lambda: open_new_tab(HELP_URL_2))
        help_menu.addAction("Bugs", lambda: open_new_tab(HELP_URL_3))
        help_menu.addAction("Source Code", lambda: open_new_tab(HELP_URL_4))
        help_menu.addSeparator()
        help_menu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        help_menu.addAction("About Python 3",
                            lambda: open_new_tab('https://www.python.org'))
        help_menu.addAction("About " + __doc__,
                            lambda: QMessageBox.about(self, __doc__, HELPMSG))
        help_menu.addSeparator()
        help_menu.addAction("Keyboard Shortcuts", lambda:
                            QMessageBox.information(self, __doc__, SHORTCUTS))
        help_menu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        if not sys.platform.startswith("win"):
            help_menu.addAction("Show Source Code", lambda: call(
                ('xdg-open ' if sys.platform.startswith("linux") else 'open ')
                + __file__, shell=True))
        help_menu.addSeparator()
        help_menu.addAction("Check Updates", lambda: self.check_for_updates())

    def init_systray(self):
        """init system tray icon"""
        # System Tray
        # tray = QSystemTrayIcon(QIcon.fromTheme("text-x-python"), self)
        # icon = QIcon("syncthingui.png")
        # TODO: /usr/share/icons/
        # icon = QIcon("syncthingui.svg")
        icon = QIcon(":/images/syncthingui.svg")
        self.setWindowIcon(icon)
        # icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/file/actions/view-right-new-2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # tray = QSystemTrayIcon(QIcon("syncthingui.png"), self)
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip(__doc__.strip().capitalize())
        traymenu = QMenu(self)
        traymenu.addAction(__doc__).setDisabled(True)
        traymenu.addSeparator()
        traymenu.addAction("Stop Sync", lambda: self.process.kill())
        traymenu.addAction("Restart Sync", lambda: self.run())
        traymenu.addSeparator()
        traymenu.addAction("Show", lambda: self.show_gui())
        traymenu.addAction("Hide", lambda: self.hide())
        traymenu.addSeparator()
        # traymenu.addAction("Open Web", lambda: open_new_tab(URL))
        # traymenu.addAction("Quit All", lambda: self.close())
        traymenu.addAction("Quit All", lambda: self.app_exit())
        self.tray.setContextMenu(traymenu)
        self.tray.show()


    def show_gui(self):
        """
        Helper method to show UI, this should not be needed, but I discovered.
        """
        self.showNormal()
        # webview require 70Mb to show webpage
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
        print("ERROR:Fail:Syncthing blow up in pieces! Wheres your God now?")
        return str(self.process.readAllStandardError()).strip().lower()

    def _process_dataReady(self):
        """get process stdout/strerr when data ready"""
        # TODO: format the msg to remove extra b and \n
        msg = str(self.process.readAll())
        self.consoletextedit.append(msg)
        self.consoletextedit.ensureCursorVisible()

    def center(self):
        """Center Window on the Current Screen,with Multi-Monitor support."""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerpoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerpoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position."""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def show_console(self):
        """Show syncthing console"""
        visible = not self.consolewidget.isVisible
        print("bVisible: %s" % visible)
        self.consolewidget.setVisible(True)
        self.consolewidget.resize(QSize(200, 100))

    def view_source(self):
        """Call methods to load and display page source code."""
        access_manager = self.view.page().networkAccessManager()
        reply = access_manager.get(QNetworkRequest(self.view.url()))
        reply.finished.connect(self.slot_source_downloaded)

    def slot_source_downloaded(self):
        """Show actual page source code."""
        reply = self.sender()
        # TODO: highlight html source editor/viewer
        self.textedit = QPlainTextEdit()
        self.textedit.setAttribute(Qt.WA_DeleteOnClose)
        self.textedit.setReadOnly(True)
        self.textedit.setPlainText(QTextStream(reply).readAll())
        self.textedit.show()
        reply.deleteLater()

    @pyqtSlot()
    def start_loading(self):
        """show progressbar when downloading data"""
        self.progressbar.show()

    @pyqtSlot(bool)
    def finish_loading(self, finished):
        """Finished loading content."""
        # TODO: WebEngineView does not have following function?
        # self.view.settings().clearMemoryCaches()
        # self.view.settings().clearIconDatabase()

        # print("finish_loading %s" % datetime.strftime(datetime.now(),
        #                                              '%Y-%m-%d %H:%M:%S'))
        # TODO: following line need 6 sec to finish!!
        # TODO: (" INFO: Loading Web UI increases >250Mb RAM!.")
        # self.view.page().mainFrame().evaluateJavaScript(BASE_JS)
        # print("finish_loading %s" % datetime.strftime(datetime.now(),
        #                                             '%Y-%m-%d %H:%M:%S'))
        self.progressbar.hide()

    @pyqtSlot(int)
    def loading(self, idx):
        """loading content"""
        #print("loading %s" % idx)
        self.progressbar.setValue(idx)

    @pyqtSlot(str)
    def set_title(self, title):
        """set title when webview's title change"""
        # print("title: %s" % title)
        if len(title.strip()) > 0:
            self.setWindowTitle(self.view.title()[:99])

    def check_for_updates(self):
        """Method to check for updates from Git repo versus this version."""
        # print("TODO: https://github.com/coolshou/syncthingui/releases/latest")

        print("__version__: %s" % __version__)
        '''
        this_version = str(open(__file__).read())
        print("this_version: %s" % this_version)
        last_version = str(request.urlopen(__source__).read().decode("utf8"))
        print("last_version: %s" % last_version)

        TODO: previous use file compare, when diff then there is new file!!
        if this_version != last_version:
            m = "Theres new Version available!<br>Download update from the web"
        else:
            m = "No new updates!<br>You have the lastest version of" + __doc__
        return QMessageBox.information(self, __doc__.title(), "<b>" + m)
'''
    def closeEvent(self, event):
        """Ask to Quit."""
        if self.tray.isVisible():
            if self.tray.supportsMessages():
                self.tray.showMessage("Info",
                                      "The program will keep running in the "
                                      "system tray. To terminate the program,"
                                      " choose <b>Quit</b> in the context "
                                      "menu of the system tray entry.")
            else:
                print(" System tray not supports balloon messages ")
            self.hide()
            event.ignore()

    def app_exit(self):
        """exit app"""
        # TODO: do we need to show UI when doing close?
        # self.show_gui()
        # TODO: show QMessageBox on all virtual desktop
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit %s?' % __doc__,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        if the_conditional_is_true:
            QApplication.instance().quit
            quit()

###############################################################################


class Application(QApplication):
    """wrapper QApplication to handle event"""
    def event(self, event_):
        """application event overwrite"""
        return QApplication.event(self, event_)


def signal_handler(signal_, frame):
    """signal handler"""
    print('You pressed Ctrl+C!')
    sys.exit(0)


def main():
    """Main Loop."""
    appname = str(__package__ or __doc__)[:99].lower().strip().replace(" ", "")
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary('libc.so.6')  # set process name
        buff = create_string_buffer(len(appname) + 1)
        buff.value = bytes(appname.encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception as reason:
        print(reason)
    # app = QApplication(sys.argv)
    app = Application(sys.argv)
    # Connect your cleanup function to signal.SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    # And start a timer to call Application.event repeatedly.
    # You can change the timer parameter as you like.
    app.startTimer(200)

    app.setApplicationName(__doc__.strip().lower())
    app.setOrganizationName(__doc__.strip().lower())
    app.setOrganizationDomain(__doc__.strip())
    # app.setWindowIcon(QIcon.fromTheme("text-x-python"))
    web = MainWindow()
    app.aboutToQuit.connect(web.process.kill)
    try:
        opts, args = getopt(sys.argv[1:], 'hv', ('version', 'help'))
    except:
        pass
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(''' Usage:
                  -h, --help        Show help informations and exit.
                  -v, --version     Show version information and exit.''')
            return sys.exit(1)
        elif opt in ('-v', '--version'):
            print(__version__)
            return sys.exit(1)
    # web.show()  # comment out to hide/show main window, normally dont needed
    sys.exit(app.exec_())


if __name__ in '__main__':
    main()
