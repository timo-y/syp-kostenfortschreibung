"""
#
#   PAY_SAFETY_DEPOSIT_DLG
#   This module creates an trade dialog with the necessary input fields to pay a safety deposit.
#
"""
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate


class AddJobAdditionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.initialize_ui()
        """ set title """
        dialog_title = "Nachtrag hinzufügen..."
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        # TODO: set suffix of input to €
        self.set_date_today()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """

    def initialize_ui(self):
        uic.loadUi("ui/dlg/add_job_addition_dialog.ui", self)  # Load the .ui file

    def set_date_today(self):
        self.dateEdit_date.setDate(QDate.currentDate())

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """

    def get_input(self):
        args = {
            "name": self.lineEdit_name.text(),
            "date": self.dateEdit_date.date(),
            "amount": self.doubleSpinBox_amount.value(),
            "comment": self.textEdit_comment.toPlainText(),
        }
        return args

    """
    #
    #   EXEC
    #
    #
    """

    def exec_(self):
        ok = super().exec_()
        if ok:
            args = self.get_input()
            return args
