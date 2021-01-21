"""
#
#   Main programm
#
#
"""
import debug

import sys
import os
import traceback
import logging
import logging.config
import logging.handlers

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from ui import mainwindow
from core import api

MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Application(QtWidgets.QApplication):
    """docstring for Application"""
    def __init__(self, *args, project_file = None, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        """ for debuggin and error tracing """
        self.initialize_logger()

        self.app_data = api.AppData()

        self.window = mainwindow.MainWindow(self.app_data)

        self.initialize_style()
        self.initialize_autosaver()
        self.start_autosaving()

        """ setup exception handling """
        sys.excepthook = self.exception_hook

        if project_file:
            # TODO: convert file into project and add it to self.data
            # self.app_data.project = loaded_project
            pass

    """
    #
    #   STYLE
    #   Load QSS file
    #
    """
    @debug.log
    def initialize_style(self):
        stylesheet_path = os.path.join("qss","style.qss")
        with open(stylesheet_path,"r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

    """
    #
    #   AUTOSAVE
    #
    #
    """
    @debug.log_info
    def initialize_autosaver(self):
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_project)

    @debug.log_info
    def start_autosaving(self):
        autosave_time = self.app_data.config["autosave_time"]
        self.autosave_timer.start(autosave_time)

    @debug.log_info
    def autosave_project(self):
        debug.info_msg("Checking whether the file has already been saved...")
        if self.app_data.project and self.app_data.project.has_been_saved():
            debug.info_msg("Yes! Autosaving...")
            # activate visual indicator, that autosaving is in progress
            self.window.start_autosaving()
            self.app_data.autosave_project()
            self.app_data.delete_old_autosaves()
            # deactivate visual indicator
            self.window.stopp_autosaving()
            debug.info_msg("Saved!")
        else:
            debug.info_msg("Not saved yet, skipping autosave...")

    """
    #
    #   EXCEPTION HANDLING
    #   Catch exceptions and let the programm continue to run
    #
    """
    @debug.log_error
    def exception_hook(self, exctype, value, tb):
        traceback_formated = traceback.format_exception(exctype, value, tb)
        traceback_string = "".join(traceback_formated)
        debug.error_msg(traceback_string)
        self.show_exception_box(traceback_string)
        # QtWidgets.QApplication.quit() # activate this, once serious, before we can mess around with exceptions

    @debug.log
    def show_exception_box(self, log_msg):
        errorbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Oops... Error!", f"Oops. An unexpected error occured:\n{log_msg}")
        errorbox.exec_()

    """
    #
    #   LOGGIN AND DEBUGGING
    #
    #
    """
    def initialize_logger(self):
        logging.config.fileConfig('logging.conf')

        # create logger
        self.logger = logging.getLogger()

if __name__ == '__main__':
    app = Application(sys.argv)
    app.window.show()
    sys.exit(app.exec_())
