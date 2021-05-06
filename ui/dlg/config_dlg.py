"""
#
#   CONFIG_DLG
#   This module creates a dialog to edit configs in a plain text field.
#
"""
import json
from PyQt5 import QtWidgets, uic


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, loaded_config=None, default_config=None):
        super().__init__()

        """ create local variables """
        self.default_config = default_config

        self.initialize_ui()
        """ fixed window size """
        # self.setFixedSize(self.size())
        """ activate UI """
        self.set_button_actions()
        self.set_update_trigger()

        if loaded_config:
            self.set_input(self.dct_to_str(loaded_config))

        self.update()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """

    def initialize_ui(self):
        uic.loadUi("ui/dlg/config_dialog.ui", self)

    def update(self):
        args_raw = self.get_input_raw()
        if self.default_config:
            default_config_str = self.dct_to_str(self.default_config).encode("utf8")
            if args_raw["config"] != default_config_str:
                self.pushButton_reset_to_default.setEnabled(True)
            else:
                self.pushButton_reset_to_default.setEnabled(False)
        else:
            self.pushButton_reset_to_default.setEnabled(False)

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """

    def set_button_actions(self):
        """reset to default config"""
        self.pushButton_reset_to_default.clicked.connect(self.reset_to_default)

    def set_update_trigger(self):
        self.pushButton_reset_to_default.clicked.connect(self.update)
        self.textEdit_config.textChanged.connect(self.update)

    def set_event_handler(self):
        self.keyReleaseEvent = self.eventHandler
        self.mouseReleaseEvent = self.eventHandler

    """ add event handler """

    def eventHandler(self, event):
        self.update()

    """
    #
    #   FUNCTIONALITY
    #
    #
    """

    def reset_to_default(self):
        if self.default_config:
            default_config_str = self.dct_to_str(self.default_config)
            self.set_input(default_config_str)

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """

    def set_input(self, config_str):
        self.textEdit_config.setText(config_str)

    def get_input(self):
        args = {"config": json.loads(self.textEdit_config.toPlainText().encode("utf8"))}
        return args

    def get_input_raw(self):
        args = {"config": self.textEdit_config.toPlainText().encode("utf8")}
        return args

    def dct_to_str(self, dct):
        json_string = (
            json.dumps(dct, indent=4, ensure_ascii=False).encode("utf8").decode("utf8")
        )
        return json_string

    def str_to_dct(self, str):
        json_dct = json.loads(str.encode("utf8"))
        return json_dct

    """
    #
    #   EXEC
    #
    #
    """

    def exec_(self):
        ok = super().exec_()
        if ok:
            input_dct = self.get_input()
            return input_dct
