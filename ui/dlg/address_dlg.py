"""
#
#   ADDRESS_DLG
#   This module creates an address dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, uic
from core.obj import (proj, corp)

class AddressDialog(QtWidgets.QDialog):
    def __init__(self, loaded_address=None):
        super().__init__()
        self.loaded_address = loaded_address

        self.initialize_ui()
        """ set title """
        dialog_title = f"Adresse ({loaded_address.street}, {loaded_address.house_number}) bearbeiten..." if loaded_address else "Neue Adresse"
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())

        if loaded_address:
            loaded_address_args = vars(loaded_address).copy()
            self.set_input(**loaded_address_args)

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/address_dialog.ui', self) # Load the .ui file

    def set_input(self, street, house_number, city, state, zipcode, country):
        self.lineEdit_street.setText(street),
        self.lineEdit_house_number.setText(house_number),
        self.lineEdit_city.setText(city),
        self.lineEdit_state.setText(state),
        self.lineEdit_zipcode.setText(zipcode),
        self.lineEdit_country.setText(country)

    def get_input(self):
        args = {
            "street": self.lineEdit_street.text(),
            "house_number": self.lineEdit_house_number.text(),
            "city": self.lineEdit_city.text(),
            "state": self.lineEdit_state.text(),
            "zipcode": self.lineEdit_zipcode.text(),
            "country": self.lineEdit_country.text()
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
