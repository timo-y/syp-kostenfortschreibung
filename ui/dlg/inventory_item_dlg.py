"""
#
#   INVENTORY_ITEM_DLG
#   This module creates an dialog with the necessary input fields to input an inventory item for the project cost calculation.
#
"""

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QDialogButtonBox

from ui import dlg, helper
from ui.helper import amount_str, amount_w_currency_str
from core.obj import proj

class InventoryItemDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, loaded_inventory_item=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.vat = app_data.project.get_vat()
        self.currency = app_data.project.get_currency()

        self.loaded_inventory_item = loaded_inventory_item

        self.initialize_ui()
        """ set title """
        dialog_title = "Neues Inventaritem"
        if loaded_inventory_item:
            dialog_title = f"Inventaritem ({loaded_inventory_item.name}) bearbeiten..."
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_button_actions()
        self.set_spin_box_actions()
        self.set_combo_box_actions()
        self.set_event_handler()

        if self.loaded_inventory_item:
            """ load trade data to input """
            loaded_args = vars(self.loaded_inventory_item).copy()
            self.checkBox_is_active.setChecked(self.loaded_inventory_item.is_active)
            self.set_input(**loaded_args)
            self.set_cost_group_to(self.loaded_inventory_item.cost_group)
            self.set_unit_type_to(self.loaded_inventory_item.unit_type)
            self.setup_combo_box_trades()
            self.set_trade_to(self.loaded_inventory_item.trade)

        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/inventory_item_dialog.ui', self)

    def setup_combo_boxes(self):
        self.setup_combo_box_cost_groups()
        self.setup_combo_box_trades()
        self.setup_combo_box_unit_type()

    def setup_combo_box_cost_groups(self):
        self.comboBox_cost_group.clear()
        self.comboBox_cost_group.addItem("Keine", None)
        for cost_group in self.app_data.project.cost_groups:
            self.comboBox_cost_group.addItem(str(cost_group.id), cost_group)

    def setup_combo_box_trades(self):
        self.comboBox_trade.clear()
        self.comboBox_trade.addItem("Gewerk auswählen...", None)
        for trade in self.app_data.project.trades:
            self.comboBox_trade.addItem(str(trade.name), trade)

    def setup_combo_box_unit_type(self):
        self.comboBox_unit_type.clear()
        self.comboBox_unit_type.addItem("Einheit", "E")
        for unit_type in proj.InventoryItem.DEFAULT_UNIT_TYPES:
            self.comboBox_unit_type.addItem(unit_type, unit_type)

    def activate_ok_button(self):
        args = self.get_input()
        if len(args["name"])>0 and args["cost_group"] and args["trade"]:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def update_ui(self):
        args = self.get_input()
        total_price = args["price_per_unit"] * args["units"]
        self.set_labels(total_price)
        self.activate_ok_button()

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        self.pushButton_add_cost_group.clicked.connect(self.button_add_cost_group)
        self.pushButton_add_trade.clicked.connect(self.button_add_trade)
        """ delete button """
        self.pushButton_delete.clicked.connect(lambda:helper.delete(self, self.loaded_inventory_item))

    def set_spin_box_actions(self):
        """ spinbox update """
        self.doubleSpinBox_units.valueChanged.connect(self.update_ui)
        self.doubleSpinBox_price_per_unit.valueChanged.connect(self.update_ui)

    def set_combo_box_actions(self):
        """ ok button """
        self.comboBox_cost_group.currentIndexChanged.connect(self.activate_ok_button)
        self.comboBox_trade.currentIndexChanged.connect(self.activate_ok_button)

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
    def button_add_cost_group(self):
        cost_group = helper.input_cost_group(self.app_data)
        if cost_group:
            self.setup_combo_box_cost_groups()
            self.set_cost_group_to(cost_group)

    def button_add_trade(self):
        trade = helper.input_trade(self.app_data)
        if trade:
            self.setup_combo_box_trades()
            self.set_trade_to(trade)

    """
    #
    #   FUNCTIONALITY
    #   Functions that let the dialog do something
    #
    """
    def add_new_inventory_item(self):
        input_inventory_item_args = dlg.open_inventory_item_dialog(self.app_data)
        if input_inventory_item_args:
            input_inventory_item = self.app_data.project.input_new_trade(input_trade_args)

    def edit_inventory_item(self, inventory_item):
        inventory_item_args = dlg.open_inventory_item_dialog(self.app_data, inventory_item)
        if inventory_item_args:
            inventory_item.update(**inventory_item_args)

    """
    #
    #   RENDER VIEWS
    #   functions to render the objects to the respective widgets
    #
    """
    def set_inventory(self, inventory):
        self.treeView_inventory.clear()
        total_price_sum = 0
        for inventory_item in inventory:
            helper.add_item_to_tree(content_item=inventory_item,
                                    cost_group=self.treeView_inventory,
                                    cols=[inventory_item.name,
                                        f"{inventory_item.units} {inventory_item.unit_type}",
                                        amount_w_currency_str(inventory_item.price_per_unit, self.currency),
                                        amount_w_currency_str(inventory_item.total_price, self.currency)])
            total_price_sum += inventory_item.total_price

        self.label_total_price_sum.setText(amount_w_currency_str(total_price_sum, self.currency))

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_cost_group_to(self, cost_group):
        index = self.comboBox_cost_group.findData(cost_group)
        self.comboBox_cost_group.setCurrentIndex(index)

    def set_trade_to(self, trade):
        index = self.comboBox_trade.findData(trade)
        if index<0:
            index = 0
        self.comboBox_trade.setCurrentIndex(index)

    def set_unit_type_to(self, unit_type):
        index = self.comboBox_unit_type.findData(unit_type)
        self.comboBox_unit_type.setCurrentIndex(index)

    def set_labels(self, total_price):
        """ total price """
        total_price_VAT_amount = total_price * self.vat
        total_price_w_VAT = total_price + total_price_VAT_amount
        self.label_total_price.setText(amount_str(total_price))
        self.label_total_price_w_VAT.setText(amount_str(total_price_w_VAT))
        self.label_total_price_VAT_amount.setText(amount_str(total_price_VAT_amount))

    def set_input(self, *, _uid=None, name, price_per_unit, units, description, **kwargs):
        """ meta data """
        self.label_uid.setText(_uid.labelize() if _uid else "-")

        self.lineEdit_name.setText(name)
        self.doubleSpinBox_price_per_unit.setValue(price_per_unit)
        self.doubleSpinBox_units.setValue(units)
        self.textEdit_description.setText(description)

    def get_input(self):
        args = {
                "name": self.lineEdit_name.text(),
                "price_per_unit": self.doubleSpinBox_price_per_unit.value(),
                "units": self.doubleSpinBox_units.value(),
                "unit_type": self.comboBox_unit_type.currentData(),
                "is_active": self.checkBox_is_active.isChecked(),
                "cost_group": self.comboBox_cost_group.currentData(),
                "trade": self.comboBox_trade.currentData(),
                "description": self.textEdit_description.toPlainText(),
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
