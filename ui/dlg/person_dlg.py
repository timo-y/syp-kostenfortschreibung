"""
#
#   PERSON_DLG
#   This module creates an person dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, uic

from ui import helper
from core.obj import proj, corp


class PersonDialog(QtWidgets.QDialog):
    def __init__(self, loaded_person=None):
        super().__init__()
        """ create local variables """
        # app_data ???
        self.address = None
        self.loaded_person = loaded_person

        self.initialize_ui()
        """ set title """
        dialog_title = (
            f"Person ({loaded_person.first_name}, {loaded_person.last_name}) bearbeiten..."
            if loaded_person
            else "Neuer Person"
        )
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.set_button_actions()
        if self.loaded_person:
            """activate delete button"""
            self.pushButton_delete.setEnabled(True)
            """ load person data to input """
            loaded_args = self.loaded_person.__dict__.copy()
            self.set_input(**loaded_args)

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """

    def initialize_ui(self):
        uic.loadUi("ui/dlg/person_dialog.ui", self)

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """

    def set_button_actions(self):
        """delete button"""
        self.pushButton_delete.clicked.connect(
            lambda: helper.delete(self, self.loaded_person)
        )

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """

    def set_input(
        self,
        *,
        _uid=None,
        first_name="",
        last_name="",
        telephone="",
        fax="",
        mobile="",
        email="",
        address=None,
        **kwargs,
    ):
        """data"""
        self.label_uid.setText(_uid.labelize())
        """ person attributes """
        self.lineEdit_first_name.setText(first_name)
        self.lineEdit_last_name.setText(last_name)
        self.lineEdit_telephone.setText(telephone)
        self.lineEdit_fax.setText(fax)
        self.lineEdit_mobile.setText(mobile)
        self.lineEdit_email.setText(email)
        """ address """
        if address:
            self.lineEdit_street.setText(address.street)
            self.lineEdit_house_number.setText(str(address.house_number))
            self.lineEdit_city.setText(address.city)
            self.lineEdit_state.setText(address.state)
            self.lineEdit_zipcode.setText(str(address.zipcode))
            self.lineEdit_country.setText(address.country)

    def get_input(self):
        address = {
            "street": self.lineEdit_street.text(),
            "house_number": self.lineEdit_house_number.text(),
            "city": self.lineEdit_city.text(),
            "state": self.lineEdit_state.text(),
            "zipcode": self.lineEdit_zipcode.text(),
            "country": self.lineEdit_country.text(),
        }
        args = {
            "first_name": self.lineEdit_first_name.text(),
            "last_name": self.lineEdit_last_name.text(),
            "telephone": self.lineEdit_telephone.text(),
            "fax": self.lineEdit_fax.text(),
            "mobile": self.lineEdit_mobile.text(),
            "email": self.lineEdit_email.text(),
            "address": corp.Address(**address),
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
            return ok, args
