"""
#
#   TRADE_DLG
#   This module creates an trade dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QDialogButtonBox

from ui import dlg, helper
from ui.helper import str_to_float, two_inputs_to_float, amount_str, rnd


class TradeDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, loaded_trade=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.default_vat = app_data.project.config["default_vat"]
        self.currency = app_data.project.config["currency"]
        self.trades = app_data.project.trades
        self.loaded_trade = loaded_trade

        self.initialize_ui()
        """ set title """
        dialog_title = (
            f"Gewerk ({loaded_trade.name}) bearbeiten..."
            if loaded_trade
            else "Neues Gewerk"
        )
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_button_actions()
        self.set_combo_box_actions()
        self.set_event_handler()
        self.set_validators()
        self.set_default_labels()

        if self.loaded_trade:
            """activate delete button"""
            self.pushButton_delete.setEnabled(True)
            """ load trade data to input """
            loaded_args = self.loaded_trade.__dict__.copy()
            self.set_input(**loaded_args)

        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """

    def initialize_ui(self):
        uic.loadUi("ui/dlg/trade_dialog.ui", self)  # Load the .ui file

    def setup_combo_boxes(self):
        pass

    def set_default_labels(self):
        pass

    def set_validators(self):
        # to allow only int
        onlyInt = QtGui.QIntValidator()
        self.lineEdit_budget_1.setValidator(onlyInt)
        self.lineEdit_budget_2.setValidator(onlyInt)

    def activate_ok_button(self):
        args = self.get_input()
        if len(args["name"]) > 0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def update_ui(self):
        # """ update the values of the labels """#
        args = self.get_input()
        budget_VAT_amount = args["budget"] * self.app_data.project.config["default_vat"]
        budget_w_VAT = args["budget"] + budget_VAT_amount
        self.set_labels(budget_w_VAT=budget_w_VAT, budget_VAT_amount=budget_VAT_amount)
        self.activate_ok_button()

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """

    def set_button_actions(self):
        """delete button"""
        self.pushButton_delete.clicked.connect(
            lambda: helper.delete(self, self.loaded_trade)
        )

    def set_combo_box_actions(self):
        pass

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
            self.setup_combo_box_trades()

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """

    def set_labels(self, *, budget_w_VAT, budget_VAT_amount):
        """budget"""
        self.label_budget_w_VAT.setText(amount_str(budget_w_VAT))
        self.label_budget_VAT_amount.setText(amount_str(budget_VAT_amount))

    def set_input(self, *, _uid=None, name="", comment="", budget=0, **kwargs):
        """meta data"""
        self.label_uid.setText(_uid.labelize() if _uid else "-")

        self.lineEdit_name.setText(str(name))
        self.textEdit_comment.setText(str(comment))

        """ budget """
        self.lineEdit_budget_1.setText(str(int(budget)) if int(budget) > 0 else "")
        self.lineEdit_budget_2.setText(
            f"{int(rnd(budget-int(budget))*100):02d}"
            if budget - int(budget) > 0
            else ""
        )

    def get_input(self):
        args = {
            "name": self.lineEdit_name.text(),
            "comment": self.textEdit_comment.toPlainText(),
            "budget": two_inputs_to_float(
                self.lineEdit_budget_1, self.lineEdit_budget_2
            ),
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
