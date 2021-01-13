"""
#
#   COMPANY_DLG
#   This module creates an company dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, QtGui, uic

from ui import dlg, helper
from ui.helper import two_inputs_to_float, amount_str, rnd
from core.obj import (proj, corp, arch, uid)

class CompanyDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, loaded_company=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data

        self.vat = app_data.project.get_vat()
        self.currency = app_data.project.get_currency()

        self.sel_contact_person = None
        self.loaded_company = loaded_company

        self.initialize_ui()
        """ set title """
        dialog_title = f"Firma ({loaded_company.name}) bearbeiten..." if loaded_company else "Neue Firma"
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_button_actions()
        self.set_event_handler()
        self.set_validators()
        self.set_default_labels()


        if self.loaded_company:
            """ activate delete button """
            self.pushButton_delete.setEnabled(True)
            """ load company data to input """
            loaded_args = self.loaded_company.__dict__.copy()
            self.set_input(**loaded_args)
            self.sel_contact_person = loaded_company.contact_person

        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/company_dialog.ui', self)

    def setup_combo_boxes(self):
       pass

    def set_default_labels(self):
        pass

    def set_validators(self):
        pass

    def update_ui(self):
        sel_c_p_first_name = self.sel_contact_person.first_name if self.sel_contact_person else "-"
        sel_c_p_last_name = self.sel_contact_person.last_name if self.sel_contact_person else "-"
        args = self.get_input()
        self.set_labels(budget_w_VAT=args["budget"]*(1+self.vat),
                        budget_VAT_amount=args["budget"]*self.vat,
                        contact_person_first_name=sel_c_p_first_name,
                        contact_person_last_name=sel_c_p_last_name)

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        """ add company """
        self.pushButton_add_contact_person.clicked.connect(self.add_new_contact_person)
        self.pushButton_edit_contact_person.clicked.connect(self.edit_contact_person)

        """ delete button """
        self.pushButton_delete.clicked.connect(lambda:helper.delete(self, self.loaded_company))

    def set_event_handler(self):
        self.keyReleaseEvent = self.eventHandler
        self.mouseReleaseEvent = self.eventHandler
    """ add event handler """
    def eventHandler(self, event):
        self.update_ui()

    """
    #
    #   FUNCTIONALITY
    #   Functions that let the dialog do something
    #
    """
    def add_new_contact_person(self):
        contact_person = helper.input_person(self.app_data)
        if contact_person:
            self.sel_contact_person
            self.update_ui()

    def edit_contact_person(self):
        if self.sel_contact_person:
            helper.edit_peron(self.app_data, self.sel_contact_person)
            self.update_ui()
        else:
            raise Exception("No contact person defined!")

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_labels(self, *, budget_w_VAT, budget_VAT_amount, contact_person_first_name, contact_person_last_name):
        """ budget """
        self.label_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_budget_VAT_amount.setText(amount_str(budget_VAT_amount))
        """ contact person """
        self.label_contact_person_first_name.setText(contact_person_first_name)
        self.label_contact_person_last_name.setText(contact_person_last_name)

    """ set input fields """
    def set_input(self, *, _uid=None, name="", service="", service_type="", budget=0, **kwargs):
        """ data """
        self.label_uid.setText(_uid.labelize() if _uid else "-")
        """ company attributes """
        self.lineEdit_name.setText(name)
        self.lineEdit_service.setText(service)
        self.lineEdit_service_type.setText(service_type)
        """ budget """
        self.lineEdit_budget_1.setText(str(int(budget)) if int(budget)>0 else "")
        self.lineEdit_budget_2.setText(f"{int(rnd(budget-int(budget))*100):02d}" if budget-int(budget)>0 else "")

    def get_input(self):
        args = {
                "name": self.lineEdit_name.text(),
                "service": self.lineEdit_service.text(),
                "service_type": self.lineEdit_service_type.text(),
                "budget": two_inputs_to_float(self.lineEdit_budget_1, self.lineEdit_budget_2),
                "contact_person": self.sel_contact_person
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
