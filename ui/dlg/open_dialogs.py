"""
#
#   OPEN DIALOGS
#   open dialogs and return objects args
#
"""
from ui import dlg

from PyQt5 import QtWidgets

def open_project_dialog(app_data, loaded_project=None):
    project_dlg = dlg.ProjectDialog(app_data=app_data, loaded_project=loaded_project)
    input_project_args = project_dlg.exec_()
    if input_project_args:
        return input_project_args

def open_person_dialog(loaded_person=None):
    person_dlg = dlg.PersonDialog(loaded_person=loaded_person)
    dialog_output = person_dlg.exec_()
    if dialog_output:
        exit_state, input_person_args = dialog_output
        if exit_state==1:
            return input_person_args
        elif exit_state==-1:
            return "delete"

def open_address_dialog(loaded_address=None):
    address_dlg = dlg.AddressDialog(loaded_address=loaded_address)
    dialog_output = address_dlg.exec_()
    if dialog_output:
        exit_state, input_address_args = dialog_output
        if exit_state==1:
            return input_address_args
        elif exit_state==-1:
            return "delete"

def open_invoice_dialog(app_data, sel_job=None, loaded_invoice=None):
    invoice_dlg = dlg.InvoiceDialog(app_data=app_data, sel_job=sel_job, loaded_invoice=loaded_invoice)
    dialog_output = invoice_dlg.exec_()
    if dialog_output:
        exit_state, input_invoice_args = dialog_output
        if exit_state==1:
            return input_invoice_args
        elif exit_state==-1:
            return "delete"

def open_job_dialog(app_data, sel_company=None, loaded_job=None):
    job_dlg = dlg.JobDialog(app_data=app_data, sel_company=sel_company, loaded_job=loaded_job)
    dialog_output = job_dlg.exec_()
    if dialog_output:
        exit_state, input_job_args = dialog_output
        if exit_state==1:
            return input_job_args
        elif exit_state==-1:
            return "delete"

def open_company_dialog(app_data, loaded_company=None):
    company_dlg = dlg.CompanyDialog(app_data=app_data, loaded_company=loaded_company)
    dialog_output = company_dlg.exec_()
    if dialog_output:
        exit_state, input_company_args = dialog_output
        if exit_state==1:
            return input_company_args
        elif exit_state==-1:
            return "delete"

def open_trade_dialog(app_data, loaded_trade=None):
    trade_dlg = dlg.TradeDialog(app_data=app_data, loaded_trade=loaded_trade)
    dialog_output = trade_dlg.exec_()
    if dialog_output:
        exit_state, input_trade_args = dialog_output
        if exit_state==1:
            return input_trade_args
        elif exit_state==-1:
            return "delete"

def open_cost_group_dialog(app_data, loaded_cost_group=None):
    cost_group_dlg = dlg.CostGroupDialog(app_data=app_data, loaded_cost_group=loaded_cost_group)
    dialog_output = cost_group_dlg.exec_()
    if dialog_output:
        exit_state, input_cost_group_args = dialog_output
        if exit_state==1:
            return input_cost_group_args
        elif exit_state==-1:
            return "delete"

def open_config_dialog(loaded_config=None, default_config=None):
    config_dlg = dlg.ConfigDialog(loaded_config=loaded_config, default_config=default_config)
    input_config_args = config_dlg.exec_()
    if input_config_args:
        return input_config_args

def open_pay_safety_deposit_dialog():
    pay_safety_deposit_dlg = dlg.PaySafetyDepositDialog()
    pay_safety_deposit_args = pay_safety_deposit_dlg.exec_()
    if pay_safety_deposit_args:
        return pay_safety_deposit_args

def open_delete_prompt(dialog):
    reply = QtWidgets.QMessageBox.question(dialog, 'Löschen', 'Sicher löschen?',
    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
    return reply

def open_save_curr_project_prompt(dialog):
    reply = QtWidgets.QMessageBox.question(dialog, 'Projekt geöffnet...', 'Ein Projekt ist bereits geöffnet. Möchten Sie speichern bevor ein neues geladen wird?',
    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
    return reply

