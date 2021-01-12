"""
#
#   JOB_DLG
#   This module creates an job dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import QDialogButtonBox

from ui import dlg, helper
from ui.helper import two_inputs_to_float, amount_str, amount_w_currency_str, rnd
from core.obj import (proj, corp, arch)

class JobDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, sel_company=None, loaded_job=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.default_vat = app_data.project.get_vat()
        self.currency = app_data.project.get_currency()
        self.jobs = app_data.project.jobs
        self.companies = app_data.project.companies
        self.trades = app_data.project.trades
        self.sel_company = sel_company
        self.loaded_job = loaded_job

        self.paid_safety_deposits = loaded_job.paid_safety_deposits if loaded_job else list()

        self.initialize_ui()
        """ set title """
        dialog_title = "Neuer Auftrag"
        if loaded_job:
            loaded_job_company_name = loaded_job.company.name if loaded_job.company else "-"
            dialog_title = f"Auftrag ({loaded_job_company_name}, {loaded_job.id}) bearbeiten..."
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_widget_actions()
        self.set_button_actions()
        self.set_combo_box_actions()
        self.set_spin_box_actions()
        self.set_event_handler()
        self.set_validators()
        self.set_default_labels()
        self.set_to_max_job_number()
        if self.loaded_job:
            """ dont let the job be another """
            self.deactivate_input()
            """ activate delete button """
            self.pushButton_delete.setEnabled(True)
            """ load job data to input """
            loaded_args = vars(self.loaded_job).copy()
            self.set_input(**loaded_args)

        self.update_ui()
        self.set_paid_safety_deposits(self.paid_safety_deposits)

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/job_dialog.ui', self)
        """ TODO: figure out where to put this """
        tree_view_cols = ["date", "amount"] # maybe put on top of file
        self.treeWidget_paid_safety_deposits.setHeaderLabels([self.app_data.titles[col] for col in tree_view_cols])
        self.treeWidget_safety_deposits_of_invoices.setHeaderLabels([self.app_data.titles[col] for col in tree_view_cols])

    def deactivate_input(self):
        self.comboBox_company.setEnabled(False)
        self.pushButton_add_company.setEnabled(False)
        self.spinBox_id.setEnabled(False)
        self.pushButton_determine_job_nr.setEnabled(False)

    def setup_combo_boxes(self):
        self.setup_company_combo_box()
        if self.sel_company:
            self.set_company_to(self.sel_company)
            self.sel_company = None
        self.setup_trade_combo_box()

    def setup_company_combo_box(self):
        self.comboBox_company.addItem("Firma auswählen...", None)
        for company in self.companies:
            self.comboBox_company.addItem(company.name, company)

    def setup_trade_combo_box(self):
        self.comboBox_trade.addItem("Gewerk auswählen...", None)
        for trade in self.trades:
            self.comboBox_trade.addItem(trade.name, trade)

    def set_default_labels(self):
        pass

    def enable_set_max_job_nr_button(self):
        self.pushButton_determine_job_nr.setEnabled(False)
        args = self.get_input()
        if self.loaded_job is None and args["company"] and args["id"] != self.get_max_job_number():
            self.pushButton_determine_job_nr.setEnabled(True)

    def set_validators(self):
        # to allow only int
        onlyInt = QtGui.QIntValidator()
        self.lineEdit_job_sum_1.setValidator(onlyInt)
        self.lineEdit_job_sum_2.setValidator(onlyInt)

    def activate_psd_buttons(self):
        args = self.get_input()
        if args["company"]:
            self.pushButton_add_paid_safety_deposit.setEnabled(True)
            if self.treeWidget_paid_safety_deposits.currentItem():
                self.pushButton_remove_paid_safety_deposit.setEnabled(True)
            else:
                self.pushButton_remove_paid_safety_deposit.setEnabled(False)
        else:
            self.pushButton_add_paid_safety_deposit.setEnabled(False)
            self.pushButton_remove_paid_safety_deposit.setEnabled(False)

    def activate_ok_button(self):
        args = self.get_input()
        if self.loaded_job is not None or (args["trade"] and args["company"] and not(self.app_data.project.job_exists(id=args["id"], company=args["company"]))):
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def update_ui(self):
        """ update set_max_job_nr button """
        self.enable_set_max_job_nr_button()
        #""" update the values of the labels """#
        args = self.get_input()

        """ job exists """
        if self.loaded_job is None and self.app_data.project.job_exists(id=args["id"], company=args["company"]):
            self.label_job_exists.setText("Auftrag existiert bereits!")
        else:
            self.label_job_exists.setText("")

        tmp_job = arch.ArchJob(**args)
        self.set_labels(job_sum_w_VAT=tmp_job.job_sum*(1+self.default_vat),
            job_sum_VAT_amount=tmp_job.job_sum*self.default_vat,
            cost_group=tmp_job.trade.cost_group if tmp_job.trade else None
            )
        self.set_paid_safety_deposits(self.paid_safety_deposits)
        invoices = self.app_data.project.get_invoices_of_job(self.loaded_job)
        self.set_safety_deposits_of_invoices(invoices)
        self.activate_psd_buttons()
        self.activate_ok_button()

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_widget_actions(self):
        self.treeWidget_safety_deposits_of_invoices.itemDoubleClicked.connect(self.double_click_invoice_tree)
        self.treeWidget_paid_safety_deposits.clicked.connect(self.activate_psd_buttons)

    def set_button_actions(self):
        self.pushButton_determine_job_nr.clicked.connect(self.set_to_max_job_number)
        self.pushButton_add_company.clicked.connect(self.add_new_company)
        self.pushButton_add_trade.clicked.connect(self.add_new_trade)
        self.pushButton_add_paid_safety_deposit.clicked.connect(self.pay_safety_deposit)
        self.pushButton_remove_paid_safety_deposit.clicked.connect(self.button_remove_psd)
        """ delete button """
        self.pushButton_delete.clicked.connect(lambda:helper.delete(self, self.loaded_job))

    def set_combo_box_actions(self):
        # update ui when combobox is activated
        self.comboBox_company.activated.connect(self.update_ui)
        self.comboBox_company.currentIndexChanged.connect(self.set_to_max_job_number)
        self.comboBox_trade.activated.connect(self.update_ui)

    def set_spin_box_actions(self):
        # update the set_max_job_nr_button on change
        self.spinBox_id.valueChanged.connect(self.enable_set_max_job_nr_button)
        self.spinBox_id.valueChanged.connect(self.update_ui)

    def set_event_handler(self):
        self.keyReleaseEvent = self.eventHandler
        self.mouseReleaseEvent = self.eventHandler
    """ add event handler """
    def eventHandler(self, event):
        self.update_ui()

    """
    #
    #   SIGNAL FUNCTIONS
    #   functions to that get connected to the widget signals (some might also be directly used and not in this section)
    #
    """
    def button_remove_psd(self):
        psd = self.treeWidget_paid_safety_deposits.currentItem().data(1, QtCore.Qt.UserRole)
        self.paid_safety_deposits.remove(psd)
        self.update_ui()

    def double_click_invoice_tree(self, item):
        self.edit_invoice(item.data(1, QtCore.Qt.UserRole))

    """
    #
    #   FUNCTIONALITY
    #   Functions that let the dialog do something
    #
    """
    def add_new_company(self):
        input_company_args = dlg.open_company_dialog(self.app_data)
        if input_company_args:
            input_company = self.app_data.project.input_new_company(input_company_args)
            self.setup_combo_boxes()
            self.set_company_to(input_company)
            print(f"New company added: {input_company.name}, {input_company.uid}")

    def add_new_trade(self):
        input_trade_args = dlg.open_trade_dialog(self.app_data)
        if input_trade_args:
            input_trade = self.app_data.project.input_new_trade(input_trade_args)
            self.setup_combo_boxes()
            self.set_trade_to(input_trade)
            print(f"New trade added: {input_trade.name}, {input_trade.uid}")

    def pay_safety_deposit(self):
        paid_safety_deposit_args = dlg.open_pay_safety_deposit_dialog()
        if paid_safety_deposit_args:
            self.paid_safety_deposits.append(paid_safety_deposit_args)
        self.update_ui()

    def edit_invoice(self, invoice):
        invoice = helper.edit_invoice(self.app_data, invoice)
        self.update_ui()

    """
    #
    #   RENDER VIEWS
    #   functions to render the objects to the respective widgets
    #
    """
    def set_safety_deposits_of_invoices(self, invoices):
        self.treeWidget_safety_deposits_of_invoices.clear()
        sd_sum = 0
        for invoice in invoices:
            helper.add_item_to_tree(content_item=invoice,
                                    parent=self.treeWidget_safety_deposits_of_invoices,
                                    cols=[str(invoice.invoice_date.toPyDate()), amount_w_currency_str(invoice.safety_deposit_amount, self.currency)])
            sd_sum += invoice.safety_deposit_amount
        self.label_safety_deposits_of_invoices_sum.setText(amount_str(sd_sum))

    def set_paid_safety_deposits(self, paid_safety_deposits):
        self.treeWidget_paid_safety_deposits.clear()
        psd_sum = 0
        for psd in paid_safety_deposits:
            helper.add_item_to_tree(content_item=psd,
                                    parent=self.treeWidget_paid_safety_deposits,
                                    cols=[str(psd["date"]), amount_w_currency_str(psd["amount"], self.currency)])
            psd_sum += psd["amount"]
        self.label_paid_safety_deposits_sum.setText(amount_str(psd_sum))

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_to_max_job_number(self):
        self.set_job_id_to(self.get_max_job_number())

    def get_max_job_number(self):
        company = self.comboBox_company.currentData()
        max_job_nr = max([job.id for job in self.app_data.project.jobs if job.company is company]+[0])
        return max_job_nr+1

    def set_job_id_to(self, id):
        self.spinBox_id.setValue(id)

    def set_company_to(self, company):
        index = self.comboBox_company.findData(company)
        self.comboBox_company.setCurrentIndex(index)

    def set_trade_to(self, trade):
        index = self.comboBox_trade.findData(trade)
        self.comboBox_trade.setCurrentIndex(index)

    def set_labels(self, *, job_sum_w_VAT, job_sum_VAT_amount, cost_group):
        """ amounts """
        self.label_job_sum_w_VAT.setText(amount_str(job_sum_w_VAT))
        self.label_job_sum_VAT_amount.setText(amount_str(job_sum_VAT_amount))
        """ KG """
        cost_group = str(cost_group.id) if cost_group else "-"
        self.label_cost_group_2.setText(cost_group)

    """ set input fields """
    def set_input(self, *, _uid="-", company=None, id=0, trade=None, job_sum=0, **kwargs):
        """ combo boxes first, since they might trigger updates """
        if company:
            self.set_company_to(company)
        if trade:
            self.set_trade_to(trade)
        """ data """
        self.set_job_id_to(id)
        self.label_uid.setText(_uid.labelize())
        """ amounts """
        self.lineEdit_job_sum_1.setText(str(int(job_sum)) if int(job_sum)>0 else "")
        self.lineEdit_job_sum_2.setText(f"{int(rnd(job_sum-int(job_sum))*100):02d}" if job_sum-int(job_sum)>0 else "")

    def get_input(self):
        args = {
                "id": self.spinBox_id.value(),
                "company": self.comboBox_company.currentData(),
                "trade": self.comboBox_trade.currentData(),
                "job_sum": two_inputs_to_float(self.lineEdit_job_sum_1, self.lineEdit_job_sum_2),
                "paid_safety_deposits": self.paid_safety_deposits
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
