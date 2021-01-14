"""
#
#   Main window
#
#
"""
import debug

import os
import datetime

import json, uuid

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import (QDialog, QInputDialog, QFileDialog, QGraphicsColorizeEffect)
from PyQt5.QtCore import QEvent, QDate, QPropertyAnimation
from ui import customqt

from core.obj import (proj, corp, arch)
from ui import dlg, helper
from ui.helper import rnd, amount_str, amount_w_currency_str, percent_str, percent_str_w_sign, qdate_to_str

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_data):
        super().__init__()

        self.app_data = app_data

        """
        #
        #   COLUMNS OF TABLE VIEWS
        #   TODO: load these from external file
        #
        """
        self.cost_stand_cols = [
            {"title": "cost_group", "width": 130},
            {"title": "project_budget", "width": 130},
            {"title": "project_budget_w_VAT", "width": 130},
            {"title": "trade_budget", "width": 130},
            {"title": "trade_budget_w_VAT", "width": 130},
            {"title": "difference_proj_to_trades_budget", "width": 230},
            {"title": "job_sums", "width": 130},
            {"title": "job_sums_w_VAT", "width": 130},
            {"title": "approved_invoices_w_VAT", "width": 150},
            {"title": "approved_invoices_w_VAT_by_tradebudgets", "width": 150},
            ]

        self.invoice_cols = [
            {"title": "id", "width": 150},
            #{"title": "internal_index", "width": 100},
            #{"title": "cumulative", "width": 100},
            {"title": "company", "width": 120},
            {"title": "job", "width": 60},
            {"title": "invoice_date", "width": 100},
            {"title": "inbox_date", "width": 95},
            {"title": "checked_date", "width": 95},
            {"title": "trade", "width": 105},
            {"title": "cost_group", "width": 90},
            #{"title": "amount", "width": 100},
            #{"title": "verified_amount", "width": 100},
            #{"title": "rebate", "width": 100},
            #{"title": "reduction_insurance_costs", "width": 100},
            #{"title": "reduction_usage_costs", "width": 100},
            #{"title": "prev_invoices", "width": 100},
            #{"title": "VAT", "width": 100},
            #{"title": "safety_deposit", "width": 100},
            #{"title": "discount", "width": 100},
        ]
        self.job_cols = [
            {"title": "id", "width": 80},
            {"title": "company", "width": 200},
            {"title": "job_sum", "width": 200},
            {"title": "job_sum_w_additions", "width": 200},
            #{"title": "job_additions", "width": 100},
            #{"title": "paid_safety_deposits", "width": 100},
            {"title": "trade", "width": 100},
        ]
        self.company_cols = [
            {"title": "name", "width": 200},
            {"title": "service", "width": 120},
            {"title": "service_type", "width": 120},
            {"title": "budget", "width": 120},
            {"title": "contact_person", "width": 100},
        ]
        self.trade_cols = [
            {"title": "name", "width": 150},
            {"title": "cost_group", "width": 90},
            {"title": "budget", "width": 120},
            {"title": "comment", "width": 100},
        ]
        self.cost_group_cols = [
            {"title": "id", "width": 80},
            {"title": "name", "width": 180},
            {"title": "description", "width": 180},
            {"title": "budget", "width": 120},
        ]
        self.person_cols = [
            {"title": "first_name", "width": 150},
            {"title": "last_name", "width": 150},
            #{"title": "address", "width": 180},
            {"title": "telephone", "width": 150},
            #{"title": "fax", "width": 150},
            {"title": "mobile", "width": 150},
            {"title": "email", "width": 150},
            {"title": "company", "width": 150}
        ]

        self.initialize_ui()
        self.center_window()
        self.set_button_actions()
        self.load_widget_signals()
        self.load_action_signals()

        if self.app_data.project is None:
            self.disable_ui()

    @property
    def currency(self):
        return self.app_data.project.get_currency() if self.app_data.project_loaded() else self.app_data.get_currency()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/mainwindow.ui', self) # Load the .ui file
        self.initialize_tabwidget()
        self.init_tree_widget_columns()

    def initialize_tabwidget(self):
        self.tabWidget_content.clear()
        self.tabWidget_content.setTabBar(customqt.TabBar(self))
        self.tabWidget_content.setTabPosition(QtWidgets.QTabWidget.West)
        #self.tabWidget_content.addTab(self.tab_overview, "Übersicht")
        self.tabWidget_content.addTab(self.tab_cost_stand, "Kostenstand")
        self.tabWidget_content.addTab(self.tab_invoice_table, "Rechnungen")
        self.tabWidget_content.addTab(self.tab_jobs_table, "Aufträge")
        self.tabWidget_content.addTab(self.tab_companies_table, "Firmen")
        self.tabWidget_content.addTab(self.tab_trades_table, "Gewerke")
        self.tabWidget_content.addTab(self.tab_cost_groups_table, "Kostengruppen")
        self.tabWidget_content.addTab(self.tab_people, "Beteiligten")
        #self.tabWidget_content.addTab(self.tab_invoice_check, "???")

    def init_column_width(self):
        self.render_cost_stand(set_width=True)
        self.render_invoice_view(set_width=True)
        self.render_job_view(set_width=True)
        self.render_company_view(set_width=True)
        self.render_trades(set_width=True)
        self.render_cost_groups(set_width=True)
        self.render_people(set_width=True)

    def init_tree_widget_columns(self):
        """ TODO: figure out where to put this """
        company_tree_view_cols = ["job", "invoice", "verified_amount"] # maybe put on top of file
        self.treeWidget_company_invoices_by_job.setHeaderLabels([self.app_data.titles[col] for col in company_tree_view_cols])
        job_tree_view_cols = ["date", "id", "safety_deposit_amount", "verified_amount"] # maybe put on top of file
        self.treeWidget_invoices_of_curr_job.setHeaderLabels([self.app_data.titles[col] for col in job_tree_view_cols])
        paid_safety_deposits_cols = ["date", "amount", "comment"]
        self.treeWidget_paid_safety_desposits.setHeaderLabels([self.app_data.titles[col] for col in paid_safety_deposits_cols])
        job_additions_cols = ["date", "amount", "comment"]
        self.treeWidget_job_additions.setHeaderLabels([self.app_data.titles[col] for col in job_additions_cols])


    def enable_ui(self):
        self.centralwidget.setEnabled(True)
        self.menuProjekt.setEnabled(True)

    def disable_ui(self):
        self.centralwidget.setEnabled(False)
        self.menuProjekt.setEnabled(False)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_ui(self):
        if self.app_data.project:
            self.enable_ui()

            self.update_labels()
            #update views
            self.render_cost_stand()
            self.render_invoice_view()
            self.render_job_view()
            self.render_company_view()
            self.render_trades()
            self.render_cost_groups()
            self.render_people()

    def update_labels(self):
        self.label_cur_proj.setText(self.app_data.project.identifier)
        self.label_cur_proj_construction_scheme.setText(self.app_data.project.construction_scheme)
        """ currency """
        currency_labels = [label for label in self.findChildren(QtWidgets.QLabel) if "label_currency_" in label.objectName()]
        for label in currency_labels:
            label.setText(self.currency)

    """
    #
    #   MANIPULATE GUI
    #   Maximize/minimize areas...
    #
    """

    # this function is probably not needed
    def minimize_invoice_info(self):
        print("this should minimize the invoice info widget")
        #self.horizontalLayout_invoice_info_top.setVisible(False)
        #self.verticalLayout_12.addWidget(self.horizontalLayout_invoice_info_top)


    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        """ quick links """
        self.pushButton_quick_new_invoice.clicked.connect(lambda:self.input_invoice_to_project())
        self.pushButton_quick_new_job.clicked.connect(lambda:self.input_job_to_project())
        self.pushButton_quick_invoice_check_dir.clicked.connect(lambda:self.app_data.open_invoice_check_dir())
        self.pushButton_quick_syp_dir.clicked.connect(lambda:self.app_data.open_syp_dir())
        self.pushButton_quick_proj_dir.clicked.connect(lambda:self.app_data.open_project_dir())

        """ invoice buttons """
        self.pushButton_new_invoice.clicked.connect(self.input_invoice_to_project)
        self.pushButton_edit_invoice.clicked.connect(self.button_edit_invoice)
        self.pushButton_invoice_check.clicked.connect(self.button_invoice_check)
        self.pushButton_go_to_job.clicked.connect(self.set_job_view_sel_invoice)

        """ job buttons """
        self.pushButton_new_job.clicked.connect(lambda:self.input_job_to_project())
        self.pushButton_edit_job.clicked.connect(self.button_edit_job)
        self.pushButton_add_invoice_for_curr_job.clicked.connect(self.button_input_invoice_w_curr_job)
        self.pushButton_pay_safety_deposit.clicked.connect(self.button_pay_safety_deposit)
        self.pushButton_remove_safety_deposit.clicked.connect(self.button_remove_psd)
        self.pushButton_add_job_addition.clicked.connect(self.button_add_job_addition)
        self.pushButton_remove_job_addition.clicked.connect(self.button_remove_job_addition)
        """ company buttons """
        self.pushButton_new_company.clicked.connect(lambda:self.input_company_to_project())
        self.pushButton_edit_company.clicked.connect(self.button_edit_company)
        """ trade buttons """
        self.pushButton_new_trade.clicked.connect(lambda:self.input_trade_to_project())
        self.pushButton_edit_trade.clicked.connect(self.button_edit_trade)
        """ cost_group buttons """
        self.pushButton_new_cost_group.clicked.connect(lambda:self.input_cost_group_to_project())
        self.pushButton_edit_cost_group.clicked.connect(self.button_edit_cost_group)
        """ person buttons """
        self.pushButton_edit_person.clicked.connect(self.button_edit_person)

    def load_widget_signals(self):
        """ invoice signals """
        self.listWidget_invoices.itemDoubleClicked.connect(self.double_click_invoice)
        self.tableWidget_invoices.itemDoubleClicked.connect(self.double_click_invoice)
        self.tableWidget_invoices.itemClicked.connect(self.click_invoice)
        """ job signals """
        self.tableWidget_jobs.itemDoubleClicked.connect(self.double_click_job)
        self.tableWidget_jobs.itemClicked.connect(self.click_job)
        self.treeWidget_invoices_of_curr_job.itemDoubleClicked.connect(self.double_click_invoice_tree)
        self.treeWidget_paid_safety_desposits.itemClicked.connect(self.activate_job_buttons)
        self.treeWidget_job_additions.itemClicked.connect(self.activate_job_buttons)
        """ company signals """
        self.tableWidget_companies.itemDoubleClicked.connect(self.double_click_company)
        self.tableWidget_companies.itemClicked.connect(self.click_company)
        """ trade signals """
        self.tableWidget_trades.itemDoubleClicked.connect(self.double_click_trade)
        self.tableWidget_trades.itemClicked.connect(self.click_trade)
        """ cost_group signals """
        self.tableWidget_cost_groups.itemDoubleClicked.connect(self.double_click_cost_group)
        self.tableWidget_cost_groups.itemClicked.connect(self.click_cost_group)
        """ people signals """
        self.tableWidget_people.itemDoubleClicked.connect(self.double_click_person)
        self.tableWidget_people.itemClicked.connect(self.click_person)


    def load_action_signals(self):
        self.actionNewProject.triggered.connect(lambda:self.input_new_project())
        self.actionNewInvoice.triggered.connect(lambda:self.input_invoice_to_project())
        self.actionNewJob.triggered.connect(lambda:self.input_job_to_project())
        self.actionOpenProject.triggered.connect(lambda:self.load_project())
        self.actionSave.triggered.connect(lambda:self.save_project())
        self.actionSaveAs.triggered.connect(lambda:self.save_project_as())
        self.actionEditAppConfig.triggered.connect(lambda:self.edit_app_config())
        self.actionEditProj.triggered.connect(lambda:self.edit_project())
        self.actionEditProjConfig.triggered.connect(lambda:self.edit_proj_config())
        self.actionOpenInvoiceCheckDir.triggered.connect(lambda:self.app_data.open_invoice_check_dir())
        self.actionOpenSYPDir.triggered.connect(lambda:self.app_data.open_syp_dir())
        self.actionOpenProjectDir.triggered.connect(lambda:self.app_data.open_project_dir())
        """ EXPORT """
        self.actionExportAllCompanies.triggered.connect(self.export_companies)
        self.actionExportAllTrades.triggered.connect(self.export_trades)
        self.actionExportAllCostGroups.triggered.connect(self.export_cost_groups)
        """ IMPORT """
        self.actionImportCompanies.triggered.connect(self.import_companies)
        self.actionImportTrades.triggered.connect(self.import_trades)
        self.actionImportCostGroups.triggered.connect(self.import_cost_groups)

    """
    #
    #   SIGNAL FUNCTIONS
    #   functions to that get connected to the widget signals (some might also be directly used and not in this section)
    #
    """
    """ signal
    #
    #   INVOICE
    #
    """
    def double_click_invoice(self, item):
        self.edit_invoice(item.data(1))

    def double_click_invoice_tree(self, item):
        self.edit_invoice(item.data(1, QtCore.Qt.UserRole))

    def click_invoice(self, item):
        invoice = item.data(1)
        self.render_invoice_info(invoice)

    def button_edit_invoice(self):
        item = self.tableWidget_invoices.currentItem()
        if item:
            self.edit_invoice(item.data(1))
        else:
            debug.log_warning("Couldn't edit invoice, no invoice selected!")

    def button_invoice_check(self):
        item = self.tableWidget_invoices.currentItem()
        if item:
            self.invoice_check(item.data(1))
        else:
            debug.log_warning("Couldn't create invoice check, no invoice selected!")

    """ signal
    #
    #   JOB
    #
    """
    def double_click_job(self, item):
        self.edit_job(item.data(1))

    def click_job(self, item):
        job = item.data(1)
        self.render_job_info(job)

    def button_edit_job(self):
        if self.tableWidget_jobs.currentItem():
            self.edit_job(self.tableWidget_jobs.currentItem().data(1))
        else:
            raise Exception("No job selected!")

    def button_input_invoice_w_curr_job(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            self.input_invoice_to_project(sel_job=sel_job)
        else:
            raise Exception("No job selected!")

    def button_pay_safety_deposit(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            helper.pay_safety_deposit(sel_job)
            self.render_job_info(sel_job)
            self.update_ui()
        else:
            raise Exception("No job selected!")

    def button_remove_psd(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            psd_items = self.treeWidget_paid_safety_desposits.selectedItems()
            if psd_items:
                reply = helper.delete_prompt(self)
                if reply:
                    sel_psd = psd_items[0].data(1, QtCore.Qt.UserRole)
                    sel_job.remove_psd(sel_psd)
                    self.render_job_info(sel_job)
                    self.update_ui()
            else:
                raise Exception("No paid_safety_deposit selected!")

        else:
            raise Exception("No job selected!")

    def button_add_job_addition(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            helper.add_job_addition(sel_job)
            self.render_job_info(sel_job)
            self.update_ui()
        else:
            raise Exception("No job selected!")

    def button_remove_job_addition(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            job_addition_items = self.treeWidget_job_additions.selectedItems()
            if job_addition_items:
                reply = helper.delete_prompt(self)
                if reply:
                    sel_job_addition = job_addition_items[0].data(1, QtCore.Qt.UserRole)
                    sel_job.remove_job_addition(sel_job_addition)
                    self.render_job_info(sel_job)
                    self.update_ui()
            else:
                raise Exception("No job_addition selected!")

        else:
            raise Exception("No job selected!")

    """ signal
    #
    #   COMPANY
    #
    """
    def double_click_company(self, item):
        self.edit_company(item.data(1))

    def click_company(self, item):
        company = item.data(1)
        self.render_company_info(company)

    def button_edit_company(self):
        if self.tableWidget_companies.currentItem():
            self.edit_company(self.tableWidget_companies.currentItem().data(1))
        else:
            raise Exception("No company selected!")

    """ signal
    #
    #   TRADE
    #
    """
    def double_click_trade(self, item):
        self.edit_trade(item.data(1))

    def click_trade(self, item):
        trade = item.data(1)
        self.render_trade_info(trade)

    def button_edit_trade(self):
        if self.tableWidget_trades.currentItem():
            self.edit_trade(self.tableWidget_trades.currentItem().data(1))
        else:
            raise Exception("No trade selected!")

    """ signal
    #
    #  COST GROUP
    #
    """
    def double_click_cost_group(self, item):
        self.edit_cost_group(item.data(1))

    def click_cost_group(self, item):
        cost_group = item.data(1)
        self.render_cost_group_info(cost_group)

    def button_edit_cost_group(self):
        if self.tableWidget_cost_groups.currentItem():
            self.edit_cost_group(self.tableWidget_cost_groups.currentItem().data(1))
        else:
            raise Exception("No cost_group selected!")

    """ signal
    #
    #  PERSON
    #
    """
    def double_click_person(self, item):
        self.edit_person(item.data(1))

    def click_person(self, item):
        person = item.data(1)
        self.render_person_info(person)

    def button_edit_person(self):
        if self.tableWidget_people.currentItem():
            self.edit_person(self.tableWidget_people.currentItem().data(1))
        else:
            raise Exception("No person selected!")

    """
    #
    #   RENDER VIEWS
    #   functions to render the objects to the respective widgets
    #
    """
    """ render
    #
    #   COST STAND-TAB
    #
    """
    def render_cost_stand(self, set_width=False):
        # disable sorting when filling the table (to avoid bugs with data field)
        self.tableWidget_cost_stand.setSortingEnabled(False)
        """
        #   Number of rows is number of cost_groups plus one summary row
        """
        self.tableWidget_cost_stand.setRowCount(len(self.app_data.project.cost_groups)+1)
        """
        #   Set columns of table to the list self.invoice_cols
        """
        self.tableWidget_cost_stand.setColumnCount(len(self.cost_stand_cols))
        if set_width:
            for i in range(len(self.cost_stand_cols)):
                self.tableWidget_cost_stand.setColumnWidth(i, self.cost_stand_cols[i]["width"])
        """
        #   Set column titles
        """
        self.tableWidget_cost_stand.setHorizontalHeaderLabels([self.app_data.titles[col["title"]] for col in self.cost_stand_cols])
        """
        #   Set title height
        """
        self.tableWidget_cost_stand.horizontalHeader().setFixedHeight(100)
        """
        #   Render cost_group to the table
        """
        row = 0
        for cost_group in self.app_data.project.main_cost_groups:
            self.add_cost_group_to_table(cost_group, row)
            row += 1
        """
        #   Write summary line
        """
        vat = self.app_data.project.get_vat()
        cost_group_budget_total = sum(cost_group.budget for cost_group in self.app_data.project.main_cost_groups)
        trade_budget_total = sum(trade.budget for trade in self.app_data.project.trades)
        job_sums_total = sum(job.job_sum for job in self.app_data.project.jobs)
        approved_invoices_w_VAT_total = sum(invoice.approved_amount_a_discount_amount for invoice in self.app_data.project.invoices)
        cost_group_total = {
            "cost_group": self.app_data.titles["total"],
            "project_budget": amount_w_currency_str(cost_group_budget_total, self.currency),
            "project_budget_w_VAT":  amount_w_currency_str(cost_group_budget_total * (1+vat), self.currency),
            "trade_budget": amount_w_currency_str(trade_budget_total, self.currency),
            "trade_budget_w_VAT": amount_w_currency_str(trade_budget_total * (1+vat), self.currency),
            "difference_proj_to_trades_budget": amount_w_currency_str(cost_group_budget_total - trade_budget_total, self.currency),
            "job_sums": amount_w_currency_str(job_sums_total, self.currency),
            "job_sums_w_VAT": amount_w_currency_str(job_sums_total * (1+vat), self.currency),
            "approved_invoices_w_VAT": amount_w_currency_str(approved_invoices_w_VAT_total, self.currency),
            "approved_invoices_w_VAT_by_tradebudgets": percent_str_w_sign(approved_invoices_w_VAT_total / (trade_budget_total * (1+vat))) if trade_budget_total else "-"
        }
        col = 0
        font = QtGui.QFont()
        font.setBold(True)
        for attr in self.cost_stand_cols:
            table_item = QtWidgets.QTableWidgetItem(str(cost_group_total[attr["title"]]))
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFont(font)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand.setItem(row, col, table_item)
            col += 1

        self.tableWidget_cost_stand.setSortingEnabled(True) # enable sorting once the table is filled


    def add_cost_group_to_table(self, cost_group, row):
        """ Calculate values """
        vat = self.app_data.project.get_vat()
        trade_budget = sum([trade.budget for trade in self.app_data.project.trades if trade.cost_group is cost_group])
        job_sums = sum([job.job_sum for job in self.app_data.project.jobs if job.trade and job.trade.cost_group and job.trade.cost_group is cost_group])
        approved_invoices_w_VAT = sum([invoice.approved_amount_a_discount_amount for invoice in self.app_data.project.invoices if  invoice.job and  invoice.job.trade and invoice.job.trade.cost_group and invoice.job.trade.cost_group is cost_group])
        """ Create output dictionary """
        cost_group_attr = {
            "cost_group":  cost_group.id,
            "project_budget": amount_w_currency_str(cost_group.budget, self.currency),
            "project_budget_w_VAT":  amount_w_currency_str(cost_group.budget * (1+vat), self.currency),
            "trade_budget": amount_w_currency_str(trade_budget, self.currency),
            "trade_budget_w_VAT": amount_w_currency_str(trade_budget * (1+vat), self.currency),
            "difference_proj_to_trades_budget": amount_w_currency_str(cost_group.budget - trade_budget, self.currency),
            "job_sums": amount_w_currency_str(job_sums, self.currency),
            "job_sums_w_VAT": amount_w_currency_str(job_sums * (1+vat), self.currency),
            "approved_invoices_w_VAT": amount_w_currency_str(approved_invoices_w_VAT, self.currency),
            "approved_invoices_w_VAT_by_tradebudgets": percent_str_w_sign(approved_invoices_w_VAT / (trade_budget * (1+vat))) if trade_budget else "-"
        }

        col = 0
        for attr in self.cost_stand_cols:
            table_item = QtWidgets.QTableWidgetItem(str(cost_group_attr[attr["title"]]))
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand.setItem(row, col, table_item)
            col += 1

    """ render
    #
    #   INVOICES-TAB
    #
    """
    """
    #   render_invoice_view
    #   This functions renders the table of the invoice tab
    """
    def render_invoice_view(self, set_width=False):
        self.activate_invoice_buttons()
        date_cols = ["invoice_date", "inbox_date", "checked_date"]
        helper.render_to_table(content=self.app_data.project.invoices,
                                table=self.tableWidget_invoices,
                                cols=self.invoice_cols,
                                titles=self.app_data.titles,
                                date_cols=date_cols,
                                set_width=set_width)
        item = self.tableWidget_invoices.currentItem()
        if item:
            curr_invoice = item.data(1)
            self.render_invoice_info(curr_invoice)

    """
    #   render_invoice_info
    #   This functions renders the right info panel of the selected invoice
    """
    def render_invoice_info(self, invoice):
        if invoice.is_not_deleted():
            args = vars(invoice).copy()
            self.set_invoice_info(**args,
                                amount_w_VAT=invoice.amount_w_VAT,
                                amount_VAT_amount=invoice.amount_VAT_amount,
                                verified_amount_w_VAT=invoice.verified_amount_w_VAT,
                                verified_amount_VAT_amount=invoice.verified_amount_VAT_amount,
                                prev_invoices_count=str(len(invoice.prev_invoices)),
                                prev_invoices_amount=invoice.prev_invoices_amount,
                                rebate_amount=invoice.rebate_amount,
                                reduction_insurance_costs_amount=invoice.reduction_insurance_costs_amount,
                                reduction_usage_costs_amount=invoice.reduction_usage_costs_amount,
                                amount_a_reductions_amount=invoice.amount_a_reductions_amount,
                                amount_a_reductions_amount_w_VAT=invoice.amount_a_reductions_amount_w_VAT,
                                amount_a_reductions_amount_VAT_amount=invoice.amount_a_reductions_amount_VAT_amount,
                                safety_deposit_amount=invoice.safety_deposit_amount,
                                approved_amount=invoice.approved_amount,
                                discount_amount=invoice.discount_amount,
                                approved_amount_a_discount_amount=invoice.approved_amount_a_discount_amount)
            self.activate_invoice_buttons()
        else:
            self.reset_invoice_info()

    """
    #   activate_invoice_buttons
    #   This functions checks, if an invoice is selected or not
    #   and activates or deactivates the buttons of the right info panel
    """
    def activate_invoice_buttons(self):
        if self.tableWidget_invoices.currentItem() and self.tableWidget_invoices.currentItem().data(1).is_not_deleted():
            self.pushButton_go_to_job.setEnabled(True)
            self.pushButton_invoice_check.setEnabled(True)
            self.pushButton_edit_invoice.setEnabled(True)
        else:
            self.pushButton_go_to_job.setEnabled(False)
            self.pushButton_invoice_check.setEnabled(False)
            self.pushButton_edit_invoice.setEnabled(False)

    def reset_invoice_info(self):
        self.set_invoice_info()
        self.activate_invoice_buttons()

    def set_invoice_info(self, *, _uid=None, id="-", VAT=None, cumulative=True,
                    invoice_date=None, inbox_date=None,
                    checked_date=None, company=None, job=None, amount=0,
                    verified_amount=0, rebate=0, reduction_insurance_costs=0, reduction_usage_costs=0,
                    safety_deposit=0, discount=0,
                    amount_w_VAT=0, amount_VAT_amount=0, verified_amount_w_VAT=0, verified_amount_VAT_amount=0,
                    prev_invoices_count="-", prev_invoices_amount=0, rebate_amount=0, reduction_insurance_costs_amount=0,
                    reduction_usage_costs_amount=0, amount_a_reductions_amount=0, amount_a_reductions_amount_w_VAT=0,
                    amount_a_reductions_amount_VAT_amount=0, safety_deposit_amount=0, approved_amount=0, discount_amount=0,
                    approved_amount_a_discount_amount=0, **kwargs):
        """ LABELS """
        """ uid """
        self.label_invoice_uid.setText(_uid.labelize() if _uid else "-")
        """ id """
        self.label_invoice_id.setText(str(id))
        """ VAT """
        w_VAT = True if VAT else False
        VAT = percent_str_w_sign(VAT*100) if w_VAT else "-"
        self.label_invoice_VAT.setText(VAT)
        """ cumulative """
        f = self.label_cumulative.font()
        if not(cumulative):
            f.setStrikeOut(True)
            self.label_cumulative.setFont(f)
        else:
            f.setStrikeOut(False)
            self.label_cumulative.setFont(f)
        """ company and job """
        self.label_company_2.setText(company.name if company else "-")
        self.label_job_2.setText(str(job.id) if job else "-")
        """ dates """
        self.label_invoice_date_2.setText(qdate_to_str(invoice_date) if invoice_date else "-")
        self.label_inbox_date_2.setText(qdate_to_str(inbox_date) if inbox_date else "-")
        self.label_checked_date_2.setText(qdate_to_str(checked_date) if checked_date else "-")
        """ amounts """
        self.label_amount.setText(amount_str(amount))
        self.label_amount_w_VAT.setText(amount_str(amount_w_VAT))
        self.label_amount_VAT_amount.setText(amount_str(amount_VAT_amount))
        self.label_verified_amount.setText(amount_str(verified_amount))
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
        self.label_safety_deposit_amount.setText(amount_str(safety_deposit_amount))
        self.label_approved_amount.setText(amount_w_currency_str(approved_amount, self.currency))
        self.label_discount_amount.setText(amount_str(discount_amount))
        self.label_approved_amount_a_discount_amount.setText(amount_w_currency_str(approved_amount_a_discount_amount, self.currency))
        """ reductions """
        self.label_rebate_2.setText(percent_str_w_sign(rebate*100))
        self.label_reduction_insurance_costs_2.setText(percent_str_w_sign(reduction_insurance_costs*100))
        self.label_reduction_usage_costs_2.setText(percent_str_w_sign(reduction_usage_costs*100))
        self.label_safety_deposit_2.setText(percent_str_w_sign(safety_deposit*100))
        self.label_discount_2.setText(percent_str_w_sign(discount*100))

    """ render
    #
    #   JOBS-TAB
    #
    """
    def render_job_view(self, set_width=False):
        self.activate_job_buttons()
        amount_cols = ["job_sum", "job_sum_w_additions"]
        helper.render_to_table(content=self.app_data.project.jobs,
                                table=self.tableWidget_jobs,
                                cols=self.job_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                currency=self.currency,
                                set_width=set_width)
        item = self.tableWidget_jobs.currentItem()
        if item:
            curr_job = item.data(1)
            self.render_job_info(curr_job)

    def render_job_info(self, job):
        if job.is_not_deleted():
            args = vars(job).copy()
            invoices_of_job = self.app_data.project.get_invoices_of_job(job)
            """
            #
            #   Invoices have their own vat. Hence we have to calculate the sum_w_VAT and VAT_amount
            #   summing up again and not using a common vat factor.
            #
            """
            verified_sum = sum([invoice.verified_amount for invoice in invoices_of_job])
            verified_sum_w_VAT = sum([invoice.verified_amount_w_VAT for invoice in invoices_of_job])
            verified_sum_VAT_amount = sum([invoice.verified_amount_VAT_amount for invoice in invoices_of_job])

            safety_deposits_sum = sum([invoice.safety_deposit_amount for invoice in invoices_of_job])
            paid_safety_deposits_sum = job.paid_safety_deposits_sum

            self.set_job_data(**args,
                                job_sum_w_additions=job.job_sum_w_additions,
                                verified_sum_w_VAT=verified_sum_w_VAT,
                                safety_deposits_sum=safety_deposits_sum,
                                paid_safety_deposits_sum=paid_safety_deposits_sum)
            self.set_verified_sum_info(verified_sum, verified_sum_w_VAT, verified_sum_VAT_amount)
            self.set_paid_safety_deposits_of_job(paid_safety_deposits=job.paid_safety_deposits)
            self.set_job_additions_of_job(job_additions=job.job_additions)
            self.set_invoices_of_job(invoices_of_job=invoices_of_job)
            self.activate_job_buttons()
        else:
            self.reset_job_info()

    def activate_job_buttons(self):
        if self.tableWidget_jobs.currentItem():
            self.pushButton_edit_job.setEnabled(True)
            self.pushButton_add_invoice_for_curr_job.setEnabled(True)
            """ paid safety deposits """
            self.pushButton_pay_safety_deposit.setEnabled(True)
            if self.treeWidget_paid_safety_desposits.selectedItems():
                self.pushButton_remove_safety_deposit.setEnabled(True)
            else:
                self.pushButton_remove_safety_deposit.setEnabled(False)
            """ job additions """
            self.pushButton_add_job_addition.setEnabled(True)
            if self.treeWidget_job_additions.selectedItems():
                self.pushButton_remove_job_addition.setEnabled(True)
            else:
                self.pushButton_remove_job_addition.setEnabled(False)
        else:
            self.pushButton_edit_job.setEnabled(False)
            self.pushButton_add_invoice_for_curr_job.setEnabled(False)
            self.pushButton_pay_safety_deposit.setEnabled(False)
            self.pushButton_remove_safety_deposit.setEnabled(False)
            self.pushButton_add_job_addition.setEnabled(False)
            self.pushButton_remove_job_addition.setEnabled(False)

    def reset_job_info(self):
        self.set_job_data()
        self.set_verified_sum_info()
        self.treeWidget_invoices_of_curr_job.clear()
        self.activate_job_buttons()

    def set_job_data(self, *, _uid=None, company=None, id="-", trade=None, job_sum=0, job_sum_w_additions=0,
                        verified_sum_w_VAT=0, safety_deposits_sum=0, paid_safety_deposits_sum=0,
                        **kwargs):
        company_name = company.name if company else "-"
        self.label_job_company.setText(company_name)
        trade_name = trade.name if trade else "-"
        self.label_job_trade.setText(trade_name)
        self.label_job_id.setText(str(id))
        """ data """
        self.label_job_uid.setText(_uid.labelize() if _uid else "-")
        """ job_sum initial """
        job_sum_VAT_amount = job_sum * self.app_data.project.get_vat()
        job_sum_w_VAT = job_sum + job_sum_VAT_amount
        self.label_job_job_sum.setText(amount_str(job_sum))
        self.label_job_sum_w_VAT.setText(amount_str(job_sum_w_VAT))
        self.label_job_sum_VAT_amount.setText(amount_str(job_sum_VAT_amount))
        """ job_sum w job_additions """
        job_sum_w_additions_VAT_amount = job_sum_w_additions * self.app_data.project.get_vat()
        job_sum_w_additions_w_VAT = job_sum_w_additions + job_sum_w_additions_VAT_amount
        self.label_job_job_sum_w_job_additions.setText(amount_str(job_sum_w_additions))
        self.label_job_sum_w_job_additions_w_VAT.setText(amount_str(job_sum_w_additions_w_VAT))
        self.label_job_sum_w_job_additions_VAT_amount.setText(amount_str(job_sum_w_additions_VAT_amount))
        """ KG """
        trade_cost_group = trade.cost_group.id if trade else "-"
        self.label_job_cost_group_2.setText(str(trade_cost_group))

        """ safety deposits """
        self.label_job_safety_deposits_sum.setText(amount_str(safety_deposits_sum))
        # verified_sum_w_VAT since the safety deposit is also taken from the amount with VAT
        safety_deposits_percent = safety_deposits_sum/verified_sum_w_VAT*100 if verified_sum_w_VAT != 0 else 0
        self.label_job_safety_deposits_percent.setText(percent_str(safety_deposits_percent))
        self.label_job_paid_safety_deposits_sum.setText(amount_str(paid_safety_deposits_sum))
        paid_safety_deposits_percent = paid_safety_deposits_sum/safety_deposits_sum*100 if safety_deposits_sum !=0 else 0
        self.label_job_paid_safety_deposits_percent.setText(percent_str(paid_safety_deposits_percent))
        self.label_job_remaining_sd_sum.setText(amount_str(safety_deposits_sum-paid_safety_deposits_sum))
        remaining_sd_percent = 100-paid_safety_deposits_percent
        self.label_job_remaining_sd_percent.setText(percent_str(remaining_sd_percent))

    def set_verified_sum_info(self, verified_sum=0, verified_sum_w_VAT=0, verified_sum_VAT_amount=0):
        """ amounts """
        self.label_job_verified_sum.setText(amount_str(verified_sum))
        self.label_job_verified_sum_w_VAT.setText(amount_str(verified_sum_w_VAT))
        self.label_job_verified_sum_VAT_amount.setText(amount_str(verified_sum_VAT_amount))

    def set_paid_safety_deposits_of_job(self, paid_safety_deposits):
        self.treeWidget_paid_safety_desposits.clear()
        for psd in paid_safety_deposits:
            helper.add_item_to_tree(content_item=psd,
                                    parent=self.treeWidget_paid_safety_desposits,
                                    cols=[str(psd["date"]), amount_w_currency_str(psd["amount"], self.currency), psd["comment"]])

    def set_job_additions_of_job(self, job_additions):
        self.treeWidget_job_additions.clear()
        for job_addition in job_additions:
            helper.add_item_to_tree(content_item=job_addition,
                                    parent=self.treeWidget_job_additions,
                                    cols=[str(job_addition["date"]), amount_w_currency_str(job_addition["amount"], self.currency), job_addition["comment"]])

    #   Fill the listwidget with the invoices
    def set_invoices_of_job(self, invoices_of_job):
        self.treeWidget_invoices_of_curr_job.clear()
        for invoice in invoices_of_job:
            helper.add_item_to_tree(content_item=invoice,
                                    parent=self.treeWidget_invoices_of_curr_job,
                                    cols=[str(invoice.invoice_date.toPyDate()), str(invoice.id), amount_w_currency_str(invoice.safety_deposit_amount, self.currency), amount_w_currency_str(invoice.verified_amount, self.currency)],
                                    tooltip=f"sachlich richtig und rechnerisch geprüfte Rechnungssumme (netto) {amount_w_currency_str(invoice.verified_amount, self.app_data.project.get_currency())}")

    """ render
    #
    #   COMPANIES-TAB
    #
    """
    def render_company_view(self, set_width=False):
        self.activate_company_buttons()
        amount_cols = ["budget"]
        helper.render_to_table(content=self.app_data.project.companies,
                                table=self.tableWidget_companies,
                                cols=self.company_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                currency=self.currency,
                                set_width=set_width)
        item = self.tableWidget_companies.currentItem()
        if item:
            curr_company = item.data(1)
            self.render_company_info(curr_company)

    def render_company_info(self, company):
        if company.is_not_deleted():
            args = vars(company).copy()
            self.set_company_data(**args)
            self.set_invoices_of_company_by_job(company)
            self.activate_company_buttons()
        else:
            self.reset_company_info()

    def activate_company_buttons(self):
        if self.tableWidget_companies.currentItem():
            self.pushButton_edit_company.setEnabled(True)
        else:
            self.pushButton_edit_company.setEnabled(False)

    def reset_company_info(self):
        self.set_company_data()
        self.treeWidget_company_invoices_by_job.clear()
        self.activate_company_buttons()

    def set_company_data(self, *, _uid=None, name="-", service="-", service_type="-", budget=0, contact_person=None, **kwargs):
        """ data """
        self.label_company_uid.setText(_uid.labelize() if _uid else "-")
        """ company attributes """
        self.label_company_name.setText(name)
        self.label_company_service.setText(service)
        self.label_company_service_type.setText(service_type)
        """ budget """
        budget_VAT_amount = budget * self.app_data.project.get_vat()
        budget_w_VAT = budget + budget_VAT_amount
        self.label_company_budget.setText(amount_str(budget))
        self.label_company_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_company_budget_VAT_amount.setText(amount_str(budget_VAT_amount))
        if contact_person:
            """ contact person """
            self.label_company_contact_person_first_name.setText(contact_person.first_name)
            self.label_company_contact_person_last_name.setText(contact_person.last_name)
        else:
            self.label_company_contact_person_first_name.setText("-")
            self.label_company_contact_person_last_name.setText("")

    def set_invoices_of_company_by_job(self, company):
        self.treeWidget_company_invoices_by_job.clear()
        invoices_of_company = self.app_data.project.get_invoices_of_company(company)
        jobs = {invoice.job for invoice in invoices_of_company}
        currency = self.app_data.project.get_currency()
        for job in jobs:
            job_node = QtWidgets.QTreeWidgetItem(self.treeWidget_company_invoices_by_job)
            job_node.setData(1, QtCore.Qt.UserRole, job)
            invoices_of_company_and_job = [invoice for invoice in invoices_of_company if invoice.job is job]
            job_sum = 0
            for invoice in invoices_of_company_and_job:
                helper.add_item_to_tree(content_item=invoice,
                                            parent=job_node,
                                            cols=["", str(invoice.id), amount_w_currency_str(invoice.verified_amount, currency)])
                job_sum += invoice.verified_amount
            job_node.setText(0, f"{job.id} ({self.app_data.titles['job_sum']}: {amount_w_currency_str(job.job_sum, currency)})")
            job_node.setText(1, f"{len(invoices_of_company_and_job)}")
            job_node.setText(2, amount_w_currency_str(job_sum, currency))

    """ render
    #
    #   TRADES-TAB
    #
    """
    def render_trades(self, set_width=False):
        self.activate_trade_buttons()
        amount_cols = ["budget"]
        helper.render_to_table(content=self.app_data.project.trades,
                                table=self.tableWidget_trades,
                                cols=self.trade_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                currency=self.currency,
                                set_width=set_width)
        item = self.tableWidget_trades.currentItem()
        if item:
            curr_trade = item.data(1)
            self.render_trade_info(curr_trade)

    def render_trade_info(self, trade):
        if trade.is_not_deleted():
            args = vars(trade).copy()
            self.set_trade_data(**args)
            self.activate_trade_buttons()
        else:
            self.reset_trade_info()

    def activate_trade_buttons(self):
        if self.tableWidget_trades.currentItem():
            self.pushButton_edit_trade.setEnabled(True)
        else:
            self.pushButton_edit_trade.setEnabled(False)

    def reset_trade_info(self):
        self.set_trade_data()
        self.activate_trade_buttons()

    def set_trade_data(self, *, _uid=None, name="", cost_group=None, comment="", budget=0, **kwargs):
        """ meta data """
        self.label_trade_uid.setText(_uid.labelize() if _uid else "-")

        self.label_trade_name.setText(str(name))
        self.textEdit_trade_comment.setText(str(comment))

        """ cost_group """
        self.label_trade_cost_group.setText(str(cost_group) if cost_group else "-")

        """ budget """
        self.label_trade_budget.setText(amount_str(budget))
        budget_VAT_amount = budget * self.app_data.project.get_vat()
        budget_w_VAT = budget + budget_VAT_amount
        self.label_trade_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_trade_budget_VAT_amount.setText(amount_str(budget_VAT_amount))

    """ render
    #
    #   COST GROUPS-TAB
    #
    """
    def render_cost_groups(self, set_width=False):
        self.activate_cost_group_buttons()
        amount_cols = ["budget"]
        helper.render_to_table(content=self.app_data.project.cost_groups,
                                table=self.tableWidget_cost_groups,
                                cols=self.cost_group_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                currency=self.currency,
                                set_width=set_width)
        item = self.tableWidget_cost_groups.currentItem()
        if item:
            curr_cost_group = item.data(1)
            self.render_cost_group_info(curr_cost_group)

    def render_cost_group_info(self, cost_group):
        if cost_group.is_not_deleted():
            args = vars(cost_group).copy()
            self.set_cost_group_data(**args)
            self.activate_cost_group_buttons()
        else:
            self.reset_cost_group_info()

    def activate_cost_group_buttons(self):
        if self.tableWidget_cost_groups.currentItem():
            self.pushButton_edit_cost_group.setEnabled(True)
        else:
            self.pushButton_edit_cost_group.setEnabled(False)

    def reset_cost_group_info(self):
        self.set_cost_group_data()
        self.activate_cost_group_buttons()

    def set_cost_group_data(self, *, _uid=None, id="", name="", description="", budget=0, parent=None, **kwargs):
        """ meta data """
        self.label_cost_group_uid.setText(_uid.labelize() if _uid else "-")

        self.label_cost_group_id.setText(str(id))
        self.label_cost_group_name.setText(str(name))
        self.label_cost_group_parent_2.setText(str(parent) if parent else "-")
        self.textEdit_cost_group_description.setText(str(description))

        """ budget """
        self.label_cost_group_budget.setText(amount_str(budget))
        budget_VAT_amount = budget * self.app_data.project.get_vat()
        budget_w_VAT = budget + budget_VAT_amount
        self.label_cost_group_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_cost_group_budget_VAT_amount.setText(amount_str(budget_VAT_amount))


    """ render
    #
    #   PEOPLE-TAB
    #
    """
    def render_people(self, set_width=False):
        self.activate_person_buttons()
        amount_cols = ["budget"]
        helper.render_to_table(content=self.app_data.project.people,
                                table=self.tableWidget_people,
                                cols=self.person_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                currency=self.currency,
                                set_width=set_width)
        item = self.tableWidget_people.currentItem()
        if item:
            curr_person = item.data(1)
            self.render_person_info(curr_person)

    def render_person_info(self, person):
        if person.is_not_deleted():
            args = vars(person).copy()
            self.set_person_data(**args)
            self.activate_person_buttons()
        else:
            self.reset_person_info()

    def activate_person_buttons(self):
        if self.tableWidget_people.currentItem():
            self.pushButton_edit_person.setEnabled(True)
        else:
            self.pushButton_edit_person.setEnabled(False)

    def reset_person_info(self):
        self.set_person_data()
        self.activate_person_buttons()

    def set_person_data(self, *, _uid=None, first_name="", last_name="", telephone="", mobile="", fax="", email="", address=None, company=None, **kwargs):
        """ meta data """
        self.label_person_uid.setText(_uid.labelize() if _uid else "-")

        self.label_person_company_2.setText(str(company) if company else "-")
        self.label_person_name_2.setText(f"{first_name} {last_name}")
        self.label_person_telephone_2.setText(telephone)
        self.label_person_mobile_2.setText(mobile)
        self.label_person_fax_2.setText(fax)
        self.label_person_email_2.setText(email)
        """ address """
        if address:
            self.label_person_street_2.setText(address.street)
            self.label_person_house_number_2.setText(address.house_number)
            self.label_person_city_2.setText(address.city)
            self.label_person_state_2.setText(address.state)
            self.label_person_zipcode_2.setText(address.zipcode)
            self.label_person_country_2.setText(address.country)
        else:
            self.label_person_street_2.setText("-")
            self.label_person_house_number_2.setText("-")
            self.label_person_city_2.setText("-")
            self.label_person_state_2.setText("-")
            self.label_person_zipcode_2.setText("-")
            self.label_person_country_2.setText("-")


    """
    #
    #   RENDER INVERACTIONS
    #   functions that change views or current tabs
    #
    """
    def set_job_view_sel_invoice(self):
        sel_invoice = self.tableWidget_invoices.currentItem().data(1)
        self.set_job_view(sel_job=sel_invoice.job)
        self.render_job_info(sel_invoice.job)

    def set_job_view(self, sel_job=None):
        helper.select_table_item(self.tableWidget_jobs, sel_job)
        self.change_tab("tab_jobs_table")

    def change_tab(self, tab_name):
        tab = self.tabWidget_content.findChild(QtWidgets.QWidget, tab_name)
        self.tabWidget_content.setCurrentWidget(tab)

    """
    #
    #   FUNCTIONALITY
    #   functions actually interacting with, creating or editing/manipulating objects
    #   used in the above connect argument
    #
    """
    """ func
    #
    #   PROJECT
    #
    """
    def input_new_project(self):
        # TODO: If current project is not empty ask to save
        if self.app_data.project_loaded():
            reply = helper.save_curr_project_prompt(self, self.app_data)
            if reply:
                helper.input_new_project(self.app_data)
        else:
            helper.input_new_project(self.app_data)
        if self.app_data.project_loaded():
            self.update_ui()
            self.init_column_width()

    def edit_project(self):
        helper.edit_project(self.app_data)
        self.update_ui()

    def load_project(self):
        if self.app_data.project_loaded():
            reply = helper.save_curr_project_prompt(self, self.app_data)
            if reply:
                helper.load_project(self, self.app_data)
        else:
            helper.load_project(self, self.app_data)
        if self.app_data.project_loaded():
            self.update_ui()
            self.init_column_width()

    def save_project(self):
        helper.save_project(self, self.app_data)

    def save_project_as(self):
        helper.save_project_as(self, self.app_data)
        self.update_ui()

    """ func
    #
    #   EXPORT
    #
    """
    def export_companies(self):
        helper.export_companies(self, self.app_data)

    def export_trades(self):
        helper.export_trades(self, self.app_data)

    def export_cost_groups(self):
        helper.export_cost_groups(self, self.app_data)

    """ func
    #
    #   IMPORT
    #
    """
    def import_companies(self):
        helper.import_companies(self, self.app_data)
        self.update_ui()

    def import_trades(self):
        helper.import_trades(self, self.app_data)
        self.update_ui()

    def import_cost_groups(self):
        helper.import_cost_groups(self, self.app_data)
        self.update_ui()

    """ func
    #
    #   CLIENT
    #
    """
    def input_client(self):
        person = helper.input_person(self.app_data)
        if person:
            self.app_data.project.client = person
            """ logging """
            debug.log(f"Client set to: {person.first_name}, {person.last_name}")

    """ func
    #
    #   INVOICE
    #
    """
    @debug.log
    def input_invoice_to_project(self, sel_job=None):
        invoice = helper.input_invoice(self.app_data, sel_job=sel_job)
        self.update_ui()

    @debug.log
    def edit_invoice(self, invoice):
        invoice = helper.edit_invoice(self.app_data, invoice)
        if invoice:
            self.render_invoice_info(invoice)
            self.update_ui()
            self.activate_invoice_buttons()

    @debug.log
    def invoice_check(self, invoice, save_path=None):
        self.app_data.output_check_invoice(invoice)
        self.app_data.open_invoice_check_dir()
        self.app_data.open_client_correspondence_dir()
        debug.log(f"Invoice check file written for the invoice {invoice}")

    """ func
    #
    #   JOB
    #
    """
    @debug.log
    def input_job_to_project(self):
        job = helper.input_job(self.app_data)
        self.update_ui()

    @debug.log
    def edit_job(self, job):
        job = helper.edit_job(self.app_data, job)
        if job:
            self.render_job_info(job)
            self.update_ui()
            self.activate_job_buttons()

    """ func
    #
    #   COMPANY
    #
    """
    @debug.log
    def input_company_to_project(self):
        company = helper.input_company(self.app_data)
        self.update_ui()

    @debug.log
    def edit_company(self, company):
        company = helper.edit_company(self.app_data, company)
        if company:
            self.render_company_info(company)
            self.update_ui()
            self.activate_company_buttons()

    """ func
    #
    #   TRADE
    #
    """
    @debug.log
    def input_trade_to_project(self):
        trade = helper.input_trade(self.app_data)
        self.update_ui()

    @debug.log
    def edit_trade(self, trade):
        trade = helper.edit_trade(self.app_data, trade)
        if trade:
            self.render_trade_info(trade)
            self.update_ui()
            self.activate_trade_buttons()

    """ func
    #
    #   COST GROUP
    #
    """
    @debug.log
    def input_cost_group_to_project(self):
        cost_group = helper.input_cost_group(self.app_data)
        self.update_ui()

    @debug.log
    def edit_cost_group(self, cost_group):
        cost_group = helper.edit_cost_group(self.app_data, cost_group)
        if cost_group:
            self.render_cost_group_info(cost_group)
            self.update_ui()
            self.activate_cost_group_buttons()

    """ func
    #
    #   Person
    #
    """
    @debug.log
    def input_person_to_project(self):
        person = helper.input_person(self.app_data)
        self.update_ui()

    @debug.log
    def edit_person(self, person):
        person = helper.edit_person(self.app_data, person)
        if person:
            self.render_person_info(person)
            self.update_ui()
            self.activate_person_buttons()

    """ func
    #
    #   CONFIG
    #
    """
    @debug.log
    def edit_app_config(self):
        config = helper.edit_app_config(self.app_data)
        if config:
            self.update_ui()

    @debug.log
    def edit_proj_config(self):
        config = helper.edit_proj_config(self.app_data)
        if config:
            self.update_ui()

    """
    #
    #   DEBUG FUNCTIONS
    #
    """
    def print_project_info(self):
        if self.app_data.project:
            debug.log(self.app_data.project.__dict__)
        else:
            debug.log("No Project yet!")
    def print_invoices(self):
        if self.app_data.project.invoices:
            for invoice in self.app_data.project.invoices:
                debug.log(vars(invoice))
