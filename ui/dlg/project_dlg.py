"""
#
#   PROJECT_DLG
#   This module creates an project dialog with the necessary input fields.
#
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate

from ui import dlg
from core.obj import (proj, corp)

class ProjectDialog(QtWidgets.QDialog):
    def __init__(self, *, app_data, loaded_project=None):
        super().__init__()
        """ create local variables """
        self.app_data = app_data
        self.loaded_project = loaded_project
        self.sel_client = None

        self.initialize_ui()
        """ set title """
        dialog_title = f"Projekt ({loaded_project.identifier}) bearbeiten..." if loaded_project else "Neue Projekt"
        self.setWindowTitle(dialog_title)
        """ fixed window size """
        self.setFixedSize(self.size())
        """ activate UI """
        self.setup_combo_boxes()
        self.set_button_actions()
        self.set_check_box_actions()
        self.set_combo_box_actions()
        self.set_event_handler()
        self.set_date_today()


        if self.loaded_project:
            """ load invoice data to input """
            loaded_args = vars(self.loaded_project).copy()
            self.set_input(**loaded_args)

        self.update_ui()

    """
    #
    #   INITIALIZE, EN/-DISABLE & UPDATE THE GUI
    #
    #
    """
    def initialize_ui(self):
        uic.loadUi('ui/dlg/project_dialog.ui', self)

    def setup_combo_boxes(self):
        self.setup_combo_box_building_class()
        self.setup_combo_box_planning_status()

    def setup_combo_box_building_class(self):
        self.comboBox_building_class.clear()
        self.comboBox_building_class.addItem("Gebäudeklasse auswählen...", None)

        building_classes = self.app_data.config["building_classes"]

        for building_class in building_classes:
            self.comboBox_building_class.addItem(building_class, building_class)

    def setup_combo_box_planning_status(self):
        self.comboBox_planning_status.clear()
        self.comboBox_planning_status.addItem("Planungsstand auswählen...", None)

        planning_phases =  self.app_data.config["planning_phases"]

        for planning_phase in planning_phases:
            self.comboBox_planning_status.addItem(planning_phase[0], planning_phase)

    def update_ui(self):
        pass

    """
    #
    #   SIGNALS, ACTIONS & BUTTONS
    #   catch the signals from the mainwindow and set functions to them
    #
    """
    def set_button_actions(self):
        """ date buttons """
        self.pushButton_commissioned_date_set_today.clicked.connect(lambda:self.dateEdit_commissioned_date.setDate(QDate.currentDate()))
        self.pushButton_planning_finished_date_set_today.clicked.connect(lambda:self.dateEdit_planning_finished_date.setDate(QDate.currentDate()))
        self.pushButton_billed_date_set_today.clicked.connect(lambda:self.dateEdit_billed_date.setDate(QDate.currentDate()))

        """ add client """
        self.pushButton_add_client.clicked.connect(self.choose_client)
        self.pushButton_add_new_client.clicked.connect(self.add_new_client)

    def set_check_box_actions(self):
        self.checkBox_commissioned.toggled.connect(self.dateEdit_commissioned_date.setEnabled)
        self.checkBox_commissioned.toggled.connect(self.pushButton_commissioned_date_set_today.setEnabled)
        self.checkBox_planning_finished.toggled.connect(self.dateEdit_planning_finished_date.setEnabled)
        self.checkBox_planning_finished.toggled.connect(self.pushButton_planning_finished_date_set_today.setEnabled)
        self.checkBox_billed.toggled.connect(self.dateEdit_billed_date.setEnabled)
        self.checkBox_billed.toggled.connect(self.pushButton_billed_date_set_today.setEnabled)
        self.checkBox_execution_period.toggled.connect(self.dateEdit_execution_period_date_1.setEnabled)
        self.checkBox_execution_period.toggled.connect(self.dateEdit_execution_period_date_2.setEnabled)
        self.checkBox_execution_period.toggled.connect(self.label_to.setEnabled)

    def set_combo_box_actions(self):
        self.comboBox_planning_status.currentIndexChanged.connect(self.set_planning_phase_desc)

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
    def choose_client(self):
        # open project.people and choose person
        pass

    def add_new_client(self):
        input_client_args = dlg.open_person_dialog()
        if input_client_args:
            self.sel_client = self.app_data.project.input_new_person(input_client_args)

    """
    #
    #   UTILITY FUNCTIONS
    #
    #
    """
    def set_planning_phase_desc(self):
        planning_phase = self.comboBox_planning_status.currentData()
        self.label_planning_status.setText(planning_phase[1] if planning_phase else "-")

    def set_date_today(self):
        self.dateEdit_commissioned_date.setDate(QDate.currentDate())
        self.dateEdit_planning_finished_date.setDate(QDate.currentDate())
        self.dateEdit_billed_date.setDate(QDate.currentDate())
        self.dateEdit_execution_period_date_1.setDate(QDate.currentDate())
        self.dateEdit_execution_period_date_2.setDate(QDate.currentDate())

    def set_building_class_to(self, building_class):
        index = self.comboBox_building_class.findData(building_class)
        self.comboBox_building_class.setCurrentIndex(index)

    def set_planning_status_to(self, planning_status):
        index = self.comboBox_planning_status.findData(planning_status)
        self.comboBox_planning_status.setCurrentIndex(index)

    def set_labels(self, *, client):
        """ client """
        self.label_client_first_name.setText(client.first_name)
        self.label_client_last_name.setText(client.last_name)
        self.label_client_street_a_number.setText(" ,".join([client.address.street, client.address.house_number]))
        self.label_client_zip_a_state.setText(" ,".join([client.address.zipcode, client.address.state]))

    def set_input(self, *, _uid="-", identifier="", construction_scheme="", _address=None, _client=None,
                    _project_data=None, commissioned_date=QDate.currentDate(), planning_finished_date=QDate.currentDate(),
                    billed_date=QDate.currentDate(), planning_status=None, **kwargs
                    ):
        address = _address
        client = _client
        project_data = _project_data
        """ meta data """
        self.label_uid.setText(_uid.labelize())
        """ project """
        self.lineEdit_id.setText(identifier)
        self.lineEdit_construction_scheme.setText(construction_scheme)
        """ address """
        if address:
            self.lineEdit_street.setText(address.street)
            self.lineEdit_house_number.setText(address.house_number)
            self.lineEdit_city.setText(address.city)
            self.lineEdit_state.setText(address.state)
            self.lineEdit_zipcode.setText(address.zipcode)
            self.lineEdit_country.setText(address.country)
        """ project data """
        if project_data:
            self.lineEdit_commissioned_services.setText(project_data.commissioned_services)
            self.doubleSpinBox_property_size.setValue(project_data.property_size)
            self.doubleSpinBox_usable_floor_space_nuf.setValue(project_data.usable_floor_space_nuf)
            self.doubleSpinBox_usable_floor_space_bgf.setValue(project_data.usable_floor_space_bgf)
            self.doubleSpinBox_construction_costs_kg300_400.setValue(project_data.construction_costs_kg300_400)
            self.doubleSpinBox_production_costs.setValue(project_data.production_costs)
            self.doubleSpinBox_contract_fee.setValue(project_data.contract_fee)
            self.set_building_class_to(project_data.building_class)
            if project_data.execution_period:
                self.checkBox_execution_period.setChecked(True)
                self.dateEdit_execution_period_date_1.setDate(project_data.execution_period[0])
                self.dateEdit_execution_period_date_2.setDate(project_data.execution_period[1])
            else:
                self.checkBox_execution_period.setChecked(False)

        """ dates """
        if commissioned_date:
            self.checkBox_commissioned.setChecked(True)
            self.dateEdit_commissioned_date.setDate(commissioned_date)
        else:
            self.checkBox_commissioned.setChecked(False)
        if planning_finished_date:
            self.checkBox_planning_finished.setChecked(True)
            self.dateEdit_planning_finished_date.setDate(planning_finished_date)
        else:
            self.checkBox_planning_finished.setChecked(False)
        if billed_date:
            self.checkBox_billed.setChecked(True)
            self.dateEdit_billed_date.setDate(billed_date)
        else:
            self.checkBox_billed.setChecked(False)

        self.set_planning_status_to(planning_status)

    def get_input(self):
        address = {
                "street": self.lineEdit_street.text(),
                "house_number": self.lineEdit_house_number.text(),
                "city": self.lineEdit_city.text(),
                "state": self.lineEdit_state.text(),
                "zipcode": self.lineEdit_zipcode.text(),
                "country": self.lineEdit_country.text()
            }
        project_data = {
                "commissioned_services": self.lineEdit_commissioned_services.text(),
                "property_size": self.doubleSpinBox_property_size.value(),
                "usable_floor_space_nuf": self.doubleSpinBox_usable_floor_space_nuf.value(),
                "usable_floor_space_bgf": self.doubleSpinBox_usable_floor_space_bgf.value(),
                "building_class": self.comboBox_building_class.currentData(),
                "construction_costs_kg300_400": self.doubleSpinBox_construction_costs_kg300_400.value(),
                "production_costs": self.doubleSpinBox_production_costs.value(),
                "contract_fee": self.doubleSpinBox_contract_fee.value(),
                "execution_period": (self.dateEdit_execution_period_date_1.date(), self.dateEdit_execution_period_date_2.date()) if self.checkBox_execution_period.isChecked() else None
            }
        args = {
                "identifier": self.lineEdit_id.text(),
                "construction_scheme": self.lineEdit_construction_scheme.text(),
                "address": corp.Address(**address),
                "client": self.sel_client,
                "project_data": proj.ProjectData(**project_data),
                "commissioned_date": self.dateEdit_commissioned_date.date() if self.checkBox_commissioned.isChecked() else None,
                "planning_finished_date": self.dateEdit_planning_finished_date.date() if self.checkBox_planning_finished.isChecked() else None,
                "billed_date": self.dateEdit_billed_date.date() if self.checkBox_billed.isChecked() else None,
                "planning_status": self.comboBox_planning_status.currentData()
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
