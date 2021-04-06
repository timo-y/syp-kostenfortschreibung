"""
#
#   Main window
#
#
"""
import string
import random

import debug

import os
import datetime

import json, uuid

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtWidgets import (QDialog, QInputDialog,
                            QFileDialog, QGraphicsColorizeEffect)
from PyQt5.QtCore import QEvent, QDate, QPropertyAnimation
from PyQt5.QtCore import pyqtSlot, QObject
from ui import customqt

from core.obj import (proj, corp, arch)
from ui import dlg, helper
from ui.helper import (rnd, amount_str, percent_str,
                       percent_str_w_sign, qdate_to_str)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_data):
        super().__init__()

        self.app_data = app_data

        self.def_table_header_vars()

        self.initialize_ui()
        self.set_window_icon()
        self.center_window()
        self.set_button_actions()
        self.load_widget_signals()
        self.load_action_signals()
        self.load_line_edit_signals()

        if self.app_data.project is None:
            self.disable_ui()

        """ DEBUG """
        self.set_debug_ui()

    @property
    def currency(self):
        if self.app_data.project_loaded():
            return self.app_data.project.get_currency()
        return self.app_data.get_currency()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/mainwindow.ui', self) # Load the .ui file
        self.initialize_tabwidget()
        self.init_tree_header()

    def set_window_icon(self):
        self.setWindowIcon(QtGui.QIcon('images/icon.png'))

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
        self.tabWidget_content.addTab(self.tab_project_cost_calculation, "Kostenermittlung")
        #self.tabWidget_content.addTab(self.tab_invoice_check, "???")

    def init_table_header(self):
        self.render_cost_stand(set_width=True)
        self.render_invoice_view(set_width=True)
        self.render_job_view(set_width=True)
        self.render_company_view(set_width=True)
        self.render_trades(set_width=True)
        self.render_cost_groups(set_width=True)
        self.render_people(set_width=True)
        self.render_project_cost_calculations(set_width=True)

    def def_table_header_vars(self):
        """
        #
        #   COLUMNS OF TABLE VIEWS
        #   TODO: load these from external file
        #
        """
        self.cost_stand_cost_group_cols = [
            {"title": "cost_group", "width": 130},
            {"title": "project_budget", "width": 130},
            {"title": "project_budget_w_VAT", "width": 130},
            {"title": "job_sums", "width": 130},
            {"title": "job_sums_w_VAT", "width": 130},
            {"title": "approved_invoices_w_VAT", "width": 150},
            {"title": "approved_invoices_w_VAT_by_job_sums", "width": 150},
            ]

        self.cost_stand_trade_cols = [
            {"title": "trade", "width": 130},
            {"title": "budget", "width": 130},
            {"title": "budget_w_VAT", "width": 130},
            {"title": "job_sums", "width": 130},
            {"title": "job_sums_w_VAT", "width": 130},
            {"title": "approved_invoices_w_VAT", "width": 150},
            {"title": "approved_invoices_w_VAT_by_job_sums", "width": 150},
            ]

        self.project_cost_calculation_cols = [
            {"title": "name", "width": 180},
            {"title": "type", "width": 180},
            {"title": "date", "width": 100},
            {"title": "total_cost", "width": 150}
            ]


        self.invoice_cols = [
            {"title": "id", "width": 150},
            {"title": "invoice_date", "width": 110},
            {"title": "company", "width": 120},
            {"title": "job", "width": 60},
            {"title": "cumulative", "width": 60},
            #{"title": "inbox_date", "width": 95},
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
            {"title": "budget", "width": 120},
            {"title": "comment", "width": 100},
        ]
        self.cost_group_cols = [
            {"title": "uid", "width": 1},
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

    def init_tree_header(self):
        """ TODO: figure out where to put this
        #         maybe put on top of file
        """
        company_tree_view_cols = ["job", "job_sum", "invoice", "verified_amount"]
        self.treeWidget_company_invoices_by_job.setHeaderLabels(
            [self.app_data.titles[col] for col in company_tree_view_cols]
            )

        trade_tree_view_cols = ["job", "company", "job_sum", "cost_group", "invoice", "verified_amount"]
        self.treeWidget_trade_invoices_by_job.setHeaderLabels(
            [self.app_data.titles[col] for col in trade_tree_view_cols]
            )

        cost_group_tree_view_cols = ["job", "company", "job_sum", "trade", "invoice", "verified_amount"]
        self.treeWidget_cost_group_invoices_by_job.setHeaderLabels(
            [self.app_data.titles[col] for col in cost_group_tree_view_cols]
            )

        job_tree_view_cols = ["date", "id", "safety_deposit_amount",
                              "amount_a_reductions_amount"]
        self.treeWidget_invoices_of_curr_job.setHeaderLabels(
            [self.app_data.titles[col] for col in job_tree_view_cols]
            )

        paid_safety_deposits_cols = ["date", "amount", "comment"]
        self.treeWidget_paid_safety_desposits.setHeaderLabels(
            [self.app_data.titles[col] for col in paid_safety_deposits_cols]
            )

        job_additions_cols = ["date", "name", "amount", "comment"]
        self.treeWidget_job_additions.setHeaderLabels(
            [self.app_data.titles[col] for col in job_additions_cols]
            )

        cost_groups_costs_cols = ["id", "uid", "name", "description", "budget"]
        self.treeWidget_cost_groups.setHeaderLabels(
            [self.app_data.titles[col] for col in cost_groups_costs_cols]
            )
        # order CostGroup view by first column (id) of the TreeWidget
        self.treeWidget_cost_groups.sortItems(0, QtCore.Qt.AscendingOrder)
        # hide the UID column
        self.treeWidget_cost_groups.setColumnHidden(1, True)

        pcc_cost_group_costs_cols = ["cost_group", "uid", "inventory_items",
                                     "prognosed_costs",
                                     "prognosed_costs_sub_cost_groups"]
        self.treeWidget_pcc_cost_group_details.setHeaderLabels(
            [self.app_data.titles[col] for col in pcc_cost_group_costs_cols]
            )
        # order CostGroup view by first column (id) of the TreeWidget
        self.treeWidget_pcc_cost_group_details.sortItems(0, QtCore.Qt.AscendingOrder)
        # hide the UID column
        self.treeWidget_pcc_cost_group_details.setColumnHidden(1, True)

        pcc_trade_costs_cols = ["trade", "inventory_items", "prognosed_costs"]
        self.treeWidget_pcc_trade_details.setHeaderLabels(
            [self.app_data.titles[col] for col in pcc_trade_costs_cols]
            )


    def enable_ui(self):
        self.centralwidget.setEnabled(True)
        self.menuProjekt.setEnabled(True)
        self.menuImport.setEnabled(True)
        self.menuExport.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)

    def disable_ui(self):
        self.centralwidget.setEnabled(False)
        self.menuProjekt.setEnabled(False)
        self.menuImport.setEnabled(False)
        self.menuExport.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)


    def set_debug_ui(self):
        if self.app_data.debug_on():
            self.groupBox_debug.setVisible(True)
        else:
            self.groupBox_debug.setVisible(False)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_ui(self):
        if self.app_data.project:
            self.enable_ui()
            """ set title """
            mainwindow_title = f"Scharmer-Yu + Partner | Kostenfortschreibung | {self.app_data.project.identifier}"
            self.setWindowTitle(mainwindow_title)

            self.update_labels()
            #update views
            self.render_project_cost_calculations()
            self.render_cost_stand()
            self.render_invoice_view()
            self.render_job_view()
            self.render_company_view()
            self.render_trades()
            self.render_cost_groups()
            self.render_people()
        """ DEBUG """
        self.set_debug_ui()

    def update_labels(self):
        self.label_cur_proj.setText(self.app_data.project.identifier)
        self.label_cur_proj_construction_scheme.setText(
            self.app_data.project.construction_scheme
            )
        """ currency """
        currency_labels = [label for label
                           in self.findChildren(QtWidgets.QLabel)
                           if "label_currency_" in label.objectName()]
        for label in currency_labels:
            label.setText(self.currency)

    """
    #
    #   EVENT LISTENERS
    #
    #
    """
    def closeEvent(self, event):
        if self.app_data.project_loaded():
            reply = QtWidgets.QMessageBox.question(
                self, 'Sichern vor dem Schließen?',
                'Möchten Sie das geöffnete Projekt vor dem Beenden speichern?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel)

            if reply == QtWidgets.QMessageBox.Yes:
                self.save_project()
                event.accept()
            elif reply == QtWidgets.QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


    """
    #
    #   MANIPULATE GUI
    #   Maximize/minimize areas...
    #
    """

    # this function is probably not needed
    def minimize_invoice_info(self):
        print("this should minimize the invoice info widget")

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #       catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        """ DEBUG """
        self.pushButton_debug_run.clicked.connect(self.button_run_test)
        self.pushButton_debug_add_invoices.clicked.connect(self.button_debug_add_invoices)

        """ quick links """
        self.pushButton_quick_new_invoice.clicked.connect(self.button_input_invoice_to_project)
        self.pushButton_quick_new_job.clicked.connect(self.button_input_job_to_project)
        self.pushButton_quick_invoice_check_dir.clicked.connect(lambda:self.app_data.open_invoice_check_dir())
        self.pushButton_quick_syp_dir.clicked.connect(lambda:self.app_data.open_syp_dir())
        self.pushButton_quick_proj_dir.clicked.connect(lambda:self.app_data.open_project_dir())

        """ project cost calculation buttons """
        self.pushButton_new_pcc.clicked.connect(self.button_input_pcc_to_project)
        self.pushButton_edit_pcc.clicked.connect(self.button_edit_pcc)
        self.pushButton_copy_pcc.clicked.connect(self.button_copy_pcc)
        self.pushButton_pcc_apply_budgets.clicked.connect(self.button_apply_pcc_budgets)
        self.pushButton_pcc_apply_budget_cost_group.clicked.connect(self.button_apply_pcc_budget_cost_group)
        self.pushButton_pcc_apply_budget_trade.clicked.connect(self.button_apply_pcc_budget_trade)
        self.pushButton_pcc_apply_budgets_cost_groups.clicked.connect(self.button_apply_pcc_budgets_cost_groups)
        self.pushButton_pcc_apply_budgets_trades.clicked.connect(self.button_apply_pcc_budgets_trades)
        self.commandLinkButton_export_pcc_overviews.clicked.connect(self.button_pcc_overviews)

        """ invoice buttons """
        self.pushButton_new_invoice.clicked.connect(self.button_input_invoice_to_project)
        self.pushButton_edit_invoice.clicked.connect(self.button_edit_invoice)
        self.commandLinkButton_invoice_check_all_jobs.clicked.connect(self.button_invoice_check_all_jobs)
        self.commandLinkButton_invoice_check_curr_job.clicked.connect(self.button_invoice_check_curr_job)
        self.pushButton_go_to_job.clicked.connect(self.button_set_job_view_sel_invoice)
        self.pushButton_invoice_search.clicked.connect(lambda:self.render_invoice_view())
        self.pushButton_reset_invoice_search.clicked.connect(self.button_reset_invoice_search)

        """ job buttons """
        self.pushButton_new_job.clicked.connect(self.button_input_job_to_project)
        self.pushButton_edit_job.clicked.connect(self.button_edit_job)
        self.pushButton_add_invoice_for_curr_job.clicked.connect(self.button_input_invoice_w_curr_job)
        self.pushButton_pay_safety_deposit.clicked.connect(self.button_pay_safety_deposit)
        self.pushButton_remove_safety_deposit.clicked.connect(self.button_remove_psd)
        self.pushButton_add_job_addition.clicked.connect(self.button_add_job_addition)
        self.pushButton_remove_job_addition.clicked.connect(self.button_remove_job_addition)
        self.commandLinkButton_job_ov.clicked.connect(self.button_job_ov)

        """ company buttons """
        self.pushButton_new_company.clicked.connect(self.button_input_company_to_project)
        self.pushButton_edit_company.clicked.connect(self.button_edit_company)
        self.commandLinkButton_company_ov.clicked.connect(self.button_company_ov)
        """ trade buttons """
        self.pushButton_new_trade.clicked.connect(self.button_input_trade_to_project)
        self.pushButton_edit_trade.clicked.connect(self.button_edit_trade)
        self.commandLinkButton_trades_ov.clicked.connect(self.button_trades_ov)


        """ cost_group buttons """
        self.pushButton_new_cost_group.clicked.connect(self.button_input_cost_group_to_project)
        self.pushButton_edit_cost_group.clicked.connect(self.button_edit_cost_group)
        self.commandLinkButton_cost_groups_ov.clicked.connect(self.button_cost_groups_ov)

        """ person buttons """
        self.pushButton_edit_person.clicked.connect(self.button_edit_person)

    def load_widget_signals(self):
        """ project cost calculation signals """
        self.tableWidget_project_cost_calculations.itemDoubleClicked.connect(self.table_double_click_pcc)
        self.tableWidget_project_cost_calculations.currentItemChanged.connect(self.table_click_pcc)

        self.treeWidget_pcc_trade_details.itemClicked.connect(self.activate_pcc_buttons)
        self.treeWidget_pcc_trade_details.currentItemChanged.connect(self.activate_pcc_buttons)

        self.treeWidget_pcc_cost_group_details.itemClicked.connect(self.activate_pcc_buttons)
        self.treeWidget_pcc_cost_group_details.currentItemChanged.connect(self.activate_pcc_buttons)

        """ invoice signals """
        self.listWidget_invoices.itemDoubleClicked.connect(self.list_double_click_invoice)

        self.tableWidget_invoices.itemDoubleClicked.connect(self.table_double_click_invoice)
        self.tableWidget_invoices.currentItemChanged.connect(self.table_click_invoice)

        """ job signals """
        self.tableWidget_jobs.itemDoubleClicked.connect(self.table_double_click_job)
        self.tableWidget_jobs.currentItemChanged.connect(self.table_click_job)

        self.treeWidget_invoices_of_curr_job.itemDoubleClicked.connect(self.tree_double_click_invoice)

        self.treeWidget_paid_safety_desposits.itemClicked.connect(self.activate_job_buttons)
        self.treeWidget_paid_safety_desposits.currentItemChanged.connect(self.activate_job_buttons)

        self.treeWidget_job_additions.itemClicked.connect(self.activate_job_buttons)
        self.treeWidget_job_additions.currentItemChanged.connect(self.activate_job_buttons)

        """ company signals """
        self.tableWidget_companies.itemDoubleClicked.connect(self.table_double_click_company)
        self.tableWidget_companies.currentItemChanged.connect(self.table_click_company)

        self.treeWidget_company_invoices_by_job.itemDoubleClicked.connect(self.tree_double_click_job_invoice)

        """ trade signals """
        self.tableWidget_trades .itemDoubleClicked.connect(self.table_double_click_trade)
        self.tableWidget_trades.currentItemChanged.connect(self.table_click_trade)

        self.treeWidget_trade_invoices_by_job.itemDoubleClicked.connect(self.tree_double_click_job_invoice)

        """ cost_group signals """
        self.treeWidget_cost_groups.itemDoubleClicked.connect(self.tree_double_click_cost_group)
        self.treeWidget_cost_groups.itemClicked.connect(self.tree_click_cost_group)
        self.treeWidget_cost_groups.currentItemChanged.connect(self.tree_click_cost_group)

        self.treeWidget_cost_group_invoices_by_job.itemDoubleClicked.connect(self.tree_double_click_job_invoice)

        """ people signals """
        self.tableWidget_people.itemDoubleClicked.connect(self.table_double_click_person)
        self.tableWidget_people.currentItemChanged.connect(self.table_click_person)


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

        self.actionAbout.triggered.connect(lambda:dlg.open_about_dialog())
        """ EXPORT """
        self.actionExportAllCompanies.triggered.connect(self.export_companies)
        self.actionExportAllTrades.triggered.connect(self.export_trades)
        self.actionExportAllCostGroups.triggered.connect(self.export_cost_groups)
        """ IMPORT """
        self.actionImportProject.triggered.connect(lambda:self.import_project())
        self.actionImportCompanies.triggered.connect(self.import_companies)
        self.actionImportTrades.triggered.connect(self.import_trades)
        self.actionImportCostGroups.triggered.connect(self.import_cost_groups)

        """ CLOSE """
        self.actionClose.triggered.connect(lambda:self.close())

    def load_line_edit_signals(self):
        self.lineEdit_invoice_search.returnPressed.connect(lambda:self.render_invoice_view())
    """
    #
    #   SIGNAL FUNCTIONS
    #   functions to that get connected to the widget signals (some might also be directly used and not in this section)
    #
    """
    """ signal
    #
    #   Mixed
    #
    """
    @pyqtSlot(QtWidgets.QTreeWidgetItem)
    def tree_double_click_job_invoice(self, item):
        if item:
            item_data = item.data(1, QtCore.Qt.UserRole)
            if isinstance(item_data, corp.Invoice):
                self.edit_invoice(item_data)
            elif isinstance(item_data, arch.ArchJob):
                self.edit_job(item_data)

    @pyqtSlot(QtWidgets.QTreeWidgetItem)
    def tree_double_click_cost_group_job_invoice(self, item):
        self.tree_double_click_job_invoice(item)

    """ signal
    #
    #   PROJECT COST CALCULATION
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_pcc(self, item):
        pcc = item.data(1)
        self.edit_pcc(pcc)

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_pcc(self, item):
        if item:
            pcc = item.data(1)
            self.render_pcc_info(pcc)

    @pyqtSlot()
    def button_input_pcc_to_project(self):
        self.input_pcc_to_project()

    @pyqtSlot()
    def button_edit_pcc(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            pcc = item.data(1)
            self.edit_pcc(pcc)
        else:
            debug.log_warning("Couldn't edit project_cost_calculation, no project_cost_calculation selected!")

    @pyqtSlot()
    def button_copy_pcc(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            self.copy_pcc(item.data(1))
        else:
            debug.log_warning("Couldn't copy project_cost_calculation, no project_cost_calculation selected!")

    @pyqtSlot()
    def button_apply_pcc_budgets(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            reply = helper.u_sure_prompt(self)
            if reply:
                pcc = item.data(1)
                self.app_data.project.apply_budgets(pcc)
                self.update_ui()
        else:
            debug.log_warning("Couldn't apply budgets, no project_cost_calculation selected!")

    @pyqtSlot()
    def button_apply_pcc_budget_cost_group(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        cost_group_items = self.treeWidget_pcc_cost_group_details.selectedItems()
        if item and len(cost_group_items)>0:
            reply = helper.u_sure_prompt(self)
            if reply:
                pcc = item.data(1)
                sel_cost_group = cost_group_items[0].data(1, QtCore.Qt.UserRole)
                self.app_data.project.apply_cost_group_budget(pcc, sel_cost_group)
                self.update_ui()
        else:
            debug.log_warning("Couldn't apply CostGroup budget, no project_cost_calculation or cost_group selected!")

    @pyqtSlot()
    def button_apply_pcc_budget_trade(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        trade_items = self.treeWidget_pcc_trade_details.selectedItems()
        if item and len(trade_items)>0:
            reply = helper.u_sure_prompt(self)
            if reply:
                pcc = item.data(1)
                sel_trade = trade_items[0].data(1, QtCore.Qt.UserRole)
                self.app_data.project.apply_trade_budget(pcc, sel_trade)
                self.update_ui()
        else:
            debug.log_warning("Couldn't apply Trade budget, no project_cost_calculation or trade selected!")

    @pyqtSlot()
    def button_apply_pcc_budgets_cost_groups(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            reply = helper.u_sure_prompt(self)
            if reply:
                pcc = item.data(1)
                self.app_data.project.apply_cost_group_budgets(pcc)
                self.update_ui()
        else:
            debug.log_warning("Couldn't apply CostGroup budgets, no project_cost_calculation selected!")

    @pyqtSlot()
    def button_apply_pcc_budgets_trades(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            reply = helper.u_sure_prompt(self)
            if reply:
                pcc = item.data(1)
                self.app_data.project.apply_trade_budgets(pcc)
                self.update_ui()
        else:
            debug.log_warning("Couldn't apply Trade budgets, no project_cost_calculation selected!")


    @pyqtSlot()
    def button_pcc_overviews(self):
        item = self.tableWidget_project_cost_calculations.currentItem()
        if item:
            helper.pcc_overviews(app_data=self.app_data, pcc=item.data(1))
            self.app_data.open_overviews_dir()
        else:
            debug.log_warning("Couldn't create pcc overviews, no pcc selected!")
    """ signal
    #
    #   INVOICE
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_invoice(self, item):
        invoice = item.data(1)
        self.edit_invoice(invoice)

    @pyqtSlot(QtWidgets.QListWidgetItem)
    def list_double_click_invoice(self, item):
        invoice = item.data(1)
        self.edit_invoice(invoice)

    @pyqtSlot(QtWidgets.QTreeWidgetItem)
    def tree_double_click_invoice(self, item):
        self.edit_invoice(item.data(1, QtCore.Qt.UserRole))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_invoice(self, item, prev_item=None):
        if item:
            invoice = item.data(1)
            self.render_invoice_info(invoice)

    @pyqtSlot()
    def button_input_invoice_to_project(self):
        self.input_invoice_to_project()

    @pyqtSlot()
    def button_input_invoice_w_curr_job(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            self.input_invoice_to_project(sel_job=sel_job)
        else:
            raise Exception("No job selected!")

    @pyqtSlot()
    def button_edit_invoice(self):
        item = self.tableWidget_invoices.currentItem()
        if item:
            self.edit_invoice(item.data(1))
        else:
            debug.log_warning("Couldn't edit invoice, no invoice selected!")

    @pyqtSlot()
    def button_invoice_check_curr_job(self):
        item = self.tableWidget_invoices.currentItem()
        if item:
            helper.invoice_check(self.app_data, invoice=item.data(1), curr_job_only=True)
            self.app_data.open_invoice_check_dir()
            self.app_data.open_client_correspondence_dir()
        else:
            debug.log_warning("Couldn't create invoice check, no invoice selected!")

    @pyqtSlot()
    def button_invoice_check_all_jobs(self):
        item = self.tableWidget_invoices.currentItem()
        if item:
            helper.invoice_check(self.app_data, invoice=item.data(1), curr_job_only=False)
            self.app_data.open_invoice_check_dir()
            self.app_data.open_client_correspondence_dir()
        else:
            debug.log_warning("Couldn't create invoice check, no invoice selected!")

    @pyqtSlot()
    def button_reset_invoice_search(self):
        self.lineEdit_invoice_search.setText("")
        self.render_invoice_view()

    """ signal
    #
    #   JOB
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_job(self, item):
        self.edit_job(item.data(1))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_job(self, item, prev_item=None):
        if item:
            job = item.data(1)
            self.render_job_info(job)

    @pyqtSlot()
    def button_input_job_to_project(self):
        self.input_job_to_project()

    @pyqtSlot()
    def button_edit_job(self):
        if self.tableWidget_jobs.currentItem():
            self.edit_job(self.tableWidget_jobs.currentItem().data(1))
        else:
            raise Exception("No job selected!")

    @pyqtSlot()
    def button_pay_safety_deposit(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            helper.pay_safety_deposit(sel_job)
            self.render_job_info(sel_job)
            self.update_ui()
        else:
            raise Exception("No job selected!")

    @pyqtSlot()
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

    @pyqtSlot()
    def button_add_job_addition(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            helper.add_job_addition(sel_job)
            self.render_job_info(sel_job)
            self.update_ui()
        else:
            raise Exception("No job selected!")

    @pyqtSlot()
    def button_remove_job_addition(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            sel_job = item.data(1)
            job_addition_items = self.treeWidget_job_additions.selectedItems()
            if job_addition_items:
                reply = helper.delete_prompt(self)
                if reply:
                    sel_job_addition = job_addition_items[0].data(1,
                                                            QtCore.Qt.UserRole)
                    sel_job.remove_job_addition(sel_job_addition)
                    self.render_job_info(sel_job)
                    self.update_ui()
            else:
                raise Exception("No job_addition selected!")

        else:
            raise Exception("No job selected!")

    @pyqtSlot()
    def button_job_ov(self):
        item = self.tableWidget_jobs.currentItem()
        if item:
            helper.company_ov(self.app_data, company=item.data(1).company, selected_job=item.data(1))
            self.app_data.open_overviews_dir()
        else:
            debug.log_warning("Couldn't create job overview, no job selected!")

    """ signal
    #
    #   COMPANY
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_company(self, item):
        self.edit_company(item.data(1))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_company(self, item, prev_item=None):
        if item:
            company = item.data(1)
            self.render_company_info(company)

    @pyqtSlot()
    def button_input_company_to_project(self):
        self.input_company_to_project()

    @pyqtSlot()
    def button_edit_company(self):
        if self.tableWidget_companies.currentItem():
            self.edit_company(self.tableWidget_companies.currentItem().data(1))
        else:
            raise Exception("No company selected!")

    @pyqtSlot()
    def button_company_ov(self):
        item = self.tableWidget_companies.currentItem()
        if item:
            helper.company_ov(self.app_data, company=item.data(1))
            self.app_data.open_overviews_dir()
        else:
            debug.log_warning("Couldn't create company overview, no company selected!")

    """ signal
    #
    #   TRADE
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_trade(self, item):
        self.edit_trade(item.data(1))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_trade(self, item, prev_item=None):
        if item:
            trade = item.data(1)
            self.render_trade_info(trade)

    @pyqtSlot()
    def button_input_trade_to_project(self):
        self.input_trade_to_project()

    @pyqtSlot()
    def button_edit_trade(self):
        if self.tableWidget_trades.currentItem():
            self.edit_trade(self.tableWidget_trades.currentItem().data(1))
        else:
            raise Exception("No trade selected!")

    @pyqtSlot()
    def button_trades_ov(self):
        helper.trades_ov(self.app_data)
        self.app_data.open_overviews_dir()

    """ signal
    #
    #  COST GROUP
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_cost_group(self, item):
        self.edit_cost_group(item.data(1))

    @pyqtSlot(QtWidgets.QTreeWidgetItem)
    def tree_double_click_cost_group(self, item):
        self.edit_cost_group(item.data(1, QtCore.Qt.UserRole))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_cost_group(self, item, prev_item=None):
        if item:
            cost_group = item.data(1)
            self.render_cost_group_info(cost_group)

    @pyqtSlot(QtWidgets.QTreeWidgetItem)
    def tree_click_cost_group(self, item):
        if item:
            cost_group = item.data(1, QtCore.Qt.UserRole)
            self.render_cost_group_info(cost_group)

    @pyqtSlot()
    def button_input_cost_group_to_project(self):
        self.input_cost_group_to_project()

    @pyqtSlot()
    def button_edit_cost_group(self):
        if len(self.treeWidget_cost_groups.selectedItems())>0:
            selection = self.treeWidget_cost_groups.selectedItems()
            cost_group = selection[0].data(1, QtCore.Qt.UserRole)
            self.edit_cost_group(cost_group)
        else:
            raise Exception("No cost_group selected!")

    @pyqtSlot()
    def button_cost_groups_ov(self):
        helper.cost_groups_ov(self.app_data)
        self.app_data.open_overviews_dir()


    """ signal
    #
    #  PERSON
    #
    """
    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_double_click_person(self, item):
        self.edit_person(item.data(1))

    @pyqtSlot(QtWidgets.QTableWidgetItem)
    def table_click_person(self, item, prev_item=None):
        if item:
            person = item.data(1)
            self.render_person_info(person)

    @pyqtSlot()
    def button_edit_person(self):
        if self.tableWidget_people.currentItem():
            self.edit_person(self.tableWidget_people.currentItem().data(1))
        else:
            raise Exception("No person selected!")

    """
    #
    #   RENDER VIEWS
    #   functions to render the objects to the respective widgets.
    #   Structure:
    #       - the render_* function will always render the actual items to a
    #         table or treewidget
    #       - the render_*_info function will render the info of a selected
    #         item (from above table/tree/list) to the right sidepanel
    #       - the following functions of each section will be helper functions
    #         for the above two (like actually setting text to labels
    #         or activating buttons etc.).
    #
    """
    """ render
    #
    #   COST STAND-TAB
    #
    """
    @debug.log
    def render_cost_stand(self, set_width=False):
        self.render_cost_stand_cost_groups(set_width=set_width)
        self.render_cost_stand_trades(set_width=set_width)

    @debug.log
    def render_cost_stand_cost_groups(self, set_width=False):
        # disable sorting when filling the table
        # (to avoid bugs with data field)
        self.tableWidget_cost_stand_cost_groups.setSortingEnabled(False)
        """
        #   Number of rows is number of cost_groups plus one summary row
        """
        self.tableWidget_cost_stand_cost_groups.setRowCount(
            len(self.app_data.project.main_cost_groups)+1
            )
        """
        #   Set columns of table to the list self.invoice_cols
        """
        self.tableWidget_cost_stand_cost_groups.setColumnCount(len(self.cost_stand_cost_group_cols))
        if set_width:
            for i in range(len(self.cost_stand_cost_group_cols)):
                self.tableWidget_cost_stand_cost_groups.setColumnWidth(
                    i, self.cost_stand_cost_group_cols[i]["width"]
                    )
        """
        #   Set column titles
        """
        self.tableWidget_cost_stand_cost_groups.setHorizontalHeaderLabels(
            [self.app_data.titles[col["title"]] for col in self.cost_stand_cost_group_cols]
            )
        """
        #   Set title height
        """
        self.tableWidget_cost_stand_cost_groups.horizontalHeader().setFixedHeight(100)
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
        cost_group_budget_total = self.app_data.project.get_cost_group_budget_total()
        job_sums_total = self.app_data.project.get_job_sums_total()
        approved_invoices_w_VAT_total = self.app_data.project.get_approved_amounts_total()
        paid_safety_deposit_total = self.app_data.project.get_psds_total()

        sorting_keys = {
            "cost_group":
                float("inf"),
            "project_budget":
                cost_group_budget_total,
            "project_budget_w_VAT":
                cost_group_budget_total * (1+vat),
            "job_sums":
                job_sums_total,
            "job_sums_w_VAT":
                job_sums_total * (1+vat),
            "approved_invoices_w_VAT":
                approved_invoices_w_VAT_total+paid_safety_deposit_total,
            "approved_invoices_w_VAT_by_job_sums":
                approved_invoices_w_VAT_total*100 /
                (job_sums_total * (1+vat))
                if job_sums_total else 0
        }
        cost_group_total = {
            "cost_group":
                self.app_data.titles["total"],
            "project_budget":
                amount_str(sorting_keys["project_budget"], self.currency),
            "project_budget_w_VAT":
                amount_str(sorting_keys["project_budget_w_VAT"], self.currency),
            "job_sums":
                amount_str(sorting_keys["job_sums"], self.currency),
            "job_sums_w_VAT":
                amount_str(sorting_keys["job_sums_w_VAT"], self.currency),
            "approved_invoices_w_VAT":
                amount_str(sorting_keys["approved_invoices_w_VAT"], self.currency),
            "approved_invoices_w_VAT_by_job_sums":
                percent_str_w_sign(
                    sorting_keys["approved_invoices_w_VAT_by_job_sums"]
                    ) if job_sums_total else "-"
        }

        col = 0
        font = QtGui.QFont()
        font.setBold(True)
        for attr in self.cost_stand_cost_group_cols:
            table_item = customqt.AmountTableWidgetItem(str(cost_group_total[attr["title"]]), sorting_key=sorting_keys[attr["title"]])
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFont(font)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand_cost_groups.setItem(row, col, table_item)
            col += 1

        self.tableWidget_cost_stand_cost_groups.setSortingEnabled(True) # enable sorting once the table is filled

    @debug.log
    def render_cost_stand_trades(self, set_width=False):
        # disable sorting when filling the table
        # (to avoid bugs with data field)
        self.tableWidget_cost_stand_trades.setSortingEnabled(False)
        """
        #   Number of rows is number of cost_groups plus one summary row
        """
        self.tableWidget_cost_stand_trades.setRowCount(
            len(self.app_data.project.trades)+1
            )
        """
        #   Set columns of table to the list self.cost_stand_trade_cols
        """
        self.tableWidget_cost_stand_trades.setColumnCount(len(self.cost_stand_trade_cols))
        if set_width:
            for i in range(len(self.cost_stand_trade_cols)):
                self.tableWidget_cost_stand_trades.setColumnWidth(
                    i, self.cost_stand_trade_cols[i]["width"]
                    )
        """
        #   Set column titles
        """
        self.tableWidget_cost_stand_trades.setHorizontalHeaderLabels(
            [self.app_data.titles[col["title"]] for col in self.cost_stand_trade_cols]
            )
        """
        #   Set title height
        """
        self.tableWidget_cost_stand_trades.horizontalHeader().setFixedHeight(100)
        """
        #   Render cost_group to the table
        """
        row = 0
        for trade in self.app_data.project.trades:
            self.add_trade_to_table(trade, row)
            row += 1
        """
        #   Write summary line
        """
        vat = self.app_data.project.get_vat()
        trade_budgets_total = self.app_data.project.get_trade_budgets_total()
        job_sums_total = self.app_data.project.get_job_sums_total()
        approved_invoices_w_VAT_total = self.app_data.project.get_approved_amounts_total()
        paid_safety_deposit_total = self.app_data.project.get_psds_total()

        sorting_keys = {
            "trade":
                "z"*100,
            "budget":
                trade_budgets_total,
            "budget_w_VAT":
                trade_budgets_total * (1+vat),
            "job_sums":
                job_sums_total,
            "job_sums_w_VAT":
                job_sums_total * (1+vat),
            "approved_invoices_w_VAT":
                approved_invoices_w_VAT_total+paid_safety_deposit_total,
            "approved_invoices_w_VAT_by_job_sums":
                approved_invoices_w_VAT_total*100 / (job_sums_total * (1+vat)) if job_sums_total else 0
        }
        trade_total = {
            "trade":
                self.app_data.titles["total"],
            "budget":
                amount_str(sorting_keys["budget"], self.currency),
            "budget_w_VAT":
                amount_str(sorting_keys["budget_w_VAT"], self.currency),
            "job_sums":
                amount_str(sorting_keys["job_sums"], self.currency),
            "job_sums_w_VAT":
                amount_str(sorting_keys["job_sums_w_VAT"], self.currency),
            "approved_invoices_w_VAT":
                amount_str(sorting_keys["approved_invoices_w_VAT"], self.currency),
            "approved_invoices_w_VAT_by_job_sums":
                percent_str_w_sign(
                    sorting_keys["approved_invoices_w_VAT_by_job_sums"]
                    ) if job_sums_total else "-"
        }

        col = 0
        font = QtGui.QFont()
        font.setBold(True)
        for attr in self.cost_stand_trade_cols:
            table_item = customqt.AmountTableWidgetItem(str(trade_total[attr["title"]]), sorting_key=sorting_keys[attr["title"]])
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFont(font)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand_trades.setItem(row, col, table_item)
            col += 1

        self.tableWidget_cost_stand_trades.setSortingEnabled(True) # enable sorting once the table is filled


    def add_cost_group_to_table(self, cost_group, row):
        """ Calculate values """
        vat = self.app_data.project.get_vat()
        cost_group_budget = self.app_data.project.get_budget_sub_cost_groups(cost_group)
        job_sums = self.app_data.project.get_job_sums_of_sub_cost_groups(cost_group)
        approved_invoices_w_VAT = self.app_data.project.get_approved_amounts_of_sub_cost_groups(cost_group)
        paid_safety_deposit = self.app_data.project.get_psds_of_sub_cost_groups(cost_group)
        """ Create output dictionary """

        sorting_keys = {
            "cost_group":
                int(cost_group.id) if cost_group.id.isnumeric() else helper.to_lex(cost_group.id),
            "project_budget":
                cost_group_budget,
            "project_budget_w_VAT":
                cost_group_budget * (1+vat),
            "job_sums":
                job_sums,
            "job_sums_w_VAT":
                job_sums * (1+vat),
            "approved_invoices_w_VAT":
                approved_invoices_w_VAT+paid_safety_deposit,
            "approved_invoices_w_VAT_by_job_sums":
                approved_invoices_w_VAT*100 /
                (job_sums * (1+vat))
                if job_sums else 0
        }
        cost_group_attr = {
            "cost_group":
                cost_group.id,
            "project_budget":
                amount_str(sorting_keys["project_budget"], self.currency),
            "project_budget_w_VAT":
                amount_str(sorting_keys["project_budget_w_VAT"], self.currency),
            "job_sums":
                amount_str(sorting_keys["job_sums"], self.currency),
            "job_sums_w_VAT":
                amount_str(sorting_keys["job_sums_w_VAT"], self.currency),
            "approved_invoices_w_VAT":
                amount_str(sorting_keys["approved_invoices_w_VAT"], self.currency),
            "approved_invoices_w_VAT_by_job_sums":
                percent_str_w_sign(
                    sorting_keys["approved_invoices_w_VAT_by_job_sums"]
                    ) if job_sums else "-"
        }

        col = 0
        for attr in self.cost_stand_cost_group_cols:
            table_item = customqt.AmountTableWidgetItem(str(cost_group_attr[attr["title"]]), sorting_key=sorting_keys[attr["title"]])
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand_cost_groups.setItem(row, col, table_item)
            col += 1

    def add_trade_to_table(self, trade, row):
        """ Calculate values """
        vat = self.app_data.project.get_vat()
        job_sums = self.app_data.project.get_job_sums_of_trade(trade)
        approved_invoices_w_VAT = self.app_data.project.get_approved_amounts_of_trade(trade)
        paid_safety_deposit = self.app_data.project.get_psds_of_trade(trade)

        """ Create output dictionary """
        sorting_keys = {
            "trade":
                trade.name,
            "budget":
                trade.budget,
            "budget_w_VAT":
                trade.budget * (1+vat),
            "job_sums":
                job_sums,
            "job_sums_w_VAT":
                job_sums * (1+vat),
            "approved_invoices_w_VAT":
                approved_invoices_w_VAT+paid_safety_deposit,
            "approved_invoices_w_VAT_by_job_sums":
                approved_invoices_w_VAT*100 /
                (job_sums * (1+vat))
                if job_sums else 0
        }
        trade_attr = {
            "trade":
                trade.name,
            "budget":
                amount_str(sorting_keys["budget"], self.currency),
            "budget_w_VAT":
                amount_str(sorting_keys["budget_w_VAT"], self.currency),
            "job_sums":
                amount_str(sorting_keys["job_sums"], self.currency),
            "job_sums_w_VAT":
                amount_str(sorting_keys["job_sums_w_VAT"], self.currency),
            "approved_invoices_w_VAT":
                amount_str(sorting_keys["approved_invoices_w_VAT"], self.currency),
            "approved_invoices_w_VAT_by_job_sums":
                percent_str_w_sign(
                    sorting_keys["approved_invoices_w_VAT_by_job_sums"]
                    ) if job_sums else "-"
        }

        col = 0
        for attr in self.cost_stand_trade_cols:
            table_item = customqt.AmountTableWidgetItem(str(trade_attr[attr["title"]]), sorting_key=sorting_keys[attr["title"]])
            table_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
            self.tableWidget_cost_stand_trades.setItem(row, col, table_item)
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
    @debug.log
    def render_invoice_view(self, set_width=False):
        self.activate_invoice_buttons()
        date_cols = ["invoice_date", "inbox_date", "checked_date"]
        search_terms = self.lineEdit_invoice_search.text().split(" ") \
                       if len(self.lineEdit_invoice_search.text())>0 else None
        """
        #
        #   invoices_to_render
        #       Filter the invoices by the search terms.
        #
        """
        invoices_to_render = {invoice for invoice in
                              self.app_data.project.invoices
                              for search_term in search_terms
                              for invoice_info in [str(invoice.id).lower(), str(invoice.company.name).lower()]
                              if str(search_term).lower() in invoice_info
                             } if search_terms else self.app_data.project.invoices

        helper.render_to_table(content=invoices_to_render,
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
            self.commandLinkButton_invoice_check_all_jobs.setEnabled(True)
            self.commandLinkButton_invoice_check_curr_job.setEnabled(True)
            self.pushButton_edit_invoice.setEnabled(True)
        else:
            self.pushButton_go_to_job.setEnabled(False)
            self.commandLinkButton_invoice_check_all_jobs.setEnabled(False)
            self.commandLinkButton_invoice_check_curr_job.setEnabled(False)
            self.pushButton_edit_invoice.setEnabled(False)

    def reset_invoice_info(self):
        self.set_invoice_info()
        self.activate_invoice_buttons()

    def set_invoice_info(self, *, _uid=None, id="-", VAT=None, cumulative=True,
                    invoice_date=None, inbox_date=None, checked_date=None,
                    company=None, job=None, amount=0, verified_amount=0,
                    rebate=0, reduction_insurance_costs=0,
                    reduction_usage_costs=0, safety_deposit=0, discount=0,
                    amount_w_VAT=0, amount_VAT_amount=0,
                    verified_amount_w_VAT=0, verified_amount_VAT_amount=0,
                    prev_invoices_count="-", prev_invoices_amount=0,
                    rebate_amount=0, reduction_insurance_costs_amount=0,
                    reduction_usage_costs_amount=0,
                    amount_a_reductions_amount=0,
                    amount_a_reductions_amount_w_VAT=0,
                    amount_a_reductions_amount_VAT_amount=0,
                    safety_deposit_amount=0, approved_amount=0,
                    discount_amount=0, approved_amount_a_discount_amount=0,
                    **kwargs):
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
            self.label_cumulative.setEnabled(False)
            f.setStrikeOut(True)
            self.label_cumulative.setFont(f)
        else:
            self.label_cumulative.setEnabled(True)
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
        self.label_approved_amount.setText(amount_str(approved_amount, self.currency))
        self.label_discount_amount.setText(amount_str(discount_amount))
        self.label_approved_amount_a_discount_amount.setText(amount_str(approved_amount_a_discount_amount, self.currency))
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
    @debug.log
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
            inv_sum = sum([invoice.amount_a_reductions_amount for invoice in invoices_of_job])
            inv_sum_w_VAT = sum([invoice.amount_a_reductions_amount_w_VAT for invoice in invoices_of_job])
            inv_sum_VAT_amount = sum([invoice.amount_a_reductions_amount_VAT_amount for invoice in invoices_of_job])

            safety_deposits_sum = sum([invoice.safety_deposit_amount for invoice in invoices_of_job])
            paid_safety_deposits_sum = job.paid_safety_deposits_sum

            self.set_job_data(**args,
                                job_sum_w_additions=job.job_sum_w_additions,
                                inv_sum_w_VAT=inv_sum_w_VAT,
                                safety_deposits_sum=safety_deposits_sum,
                                paid_safety_deposits_sum=paid_safety_deposits_sum)
            self.set_invoice_sum_info(inv_sum, inv_sum_w_VAT, inv_sum_VAT_amount)
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
            self.commandLinkButton_job_ov.setEnabled(True)
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
            self.commandLinkButton_job_ov.setEnabled(False)
            self.pushButton_pay_safety_deposit.setEnabled(False)
            self.pushButton_remove_safety_deposit.setEnabled(False)
            self.pushButton_add_job_addition.setEnabled(False)
            self.pushButton_remove_job_addition.setEnabled(False)

    def reset_job_info(self):
        self.set_job_data()
        self.set_invoice_sum_info()
        self.set_paid_safety_deposits_of_job()
        self.set_job_additions_of_job()
        self.set_invoices_of_job()
        self.treeWidget_invoices_of_curr_job.clear()
        self.activate_job_buttons()

    def set_job_data(self, *, _uid=None, company=None, id="-", trade=None, cost_group=None, job_sum=0, job_sum_w_additions=0,
                        inv_sum_w_VAT=0, safety_deposits_sum=0, paid_safety_deposits_sum=0,
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
        cost_group_id = cost_group.id if cost_group else "-"
        self.label_job_cost_group_2.setText(str(cost_group_id))

        """ safety deposits """
        self.label_job_safety_deposits_sum.setText(amount_str(safety_deposits_sum))
        # verified_sum_w_VAT since the safety deposit is also taken from the amount with VAT
        safety_deposits_percent = safety_deposits_sum/inv_sum_w_VAT*100 if inv_sum_w_VAT != 0 else 0
        self.label_job_safety_deposits_percent.setText(percent_str(safety_deposits_percent))
        self.label_job_paid_safety_deposits_sum.setText(amount_str(paid_safety_deposits_sum))
        paid_safety_deposits_percent = paid_safety_deposits_sum/safety_deposits_sum*100 if safety_deposits_sum !=0 else 0
        self.label_job_paid_safety_deposits_percent.setText(percent_str(paid_safety_deposits_percent))
        self.label_job_remaining_sd_sum.setText(amount_str(safety_deposits_sum-paid_safety_deposits_sum))
        remaining_sd_percent = 100-paid_safety_deposits_percent
        self.label_job_remaining_sd_percent.setText(percent_str(remaining_sd_percent))

    def set_invoice_sum_info(self, inv_sum=0, inv_sum_w_VAT=0, inv_sum_VAT_amount=0):
        """ amounts """
        self.label_job_invoice_sum.setText(amount_str(inv_sum))
        self.label_job_invoice_sum_w_VAT.setText(amount_str(inv_sum_w_VAT))
        self.label_job_invoice_sum_VAT_amount.setText(amount_str(inv_sum_VAT_amount))

    def set_paid_safety_deposits_of_job(self, paid_safety_deposits=list()):
        self.treeWidget_paid_safety_desposits.clear()
        for psd in paid_safety_deposits:
            helper.add_item_to_tree(content_item=psd,
                                    parent=self.treeWidget_paid_safety_desposits,
                                    cols=[str(psd["date"].toPyDate()), amount_str(psd["amount"], self.currency), psd["comment"]])

    def set_job_additions_of_job(self, job_additions=list()):
        self.treeWidget_job_additions.clear()
        for job_addition in job_additions:
            helper.add_item_to_tree(content_item=job_addition,
                                    parent=self.treeWidget_job_additions,
                                    cols=[str(job_addition["date"].toPyDate()), job_addition["name"], amount_str(job_addition["amount"], self.currency), job_addition["comment"]])

    #   Fill the listwidget with the invoices
    def set_invoices_of_job(self, invoices_of_job=list()):
        self.treeWidget_invoices_of_curr_job.clear()
        for invoice in invoices_of_job:
            helper.add_item_to_tree(content_item=invoice,
                                    parent=self.treeWidget_invoices_of_curr_job,
                                    cols=[str(invoice.invoice_date.toPyDate()), str(invoice.id), amount_str(invoice.safety_deposit_amount, self.currency), amount_str(invoice.amount_a_reductions_amount, self.currency)],
                                    )

    """ render
    #
    #   COMPANIES-TAB
    #
    """
    @debug.log
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
            self.commandLinkButton_company_ov.setEnabled(True)
        else:
            self.pushButton_edit_company.setEnabled(False)
            self.commandLinkButton_company_ov.setEnabled(False)

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
                                            cols=["","", str(invoice.id), amount_str(invoice.amount_wout_prev_payments, currency)])
                job_sum += invoice.amount_wout_prev_payments
            job_node.setText(0, f"{job.id}")
            job_node.setText(1, f"{amount_str(job.job_sum, currency)}")
            job_node.setText(2, f"{len(invoices_of_company_and_job)}")
            job_node.setText(3, amount_str(job_sum, currency))
        helper.resize_tree_columns(self.treeWidget_company_invoices_by_job)

    """ render
    #
    #   TRADES-TAB
    #
    """
    @debug.log
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
            self.set_invoices_of_trade_by_job(trade)
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
        self.treeWidget_trade_invoices_by_job.clear()
        self.activate_trade_buttons()

    def set_trade_data(self, *, _uid=None, name="", comment="", budget=0, **kwargs):
        """ meta data """
        self.label_trade_uid.setText(_uid.labelize() if _uid else "-")

        self.label_trade_name.setText(str(name))
        self.textEdit_trade_comment.setText(str(comment))

        """ budget """
        self.label_trade_budget.setText(amount_str(budget))
        budget_VAT_amount = budget * self.app_data.project.get_vat()
        budget_w_VAT = budget + budget_VAT_amount
        self.label_trade_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_trade_budget_VAT_amount.setText(amount_str(budget_VAT_amount))

    def set_invoices_of_trade_by_job(self, trade):
        self.treeWidget_trade_invoices_by_job.clear()
        invoices_of_trade = self.app_data.project.get_invoices_of_trade(trade)
        jobs = {invoice.job for invoice in invoices_of_trade}
        currency = self.app_data.project.get_currency()
        for job in jobs:
            job_node = QtWidgets.QTreeWidgetItem(self.treeWidget_trade_invoices_by_job)
            job_node.setData(1, QtCore.Qt.UserRole, job)
            invoices_of_trade_and_job = [invoice for invoice in invoices_of_trade if invoice.job is job]
            job_sum = 0
            for invoice in invoices_of_trade_and_job:
                helper.add_item_to_tree(content_item=invoice,
                                            parent=job_node,
                                            cols=["","","","", str(invoice.id), amount_str(invoice.amount_wout_prev_payments, currency)])
                job_sum += invoice.amount_wout_prev_payments
            job_node.setText(0, f"{job.id}")
            job_node.setText(1, f"{job.company.name}")
            job_node.setText(2, f"{amount_str(job.job_sum, currency)}")
            job_node.setText(3, f"{job.cost_group.id}")
            job_node.setText(4, f"{len(invoices_of_trade_and_job)}")
            job_node.setText(5, amount_str(job_sum, currency))
        helper.resize_tree_columns(self.treeWidget_trade_invoices_by_job)

    """ render
    #
    #   COST GROUPS-TAB
    #
    """
    @debug.log
    def render_cost_groups(self, set_width=False):
        self.activate_cost_group_buttons()
        # TREE WIDGET
        self.render_cost_groups_to_treewidget()
        sel_items = self.treeWidget_cost_groups.selectedItems()
        if len(sel_items)>0:
            curr_cost_group = sel_items[0].data(1, QtCore.Qt.UserRole)
            self.render_cost_group_info(curr_cost_group)

    """
    #
    #   COST GROUPS to TreeWidget
    #       Its a little harder to get the tree structure, so the following two functions
    #       help us to render the cost_groups with the tree-structure.
    """
    def render_cost_groups_to_treewidget(self):
        # if a cost_group was selected, save here
        sel_items = self.treeWidget_cost_groups.selectedItems()
        sel_cost_group = sel_items[0].data(1, QtCore.Qt.UserRole) if len(sel_items)>0 else None

        self.treeWidget_cost_groups.clear()
        # go layer by layer
        tree_depth = 0
        cost_groups = self.app_data.project.get_cost_groups_of_level(tree_depth)
        cost_groups.sort(key=lambda cost_group:int(cost_group.id) if cost_group.id.isnumeric() else helper.to_lex(cost_group.id), reverse=True)

        while len(cost_groups)>0:
            for cost_group in cost_groups:
                cols = [
                    str(cost_group.id),
                    str(cost_group.uid),
                    cost_group.name,
                    cost_group.description,
                    amount_str(cost_group.budget, self.currency)
                ]
                self.render_cc_nodes(self.treeWidget_cost_groups, cost_group, cols)
            tree_depth += 1
            cost_groups = self.app_data.project.get_cost_groups_of_level(tree_depth)
        helper.resize_tree_columns(self.treeWidget_cost_groups)
        # reselect the cost_grop if there was a selection
        sel_items = self.treeWidget_cost_groups.findItems(str(sel_cost_group.uid),
            QtCore.Qt.MatchFlag.MatchExactly
            |QtCore.Qt.MatchFlag.MatchRecursive,
            1) if sel_cost_group else list()
        if len(sel_items)>0:
            self.treeWidget_cost_groups.setCurrentItem(sel_items[0])

    def render_cc_nodes(self, tree_widget, cost_group, cols):
        parent_node = None
        if cost_group.parent is None:
            parent_node = tree_widget
        else:
            # Since we are rendering layer by layer, we can assume, that the parent node already exists and thus the below list is never empty
            parent_node = tree_widget.findItems(str(cost_group.parent.uid),
                QtCore.Qt.MatchFlag.MatchExactly
                |QtCore.Qt.MatchFlag.MatchRecursive,
                1)[0]
        helper.add_item_to_tree(content_item=cost_group,
                                            parent=parent_node,
                                            cols=cols)

    def render_cost_group_info(self, cost_group):
        if cost_group.is_not_deleted():
            args = vars(cost_group).copy()
            self.set_cost_group_data(**args,
                        sub_costgroups_budget=self.app_data.project.get_budget_sub_cost_groups(cost_group))
            self.set_invoices_of_cost_group_by_job(cost_group)
            self.activate_cost_group_buttons()
        else:
            self.reset_cost_group_info()

    def activate_cost_group_buttons(self):
        if len(self.treeWidget_cost_groups.selectedItems())>0:
            self.pushButton_edit_cost_group.setEnabled(True)
        else:
            self.pushButton_edit_cost_group.setEnabled(False)

    def reset_cost_group_info(self):
        self.set_cost_group_data()
        self.treeWidget_cost_group_invoices_by_job.clear()
        self.activate_cost_group_buttons()

    def set_cost_group_data(self, *, _uid=None, id="", name="", description="", budget=0, sub_costgroups_budget=0, parent=None, **kwargs):
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
        """ sub_cost_groups budget """
        self.label_sub_cost_groups_budget.setText(amount_str(sub_costgroups_budget))
        sub_cost_groups_budget_VAT_amount = sub_costgroups_budget * self.app_data.project.get_vat()
        sub_cost_groups_budget_w_VAT = sub_costgroups_budget + sub_cost_groups_budget_VAT_amount
        self.label_sub_cost_groups_budget_w_VAT.setText(amount_str(sub_cost_groups_budget_w_VAT))
        self.label_sub_cost_groups_budget_VAT_amount.setText(amount_str(sub_cost_groups_budget_VAT_amount))

    def set_invoices_of_cost_group_by_job(self, cost_group):
        self.treeWidget_cost_group_invoices_by_job.clear()
        invoices_of_cost_group = self.app_data.project.get_invoices_of_cost_group(cost_group)
        jobs = {invoice.job for invoice in invoices_of_cost_group}
        currency = self.app_data.project.get_currency()
        for job in jobs:
            job_node = QtWidgets.QTreeWidgetItem(self.treeWidget_cost_group_invoices_by_job)
            job_node.setData(1, QtCore.Qt.UserRole, job)
            invoices_of_cost_group_and_job = [invoice for invoice in invoices_of_cost_group if invoice.job is job]
            job_sum = 0
            for invoice in invoices_of_cost_group_and_job:
                helper.add_item_to_tree(content_item=invoice,
                                            parent=job_node,
                                            cols=["","","","", str(invoice.id), amount_str(invoice.amount_wout_prev_payments, currency)])
                job_sum += invoice.amount_wout_prev_payments
            job_node.setText(0, f"{job.id}")
            job_node.setText(1, f"{job.company.name}")
            job_node.setText(2, f"{amount_str(job.job_sum, currency)}")
            job_node.setText(3, f"{job.trade.name}")
            job_node.setText(4, f"{len(invoices_of_cost_group_and_job)}")
            job_node.setText(5, amount_str(job_sum, currency))
        helper.resize_tree_columns(self.treeWidget_cost_group_invoices_by_job)

    """ render
    #
    #   PROJECT-COST-CALCULATION-TAB
    #
    """
    @debug.log
    def render_project_cost_calculations(self, set_width=False):
        self.activate_pcc_buttons()
        amount_cols = ["total_cost"]
        date_cols = ["date"]
        helper.render_to_table(content=self.app_data.project.project_cost_calculations,
                                table=self.tableWidget_project_cost_calculations,
                                cols=self.project_cost_calculation_cols,
                                titles=self.app_data.titles,
                                amount_cols=amount_cols,
                                date_cols=date_cols,
                                currency=self.currency,
                                set_width=set_width)

    def render_pcc_info(self, pcc):
        if pcc.is_not_deleted():
            args = vars(pcc).copy()
            self.set_pcc_data(**args,
                                total_cost=pcc.total_cost)
            self.set_costs_of_cost_group_of_pcc(pcc)
            self.set_costs_of_trade_of_pcc(pcc)
            self.activate_pcc_buttons()
        else:
            self.reset_pcc_info()

    def activate_pcc_buttons(self):
        if self.tableWidget_project_cost_calculations.currentItem():
            self.pushButton_pcc_apply_budgets.setEnabled(True)
            self.pushButton_pcc_apply_budgets_cost_groups.setEnabled(True)
            self.pushButton_pcc_apply_budgets_trades.setEnabled(True)
            self.pushButton_edit_pcc.setEnabled(True)
            self.pushButton_copy_pcc.setEnabled(True)
            self.commandLinkButton_export_pcc_overviews.setEnabled(True)
            self.commandLinkButton_export_pcc_overviews_2.setEnabled(True)
            self.commandLinkButton_export_pcc_overviews_3.setEnabled(True)

            if len(self.treeWidget_pcc_trade_details.selectedItems())>0:
                self.pushButton_pcc_apply_budget_trade.setEnabled(True)
            else:
                self.pushButton_pcc_apply_budget_trade.setEnabled(False)

            if len(self.treeWidget_pcc_cost_group_details.selectedItems())>0:
                self.pushButton_pcc_apply_budget_cost_group.setEnabled(True)
            else:
                self.pushButton_pcc_apply_budget_cost_group.setEnabled(False)
        else:
            self.pushButton_pcc_apply_budgets.setEnabled(False)
            self.pushButton_pcc_apply_budgets_cost_groups.setEnabled(False)
            self.pushButton_pcc_apply_budgets_trades.setEnabled(False)
            self.pushButton_edit_pcc.setEnabled(False)
            self.pushButton_copy_pcc.setEnabled(False)
            self.pushButton_pcc_apply_budget_trade.setEnabled(False)
            self.pushButton_pcc_apply_budget_cost_group.setEnabled(False)
            self.commandLinkButton_export_pcc_overviews.setEnabled(False)
            self.commandLinkButton_export_pcc_overviews_2.setEnabled(False)
            self.commandLinkButton_export_pcc_overviews_3.setEnabled(False)

    def reset_pcc_info(self):
        self.treeWidget_pcc_cost_group_details.clear()
        self.treeWidget_pcc_trade_details.clear()
        self.set_pcc_data()
        self.activate_pcc_buttons()

    def set_pcc_data(self, *, _uid=None, name="", type=None, date=None, total_cost=0, **kwargs):
        """ meta data """
        self.label_pcc_uid.setText(_uid.labelize() if _uid else "-")

        self.label_pcc_name.setText(str(name))
        self.label_pcc_type.setText(type if type else "-")
        self.label_pcc_date.setText(qdate_to_str(date) if date else "-")

        """ total cost """
        self.label_pcc_total_cost.setText(amount_str(total_cost, self.currency))

    def set_costs_of_cost_group_of_pcc(self, pcc):
        # if a cost_group was selected, save here
        sel_items = self.treeWidget_pcc_cost_group_details.selectedItems()
        sel_cost_group = sel_items[0].data(1, QtCore.Qt.UserRole) if len(sel_items)>0 else None

        self.treeWidget_pcc_cost_group_details.clear()
        # go layer by layer
        tree_depth = 0
        cost_groups = self.app_data.project.get_cost_groups_of_level(tree_depth)
        while len(cost_groups)>0:
            for cost_group in cost_groups:
                cols = [
                    str(cost_group.id),
                    str(cost_group.uid),
                    str(len(pcc.get_cost_group_items(cost_group))),
                    amount_str(pcc.get_cost_group_prognosis(cost_group), self.currency),
                    amount_str(pcc.get_sub_cost_groups_prognosis(cost_group, self.app_data.project.cost_groups), self.currency)
                ]
                self.render_cc_nodes(self.treeWidget_pcc_cost_group_details, cost_group, cols)
            tree_depth += 1
            cost_groups = self.app_data.project.get_cost_groups_of_level(tree_depth)
        helper.resize_tree_columns(self.treeWidget_pcc_cost_group_details)
        # reselect the cost_grop if there was a selection
        sel_items = self.treeWidget_pcc_cost_group_details.findItems(str(sel_cost_group.uid),
            QtCore.Qt.MatchFlag.MatchExactly
            |QtCore.Qt.MatchFlag.MatchRecursive,
            1) if sel_cost_group else list()
        if len(sel_items)>0:
            self.treeWidget_pcc_cost_group_details.setCurrentItem(sel_items[0])


    def set_costs_of_trade_of_pcc(self, pcc):
        self.treeWidget_pcc_trade_details.clear()
        for trade in self.app_data.project.trades:
            cols = [
                str(trade.name),
                str(len(pcc.get_trade_items(trade))),
                amount_str(pcc.get_trade_prognosis(trade), self.currency)
            ]
            helper.add_item_to_tree(content_item=trade,
                                            parent=self.treeWidget_pcc_trade_details,
                                            cols=cols)
        helper.resize_tree_columns(self.treeWidget_pcc_trade_details)

    """ render
    #
    #   PEOPLE-TAB
    #
    """
    @debug.log
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
            self.label_person_house_number_2.setText(str(address.house_number))
            self.label_person_city_2.setText(address.city)
            self.label_person_state_2.setText(address.state)
            self.label_person_zipcode_2.setText(str(address.zipcode))
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
    #   VIEW INVERACTIONS
    #   functions that change views or current tabs
    #
    """
    @pyqtSlot()
    def button_set_job_view_sel_invoice(self):
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
    @pyqtSlot()
    @debug.log_info
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
            self.init_table_header()

    @debug.log_info
    def edit_project(self):
        helper.edit_project(self.app_data)
        self.update_ui()

    @debug.log_info
    def load_project(self):
        if self.app_data.project_loaded():
            reply = helper.save_curr_project_prompt(self, self.app_data)
            if reply:
                helper.load_project(self, self.app_data)
        else:
            helper.load_project(self, self.app_data)
        if self.app_data.project_loaded():
            self.update_ui()
            self.init_table_header()

    @debug.log_info
    def save_project(self):
        helper.save_project(self, self.app_data)

    @debug.log_info
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
    @debug.log_info
    def import_project(self):
        if self.app_data.project_loaded():
            reply = helper.save_curr_project_prompt(self, self.app_data)
            if reply:
                helper.import_project(self, self.app_data)
        else:
            helper.import_project(self, self.app_data)
        self.update_ui()

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
    @debug.log_info
    def input_client(self):
        person = helper.input_person(self.app_data)
        if person:
            self.app_data.project.client = person
            """ logging """
            debug.log(f"Client set to: {person.first_name}, {person.last_name}")

    """ func
    #
    #   PROJECT COST CALCULATION
    #
    """
    @debug.log_info
    def input_pcc_to_project(self):
        pcc = helper.input_pcc(self.app_data)
        self.update_ui()

    @debug.log_info
    def edit_pcc(self, pcc):
        pcc = helper.edit_pcc(self.app_data, pcc)
        if pcc:
            self.render_pcc_info(pcc)
            self.update_ui()
            self.activate_pcc_buttons()

    @debug.log_info
    def copy_pcc(self, pcc):
        pcc_copy = pcc.__copy__()
        self.app_data.project.add_pcc(pcc_copy)
        self.update_ui()
        self.activate_pcc_buttons()

    """ func
    #
    #   INVOICE
    #
    """
    @debug.log_info
    def input_invoice_to_project(self, sel_job=None):
        invoice = helper.input_invoice(self.app_data, sel_job=sel_job)
        self.update_ui()

    @debug.log_info
    def edit_invoice(self, invoice):
        invoice = helper.edit_invoice(self.app_data, invoice)
        if invoice:
            self.render_invoice_info(invoice)
            self.update_ui()
            self.activate_invoice_buttons()

    """ func
    #
    #   JOB
    #
    """
    @debug.log_info
    def input_job_to_project(self):
        job = helper.input_job(self.app_data)
        self.update_ui()

    @debug.log_info
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
    @debug.log_info
    def input_company_to_project(self):
        company = helper.input_company(self.app_data)
        self.update_ui()

    @debug.log_info
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
    @debug.log_info
    def input_trade_to_project(self):
        trade = helper.input_trade(self.app_data)
        self.update_ui()

    @debug.log_info
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
    @debug.log_info
    def input_cost_group_to_project(self):
        cost_group = helper.input_cost_group(self.app_data)
        self.update_ui()

    @debug.log_info
    def edit_cost_group(self, cost_group):
        cost_group = helper.edit_cost_group(self.app_data, cost_group)
        if cost_group:
            self.reset_cost_group_info()
            self.update_ui()
            self.activate_cost_group_buttons()

    """ func
    #
    #   Person
    #
    """
    @debug.log_info
    def input_person_to_project(self):
        person = helper.input_person(self.app_data)
        self.update_ui()

    @debug.log_info
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
    @debug.log_info
    def edit_app_config(self):
        config = helper.edit_app_config(self.app_data)
        if config:
            self.update_ui()

    @debug.log_info
    def edit_proj_config(self):
        config = helper.edit_proj_config(self.app_data)
        if config:
            self.update_ui()
    """
    #
    #   UTIL
    #
    #
    """
    """
    #   visually indicate, that an autosaving is in progress
    """
    def start_autosaving(self):
        pass

    def stop_autosaving(self):
        pass
    """
    #
    #   DEBUG FUNCTIONS
    #
    """
    @debug.log_info
    @pyqtSlot()
    def button_run_test(self):
        if self.app_data.debug_on():
            print("This is a test!")
            self.add_random_jobs()
            self.add_random_invoices()
            self.add_random_psds()
            self.add_random_job_additions()
            self.add_random_cost_calculations()
            self.add_contact_people()

            self.update_ui()

    @debug.log_info
    @pyqtSlot()
    def button_debug_add_invoices(self):
        if self.app_data.debug_on():
            print("This is a test!")
            self.add_random_invoices()
            self.add_random_psds()
            self.update_ui()

    #       TODO: Move all the testfunctions to the API file
    def add_random_jobs(self, max_jobs=50):
        number_of_jobs = random.randint(1, max_jobs)
        for i in range(number_of_jobs):
            company = random.choice(self.app_data.project.companies)
            id = self.app_data.project.get_max_job_number(company)+1
            trade = random.choice(self.app_data.project.trades)
            cost_group = random.choice(self.app_data.project.cost_groups)
            job_sum = rnd(random.random()*150000)

            input_job_args = {
                "company": company,
                "id": id,
                "trade": trade,
                "cost_group": cost_group,
                "job_sum": job_sum
            }
            self.app_data.project.input_new_job(input_job_args)

    def add_random_invoices(self, max_invoices=150):
        number_of_invoices = random.randint(1, max_invoices)
        for i in range(number_of_invoices):
            invoice_id_length = random.randint(5, 15)
            invoice_id = id_generator(invoice_id_length)
            job = random.choice(self.app_data.project.jobs)
            company = job.company
            cumulative = bool(random.getrandbits(1))
            w_discount = bool(random.getrandbits(1))
            invoice_date = QDate.currentDate()
            amount = rnd(random.random()*100000)
            if cumulative == 1:
                prev_invoices = self.app_data.project.get_prev_invoices(company=company, job=job, invoice_date=invoice_date, invoice_created_date=datetime.datetime.now())
                if len(prev_invoices)>0:
                    amount += prev_invoices[0].amount
            input_invoice_args = {
                "id": invoice_id,
                "job": job,
                "cumulative": cumulative,
                "company": company,
                "invoice_date": invoice_date,
                "amount": amount,
                "verified_amount": amount+rnd(random.random()*100)-rnd(random.random()*100),
                "rebate": rnd(random.random()*0.15),
                #"reduction_insurance_costs": rnd(random.random()*0.5),
                #"reduction_usage_costs": rnd(random.random()*0.5),
                "safety_deposit": rnd(random.random()*0.05),
                "discount": rnd(random.random()*0.05) if w_discount else 0,
                "due_date": QDate.currentDate(),
                "due_date_discount": QDate.currentDate() if w_discount else None,
            }
            self.app_data.project.input_new_invoice(input_invoice_args)

    def add_random_psds(self, max_psds=600):
        number_of_psds = random.randint(1, max_psds)
        for i in range(number_of_psds):
            job = random.choice(self.app_data.project.jobs)
            date = QDate.currentDate()
            amount = rnd(random.random()*500)
            comment_length = random.randint(0,350)
            comment = id_generator(comment_length)
            job.pay_safety_deposit(date, amount, comment)

    def add_random_job_additions(self, max_job_additions=600):
        number_of_job_additions = random.randint(1, max_job_additions)
        for i in range(number_of_job_additions):
            job = random.choice(self.app_data.project.jobs)
            date = QDate.currentDate()
            amount = rnd(random.random()*100000)
            name_length = random.randint(0,15)
            name = id_generator(name_length)
            comment_length = random.randint(0,350)
            comment = id_generator(comment_length)
            job.add_job_addition(date, name, amount, comment)

    def add_random_cost_calculations(self, max_cost_calculations=50):
        number_of_cost_calculations = random.randint(1, max_cost_calculations)
        for i in range(number_of_cost_calculations):

            name_length = random.randint(0,12)
            name = id_generator(name_length)
            type = random.choice(proj.ProjectCostCalculation.PCC_TYPES)
            pcc = proj.ProjectCostCalculation(name=name, date=QDate.currentDate(), type=type)
            self.app_data.project.add_pcc(pcc)
            number_of_inventory_items = random.randint(1, 150)
            for j in range(number_of_inventory_items):
                item = self.random_inventory_item()
                pcc.add_inventory_item(item)

    def random_inventory_item(self):
        name_length = random.randint(1,10)
        description_length = random.randint(0,350)
        trade = random.choice(self.app_data.project.trades)
        cost_group = random.choice(self.app_data.project.cost_groups)
        inventory_item_args = {
            "name": id_generator(name_length),
            "description": id_generator(description_length),
            "price_per_unit": rnd(random.random()*15),
            "units": random.randint(1,1500),
            "unit_type": random.choice(["m", "m²", "m³", "kg"]),
            "is_active": bool(random.getrandbits(1)),
            "trade": trade,
            "cost_group": cost_group
        }
        return proj.InventoryItem(**inventory_item_args)

    def add_contact_people(self):
        for company in self.app_data.project.companies:
            if company.contact_person is None:
                random_person = self.random_person()
                company.add_contact_person(random_person)

    def random_person(self, company=None):
        first_name_length = random.randint(1,10)
        last_name_length = random.randint(1,10)

        person_args = {
            "first_name": id_generator(first_name_length),
            "last_name": id_generator(last_name_length),
            "address": self.random_address(),
            "telephone": id_generator(size=8, chars=string.digits),
            "mobile": id_generator(size=10, chars=string.digits),
            "fax": id_generator(size=8, chars=string.digits),
            "email": id_generator(9),
            "company": company
        }
        return corp.Person(**person_args)

    def random_address(self):
        address_args = {
            "street": id_generator(size=1, chars=string.ascii_uppercase)+id_generator(size=12, chars=string.ascii_lowercase),
            "house_number": random.randint(1,200),
            "city": id_generator(size=1, chars=string.ascii_uppercase)+id_generator(size=5, chars=string.ascii_lowercase),
            "state": id_generator(size=1, chars=string.ascii_uppercase)+id_generator(size=8, chars=string.ascii_lowercase),
            "zipcode": id_generator(size=6, chars=string.digits),
            "country": id_generator(size=1, chars=string.ascii_uppercase)+id_generator(size=8, chars=string.ascii_lowercase),
        }
        return corp.Address(**address_args)


    def print_project_info(self):
        if self.app_data.project:
            debug.log(self.app_data.project.__dict__)
        else:
            debug.log("No Project yet!")
    def print_invoices(self):
        if self.app_data.project.invoices:
            for invoice in self.app_data.project.invoices:
                debug.log(vars(invoice))


"""
#
#   DEBUG FUNCTIONS
#
"""
def id_generator(size=10, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
