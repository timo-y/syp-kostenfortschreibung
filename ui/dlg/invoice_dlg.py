"""
#
#   INVOICE_DLG
#   This module creates an invoice dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import (QDialog, QInputDialog, QFileDialog, QDialogButtonBox)
from PyQt5.QtCore import QDate

from ui import dlg, helper
from ui.helper import input_to_float, two_inputs_to_float, str_to_float, amount_str, amount_w_currency_str, rnd
from core.obj import (proj, corp, arch)

class InvoiceDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, sel_job=None, loaded_invoice=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.default_vat = app_data.project.config["default_vat"]
        self.currency = app_data.project.config["currency"]
        self.prev_invoices = list()
        self.tmp_invoice = corp.Invoice()
        self.loaded_invoice = loaded_invoice

        self.initialize_ui()
        """ set title """
        dialog_title = f"Rechnung ({loaded_invoice.id}) bearbeiten..." if loaded_invoice else "Neue Rechnung"
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_button_actions()
        self.set_check_box_actions()
        self.set_spin_box_actions()
        self.set_combo_box_actions()
        self.set_date_edit_actions()
        self.set_event_handler()
        self.set_validators()

        self.set_date_today()
        self.uncheck_boxes()
        self.set_default_labels()
        # no idea, why this line is needed, but it is on this dialog
        self.lineEdit_id.setFocus()

        if self.loaded_invoice:
            """ activate delete button """
            self.pushButton_delete.setEnabled(True)
            """ load invoice data to input """
            loaded_args = vars(self.loaded_invoice).copy()
            self.prev_invoices = self.loaded_invoice.prev_invoices
            self.set_input(**loaded_args)
        elif sel_job:
            self.set_company_to(sel_job.company)
            self.setup_combo_box_jobs()
            self.set_job_to(sel_job)

        self.update_prev_invoices()
        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/invoice_dialog.ui', self) # Load the .ui file

    def setup_combo_boxes(self):
        self.setup_combo_box_companies()
        self.setup_combo_box_jobs()

    def setup_combo_box_companies(self):
        self.comboBox_company.clear()
        self.comboBox_company.addItem("Firma auswählen...", None)
        for company in self.app_data.project.companies:
            self.comboBox_company.addItem(company.name, company)

    def setup_combo_box_jobs(self):
        sel_company = self.comboBox_company.currentData()
        self.comboBox_job.clear()
        self.comboBox_job.addItem("Auftrag auswählen...", None)
        if sel_company:
            """ activate combobox only if there exists at least one job """
            got_a_job = False
            for job in self.app_data.project.jobs:
                if job.company is sel_company:
                    got_a_job = True
                    self.comboBox_job.addItem(str(job.id), job)
            if got_a_job:
                self.comboBox_job.setEnabled(True)
            else:
                self.comboBox_job.setEnabled(False)
        else:
            self.comboBox_job.setEnabled(False)

    def set_default_labels(self):
        """ set default vat """
        self.doubleSpinBox_VAT.setValue(self.default_vat*100)
        """ set currency """
        currency_labels = [label for label in self.findChildren(QtWidgets.QLabel) if "label_currency_" in label.objectName()]
        for label in currency_labels:
            label.setText(self.app_data.project.get_currency())

    def set_validators(self):
        # to allow only int
        onlyInt = QtGui.QIntValidator()
        self.lineEdit_amount_1.setValidator(onlyInt)
        self.lineEdit_amount_2.setValidator(onlyInt)
        self.lineEdit_verified_amount_1.setValidator(onlyInt)
        self.lineEdit_verified_amount_2.setValidator(onlyInt)
        # to allow only double
        onlyDouble = QtGui.QDoubleValidator(decimals=2)
        # self.lineEdit_prev_invoices_amount.setValidator(onlyDouble)

    def activate_ok_button(self):
        args = self.get_input()
        if len(args["id"])>0 and args["company"] and args["job"]:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def update_ui(self):
        args = self.get_input()

        self.tmp_invoice = corp.Invoice(**args, prev_invoices=self.prev_invoices)
        #""" update the values of the labels """#
        self.set_labels(amount_w_VAT=self.tmp_invoice.amount_w_VAT,
            amount_VAT_amount=self.tmp_invoice.amount_VAT_amount,
            verified_amount_w_VAT=self.tmp_invoice.verified_amount_w_VAT,
            verified_amount_VAT_amount=self.tmp_invoice.verified_amount_VAT_amount,
            prev_invoices_count=str(len(self.prev_invoices)),
            prev_invoices_amount=self.tmp_invoice.prev_invoices_amount,
            rebate_amount=self.tmp_invoice.rebate_amount,
            reduction_insurance_costs_amount=self.tmp_invoice.reduction_insurance_costs_amount,
            reduction_usage_costs_amount=self.tmp_invoice.reduction_usage_costs_amount,
            amount_a_reductions_amount=self.tmp_invoice.amount_a_reductions_amount,
            amount_a_reductions_amount_w_VAT=self.tmp_invoice.amount_a_reductions_amount_w_VAT,
            amount_a_reductions_amount_VAT_amount=self.tmp_invoice.amount_a_reductions_amount_VAT_amount,
            safety_deposit_amount=self.tmp_invoice.safety_deposit_amount,
            approved_amount=self.tmp_invoice.approved_amount,
            discount_amount=self.tmp_invoice.discount_amount,
            approved_amount_a_discount_amount=self.tmp_invoice.approved_amount_a_discount_amount)

        self.activate_ok_button()

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        """ date buttons """
        self.pushButton_invoice_date_set_today.clicked.connect(lambda:self.dateEdit_invoice_date.setDate(QDate.currentDate()))
        self.pushButton_inbox_date_set_today.clicked.connect(lambda:self.dateEdit_inbox_date.setDate(QDate.currentDate()))
        self.pushButton_checked_date_set_today.clicked.connect(lambda:self.dateEdit_checked_date.setDate(QDate.currentDate()))
        self.pushButton_due_date_set_today.clicked.connect(lambda:self.dateEdit_due_date.setDate(QDate.currentDate()))
        self.pushButton_due_date_discount_set_today.clicked.connect(lambda:self.dateEdit_due_date_discount.setDate(QDate.currentDate()))

        """ add company """
        self.pushButton_add_company.clicked.connect(self.add_new_company)

        """ add job """
        self.pushButton_add_job.clicked.connect(self.add_new_job)

        """ delete button """
        self.pushButton_delete.clicked.connect(lambda:helper.delete(self, self.loaded_invoice))

    def set_check_box_actions(self):
        """ checkbox enable disable """
        self.checkBox_inbox.toggled.connect(self.dateEdit_inbox_date.setEnabled)
        self.checkBox_inbox.toggled.connect(self.pushButton_inbox_date_set_today.setEnabled)
        self.checkBox_checked.toggled.connect(self.dateEdit_checked_date.setEnabled)
        self.checkBox_checked.toggled.connect(self.pushButton_checked_date_set_today.setEnabled)
        self.checkBox_w_VAT.toggled.connect(self.doubleSpinBox_VAT.setEnabled)
        self.checkBox_sd_absolute.toggled.connect(self.doubleSpinBox_safety_deposit_absolute.setEnabled)
        self.checkBox_sd_absolute.toggled.connect(self.doubleSpinBox_safety_deposit.setDisabled)
        self.checkBox_discount.toggled.connect(self.dateEdit_due_date_discount.setEnabled)
        self.checkBox_discount.toggled.connect(self.pushButton_due_date_discount_set_today.setEnabled)
        self.checkBox_discount.toggled.connect(self.pushButton_due_date_discount_set_today.setEnabled)
        self.checkBox_discount.toggled.connect(self.doubleSpinBox_discount.setEnabled)
        self.checkBox_discount.toggled.connect(self.label_due_date_discount.setEnabled)
        """ update ui on click of some widgets """
        self.checkBox_w_VAT.clicked.connect(self.update_ui)
        self.checkBox_cumulative.clicked.connect(self.update_ui)
        self.checkBox_reduce_prev_invoices.clicked.connect(self.update_ui)
        self.checkBox_sd_absolute.clicked.connect(self.update_ui)
        self.checkBox_discount.toggled.connect(self.update_ui)

    def set_spin_box_actions(self):
        """ spinbox update """
        self.doubleSpinBox_rebate.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_reduction_insurance_costs.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_reduction_usage_costs.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_safety_deposit.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_safety_deposit_absolute.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_discount.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_VAT.valueChanged.connect(self.update_ui)

    def set_combo_box_actions(self):
        """ combo box update """
        self.comboBox_company.currentIndexChanged.connect(self.setup_combo_box_jobs)
        """ ok button """
        self.comboBox_company.currentIndexChanged.connect(self.activate_ok_button)
        self.comboBox_job.currentIndexChanged.connect(self.activate_ok_button)
        """ update prev invoices """
        self.comboBox_job.currentIndexChanged.connect(self.update_prev_invoices)
        self.comboBox_job.currentIndexChanged.connect(self.update_ui)

    def set_date_edit_actions(self):
        """ update prev_invoices """
        self.dateEdit_invoice_date.dateChanged.connect(self.update_prev_invoices)
        self.dateEdit_invoice_date.dateChanged.connect(self.update_ui)

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
    def add_new_company(self):
        input_company_args = dlg.open_company_dialog(app_data=self.app_data)
        if input_company_args:
            input_company = self.app_data.project.input_new_company(input_company_args)
            self.setup_combo_boxes()
            self.set_company_to(input_company)
            print(f"New company added: {input_company.name}, {input_company.uid}")

    def add_new_job(self):
        args = self.get_input()
        sel_company = args["company"]
        input_job_args = dlg.open_job_dialog(app_data=self.app_data, sel_company=sel_company)
        if input_job_args:
            input_job = self.app_data.project.input_new_job(input_job_args)
            self.setup_combo_boxes()
            self.set_company_to(input_job.company)
            self.set_job_to(input_job)
            print(f"New job added: {input_job.id}, {input_job.uid}")

    def update_prev_invoices(self):
        args = self.get_input()
        invoice_uid = self.loaded_invoice.uid if self.loaded_invoice else self.tmp_invoice.uid
        invoice_created_date = self.loaded_invoice.uid.created_date if self.loaded_invoice else self.tmp_invoice.uid.created_date
        self.prev_invoices = self.app_data.project.get_prev_invoices(invoice_uid=invoice_uid, company=args["company"], job=args["job"], invoice_date=args["invoice_date"], invoice_created_date=invoice_created_date)

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_company_to(self, company):
        index = self.comboBox_company.findData(company)
        self.comboBox_company.setCurrentIndex(index)
        self.activate_ok_button()

    def set_job_to(self, job):
        index = self.comboBox_job.findData(job)
        self.comboBox_job.setCurrentIndex(index)
        self.activate_ok_button()

    def set_date_today(self):
        self.dateEdit_invoice_date.setDate(QDate.currentDate())
        self.dateEdit_inbox_date.setDate(QDate.currentDate())
        self.dateEdit_checked_date.setDate(QDate.currentDate())
        self.dateEdit_due_date.setDate(QDate.currentDate())
        self.dateEdit_due_date_discount.setDate(QDate.currentDate())

    def uncheck_boxes(self):
        self.checkBox_inbox.setChecked(False)
        self.checkBox_checked.setChecked(False)
        self.checkBox_discount.setChecked(False)

    def set_labels(self, *, amount_w_VAT, amount_VAT_amount, verified_amount_w_VAT, verified_amount_VAT_amount,
                            prev_invoices_count, prev_invoices_amount, rebate_amount, reduction_insurance_costs_amount,
                            reduction_usage_costs_amount, amount_a_reductions_amount, amount_a_reductions_amount_w_VAT,
                            amount_a_reductions_amount_VAT_amount, safety_deposit_amount, approved_amount, discount_amount,
                            approved_amount_a_discount_amount):
        """ amounts """
        self.label_amount_w_VAT.setText(amount_str(amount_w_VAT))
        self.label_amount_VAT_amount.setText(amount_str(amount_VAT_amount))
        self.label_verified_amount_w_VAT.setText(amount_str(verified_amount_w_VAT))
        self.label_verified_amount_VAT_amount.setText(amount_str(verified_amount_VAT_amount))
        """ reductions """
        self.label_prev_invoices_count.setText(prev_invoices_count)
        self.label_prev_invoices_amount.setText(amount_str(prev_invoices_amount))
        self.label_rebate_amount.setText(amount_str(rebate_amount))
        self.label_reduction_insurance_costs_amount.setText(amount_str(reduction_insurance_costs_amount))
        self.label_reduction_usage_costs_amount.setText(amount_str(reduction_usage_costs_amount))
        self.label_amount_a_reductions_amount.setText(amount_str(amount_a_reductions_amount))
        self.label_amount_a_reductions_amount_w_VAT.setText(amount_str(amount_a_reductions_amount_w_VAT))
        self.label_amount_a_reductions_VAT_amount.setText(amount_str(amount_a_reductions_amount_VAT_amount))
        """ approved amount """
        self.label_approved_amount.setText(amount_w_currency_str(approved_amount, self.app_data.project.get_currency()))
        self.label_discount_amount.setText(amount_str(discount_amount))
        self.label_approved_amount_a_discount_amount.setText(amount_w_currency_str(approved_amount_a_discount_amount, self.app_data.project.get_currency()))
        """ safety deposit """
        if not self.checkBox_sd_absolute.isChecked():
            self.doubleSpinBox_safety_deposit_absolute.setValue(safety_deposit_amount)
        else:
            self.doubleSpinBox_safety_deposit.setValue(0)

    def set_input(self, *, _uid=None, id="", VAT=None, cumulative=True, internal_index=0,
                    invoice_date=QDate.currentDate(), inbox_date=QDate.currentDate(),
                    checked_date=QDate.currentDate(), company=None, job=None, amount=0,
                    verified_amount=0, rebate=0, reduction_insurance_costs=0, reduction_usage_costs=0,
                    reduce_prev_invoices=True, safety_deposit=0, _safety_deposit_amount=None, discount=0,
                    due_date=QDate.currentDate(), due_date_discount=QDate.currentDate(), **kwargs):
        """ meta data """
        self.label_uid.setText(_uid.labelize() if _uid else "-")
        w_VAT = True if VAT else False
        VAT = VAT*100 if w_VAT else self.default_vat*100
        self.lineEdit_id.setText(str(id))
        self.doubleSpinBox_VAT.setValue(VAT)
        """ checkboxes """
        self.checkBox_w_VAT.setChecked(w_VAT)
        self.checkBox_cumulative.setChecked(cumulative)
        self.checkBox_reduce_prev_invoices.setChecked(reduce_prev_invoices)
        self.dateEdit_invoice_date.setDate(invoice_date)
        if inbox_date:
            self.checkBox_inbox.setChecked(True)
            self.dateEdit_inbox_date.setDate(inbox_date)
        else:
            self.checkBox_inbox.setChecked(False)
        if checked_date:
            self.checkBox_checked.setChecked(True)
            self.dateEdit_checked_date.setDate(checked_date)
        else:
            self.checkBox_checked.setChecked(False)
        """ company and job """
        if company:
            self.set_company_to(company)
            self.setup_combo_box_jobs()
            if job:
                self.set_job_to(job)
        """ amounts """
        self.lineEdit_amount_1.setText(str(int(amount)) if int(amount)>0 else "")
        self.lineEdit_amount_2.setText(f"{int(rnd(amount-int(amount))*100):02d}" if amount-int(amount)>0 else "")
        self.lineEdit_verified_amount_1.setText(str(int(verified_amount)) if int(verified_amount)>0 else "")
        self.lineEdit_verified_amount_2.setText(f"{int(rnd(verified_amount-int(verified_amount))*100):02d}" if verified_amount-int(verified_amount)>0 else "")
        """ reductions """
        self.doubleSpinBox_rebate.setValue(rebate*100)
        self.doubleSpinBox_reduction_insurance_costs.setValue(reduction_insurance_costs*100)
        self.doubleSpinBox_reduction_usage_costs.setValue(reduction_usage_costs*100)
        if _safety_deposit_amount:
            self.checkBox_sd_absolute.setChecked(True)
            self.doubleSpinBox_safety_deposit.setValue(0)
            self.doubleSpinBox_safety_deposit_absolute.setValue(_safety_deposit_amount)
        else:
            self.checkBox_sd_absolute.setChecked(False)
            self.doubleSpinBox_safety_deposit.setValue(safety_deposit*100)
            self.doubleSpinBox_safety_deposit_absolute.setValue(0)
        self.doubleSpinBox_discount.setValue(discount*100)
        self.dateEdit_due_date.setDate(due_date)
        if due_date_discount:
            self.checkBox_discount.setChecked(True)
            self.dateEdit_due_date_discount.setDate(due_date_discount)
        else:
            self.checkBox_discount.setChecked(False)


    def get_input(self):
        args = {
                "id": self.lineEdit_id.text(),
                "company": self.comboBox_company.currentData(),
                "job": self.comboBox_job.currentData(),
                "cumulative": self.checkBox_cumulative.isChecked(),
                "invoice_date": self.dateEdit_invoice_date.date(),
                "inbox_date": self.dateEdit_inbox_date.date() if self.checkBox_inbox.isChecked() else None,
                "checked_date": self.dateEdit_checked_date.date() if self.checkBox_checked.isChecked() else None,
                "amount": two_inputs_to_float(self.lineEdit_amount_1, self.lineEdit_amount_2),
                "verified_amount": two_inputs_to_float(self.lineEdit_verified_amount_1,self.lineEdit_verified_amount_2),
                "rebate": self.doubleSpinBox_rebate.value()/100,
                "reduction_insurance_costs": self.doubleSpinBox_reduction_insurance_costs.value()/100,
                "reduction_usage_costs": self.doubleSpinBox_reduction_usage_costs.value()/100,
                "reduce_prev_invoices": self.checkBox_reduce_prev_invoices.isChecked(),
                "VAT": self.doubleSpinBox_VAT.value()/100 if self.checkBox_w_VAT.isChecked() else 0,
                "safety_deposit": self.doubleSpinBox_safety_deposit.value()/100 if not(self.checkBox_sd_absolute.isChecked()) else 0,
                "safety_deposit_amount": self.doubleSpinBox_safety_deposit_absolute.value() if self.checkBox_sd_absolute.isChecked() else None,
                "discount": self.doubleSpinBox_discount.value()/100 if self.checkBox_discount.isChecked() else 0,
                "due_date": self.dateEdit_due_date.date(),
                "due_date_discount": self.dateEdit_due_date_discount.date() if self.checkBox_discount.isChecked() else None
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
            self.update()
            args = self.get_input()
            args["prev_invoices"] = self.prev_invoices
            return ok, args
