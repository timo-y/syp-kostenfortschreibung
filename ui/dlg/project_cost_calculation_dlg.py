"""
#
#   PROJECTCOSTCALCULATION_DLG
#   This module creates an dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtCore import QDate

from core.obj import proj
from ui import dlg, helper
from ui.helper import amount_w_currency_str

class ProjectCostCalculationDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, loaded_pcc=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.default_vat = app_data.project.get_vat() # TODO: remove?
        self.currency = app_data.project.get_currency()

        self.inventory = loaded_pcc.inventory if loaded_pcc else list()

        self.loaded_pcc = loaded_pcc

        self.initialize_ui()
        """ set title """
        dialog_title = "Neue Kostenberechnung"
        if loaded_pcc:
            dialog_title = f"Kostenberechnung ({loaded_pcc.name}, vom {loaded_pcc.date.toPyDate()}) bearbeiten..."
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.set_date_today()
        self.setup_combo_boxes()
        self.set_widget_actions()
        self.set_button_actions()
        self.set_combo_box_actions()
        self.set_event_handler()

        if self.loaded_pcc:
            """ activate delete button """
            self.pushButton_delete.setEnabled(True)
            """ load trade data to input """
            loaded_args = vars(self.loaded_pcc).copy()
            self.set_input(**loaded_args)

        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/project_cost_calculation_dialog.ui', self)
        """ TODO: figure out where to put this """
        tree_widget_cols = ["is_active", "name", "cost_group", "trade", "units", "unit_type", "price_per_unit", "total_price"] # maybe put on top of file
        self.treeWidget_inventory.setHeaderLabels([self.app_data.titles[col] for col in tree_widget_cols])

    def set_date_today(self):
        self.dateEdit_date.setDate(QDate.currentDate())

    def setup_combo_boxes(self):
        self.setup_combo_box_type()
        self.setup_combo_box_filter_by_cost_group()
        self.setup_combo_box_filter_by_trade()

    def setup_combo_box_type(self):
        self.comboBox_type.clear()
        self.comboBox_type.addItem("Typ auswählen...", None)
        for type in proj.ProjectCostCalculation.PCC_TYPES:
            self.comboBox_type.addItem(str(type), type)

    def setup_combo_box_filter_by_cost_group(self):
        self.comboBox_filter_cost_group.clear()
        self.comboBox_filter_cost_group.addItem("Nach Kostengruppe filtern", None)
        for cost_group in self.app_data.project.cost_groups:
            self.comboBox_filter_cost_group.addItem(str(cost_group.id), cost_group)

    def setup_combo_box_filter_by_trade(self):
        sel_cost_group = self.comboBox_filter_cost_group.currentData()
        self.comboBox_filter_trade.clear()
        self.comboBox_filter_trade.addItem("Nach Gewerk filtern", None)
        if sel_cost_group:
            """ activate combobox only if there exists at least one trade """
            got_a_trade = False
            for trade in self.app_data.project.trades:
                if trade.cost_group is sel_cost_group.get_main_cost_group():
                    got_a_trade = True
                    self.comboBox_filter_trade.addItem(str(trade.name), trade)
            if got_a_trade:
                self.comboBox_filter_trade.setEnabled(True)
            else:
                self.comboBox_filter_trade.setEnabled(False)
        else:
            self.comboBox_filter_trade.setEnabled(False)

    def activate_reset_filter_button(self):
        if self.comboBox_filter_cost_group.currentData():
            self.pushButton_reset_filter.setEnabled(True)
        else:
            self.pushButton_reset_filter.setEnabled(False)

    def activate_inventory_item_buttons(self):
        if self.treeWidget_inventory.currentItem():
            self.pushButton_edit_inventory_item.setEnabled(True)
            self.pushButton_remove_inventory_item.setEnabled(True)
        else:
            self.pushButton_edit_inventory_item.setEnabled(False)
            self.pushButton_remove_inventory_item.setEnabled(False)

    def activate_ok_button(self):
        args = self.get_input()
        if len(args["name"])>0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def update_ui(self):
        self.set_labels()
        self.set_inventory(self.get_inventory())
        self.activate_inventory_item_buttons()
        self.activate_reset_filter_button()
        self.activate_ok_button()

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_widget_actions(self):
        self.treeWidget_inventory.itemDoubleClicked.connect(self.double_click_inventory_item_tree)
        self.treeWidget_inventory.itemClicked.connect(self.activate_inventory_item_buttons)

    def set_button_actions(self):
        self.pushButton_reset_filter.clicked.connect(self.button_reset_filter)
        self.pushButton_add_inventory_item.clicked.connect(self.button_new_inventory_item)
        self.pushButton_edit_inventory_item.clicked.connect(self.button_edit_inventory_item)
        self.pushButton_remove_inventory_item.clicked.connect(self.button_remove_inventory_item)
        """ delete button """
        self.pushButton_delete.clicked.connect(lambda:helper.delete(self, self.loaded_pcc))

    def set_combo_box_actions(self):
        self.comboBox_filter_cost_group.currentIndexChanged.connect(self.setup_combo_box_filter_by_trade)
        self.comboBox_filter_cost_group.currentIndexChanged.connect(self.update_ui)
        self.comboBox_filter_trade.currentIndexChanged.connect(self.update_ui)

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
    def button_new_inventory_item(self):
        self.add_new_inventory_item()

    def button_edit_inventory_item(self):
        inventory_item = self.treeWidget_inventory.currentItem().data(1, QtCore.Qt.UserRole)
        self.edit_inventory_item(inventory_item)

    def button_remove_inventory_item(self):
        inventory_item = self.treeWidget_inventory.currentItem().data(1, QtCore.Qt.UserRole)
        self.remove_inventory_item(inventory_item)

    def double_click_inventory_item_tree(self, item):
        inventory_item = item.data(1, QtCore.Qt.UserRole)
        self.edit_inventory_item(inventory_item)

    def button_reset_filter(self):
        self.setup_combo_boxes()

    """
    #
    #   FUNCTIONALITY
    #   Functions that let the dialog do something
    #
    """
    def add_new_inventory_item(self):
        input_inventory_item = helper.input_inventory_item(self.app_data)
        if input_inventory_item:
            self.inventory.append(input_inventory_item)
            self.update_ui()

    def edit_inventory_item(self, inventory_item):
        helper.edit_inventory_item(self.app_data, inventory_item)
        self.update_ui()

    def remove_inventory_item(self, inventory_item):
        reply = helper.delete_prompt(self)
        if reply:
            self.inventory.remove(inventory_item)
            self.update_ui()

    """
    #
    #   RENDER VIEWS
    #   functions to render the objects to the respective widgets
    #
    """
    def set_inventory(self, inventory):
        self.treeWidget_inventory.clear()
        total_price_sum = 0
        for inventory_item in inventory:
            helper.add_item_to_tree(content_item=inventory_item,
                                    parent=self.treeWidget_inventory,
                                    cols=[f"{inventory_item.is_active}",
                                        inventory_item.name,
                                        f"{inventory_item.cost_group.id} / {inventory_item.cost_group.name}",
                                        str(inventory_item.trade.name),
                                        f"{inventory_item.units}",
                                        f"{inventory_item.unit_type}",
                                        amount_w_currency_str(inventory_item.price_per_unit, self.currency),
                                        amount_w_currency_str(inventory_item.total_price, self.currency)])
            total_price_sum += inventory_item.total_price if inventory_item.is_active else 0

        self.label_total_price_sum.setText(amount_w_currency_str(total_price_sum, self.currency))

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_type_to(self, type):
        index = self.comboBox_type.findData(type)
        self.comboBox_type.setCurrentIndex(index)

    def get_inventory(self):
        cost_group = self.comboBox_filter_cost_group.currentData()
        trade = self.comboBox_filter_trade.currentData()
        inventory = self.inventory
        if trade:
            inventory = [item for item in self.inventory if item.trade is trade]
        elif cost_group:
            inventory = [item for item in self.inventory if item.cost_group is cost_group or item.cost_group.is_sub_group_of(cost_group)]
        return inventory

    def set_labels(self):
        # TODO
        pass

    def set_input(self, *, _uid=None, name, type, date, **kwargs):
        """ meta data """
        self.label_uid.setText(_uid.labelize() if _uid else "-")

        self.lineEdit_name.setText(name)
        self.set_type_to(type)
        self.dateEdit_date.setDate(date)

    def get_input(self):
        args = {
                "name": self.lineEdit_name.text(),
                "type": self.comboBox_type.currentData(),
                "date": self.dateEdit_date.date(),
                "inventory": self.inventory,
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
