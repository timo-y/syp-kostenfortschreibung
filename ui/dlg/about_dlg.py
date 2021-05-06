"""
#
#   ABOUT_DLG
#   This module creates an info dialog.
#
"""
from PyQt5 import QtWidgets, uic


class AboutDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.initialize_ui()
        """ set title """
        dialog_title = "Über"
        self.setWindowTitle(dialog_title)

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """

    def initialize_ui(self):
        uic.loadUi("ui/dlg/about_dialog.ui", self)
