"""
#
#   HELPER
#   Module with helper functions that connect the api to the ui.
#
#
"""
import debug

import os
import datetime

from ui import dlg
from ui import customqt

from PyQt5 import QtWidgets, QtCore

"""
#
#   INPUT, ADD and EDIT
#   Input, add and edit objects.
#
"""
def save_curr_project_prompt(dialog, app_data):
    reply = dlg.open_save_curr_project_prompt(dialog)
    if reply == QtWidgets.QMessageBox.Save:
        save_project(dialog, app_data)
    elif reply == QtWidgets.QMessageBox.Cancel:
        return False
    return True

""" i,a&e
#
#   PROJECT
#
"""
def input_new_project(app_data):
    # TODO: If current project is not empty ask to save
    # open dialog and create project
    # load default companies and trades
    input_project_args = dlg.open_project_dialog(app_data=app_data)
    if input_project_args:
        app_data.new_project(input_project_args)
        """ logging """
        debug.log(f"New project created: {app_data.project.identifier}, {str(app_data.project.uid)}")


def edit_project(app_data):
    if app_data.project:
        input_project_args = dlg.open_project_dialog(app_data=app_data, loaded_project=app_data.project)
        if input_project_args:
            app_data.project.update(**input_project_args)
            """ logging """
            debug.log(f"Project edited: {app_data.project.identifier}, {str(app_data.project.uid)}")

def load_project(mainwindow, app_data):
    save_dir_path = app_data.get_save_dir()
    f_dialog = QtWidgets.QFileDialog(directory=save_dir_path)
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Projekt öffnen...",  "", "Project saves (*.project);;All Files (*)")
    if file_path:
        app_data.load_project(file_path)
        """ logging """
        debug.log(f"Project loaded: \"{app_data.project.identifier}\"")

def save_project(mainwindow, app_data):
    if app_data.project:
        if app_data.project.has_been_saved():
            save_path = app_data.project.get_usersave_path()
            app_data.save_project(save_path)
            """ logging """
            debug.log(f"Project saved: \"{app_data.project.identifier}\"")
        else:
            save_project_as(mainwindow, app_data)

def save_project_as(mainwindow, app_data):
    if app_data.project:
        save_dir_path = os.path.join(app_data.get_save_dir(), app_data.project.identifier+".project")
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Speichern...", save_dir_path, "Project save (*.project)")
        if save_path:
            app_data.save_project(save_path)
            """ logging """
            debug.log(f"Project saved: \"{app_data.project.identifier}\" as {save_path}")

""" i,a&e
#
#   EXPORT
#
"""
def export_companies(mainwindow, app_data):
    if app_data.project:
        filename = "companies.json"
        save_dir_path = os.path.join(app_data.get_save_dir(), filename)
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Firmenverzeichniss exportieren...", save_dir_path, "Company-JSON (*.json)")
        if save_path:
            app_data.export_companies(save_path)
            """ logging """
            debug.log(f"Companies exported to {save_path}")

def export_trades(mainwindow, app_data):
    if app_data.project:
        filename = "trades.json"
        save_dir_path = os.path.join(app_data.get_save_dir(), filename)
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Gewerkeverzeichniss exportieren...", save_dir_path, "Trade-JSON (*.json)")
        if save_path:
            app_data.export_trades(save_path)
            """ logging """
            debug.log(f"Trades exported to {save_path}")

""" i,a&e
#
#   IMPORT
#
"""
def import_companies(mainwindow, app_data):
    save_dir_path = app_data.get_save_dir()
    f_dialog = QtWidgets.QFileDialog(directory=save_dir_path)
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Firmenverzeichniss importieren...",  "", "Company-JSONs (*.json);;All Files (*)")
    if file_path:
        app_data.import_companies(file_path)
        """ logging """
        debug.log(f"Companies successfully imported")


def import_trades(mainwindow, app_data):
    save_dir_path = app_data.get_save_dir()
    f_dialog = QtWidgets.QFileDialog(directory=save_dir_path)
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Gewerkeverzeichniss importieren...",  "", "Trade-JSONs (*.json);;All Files (*)")
    if file_path:
        app_data.import_trades(file_path)
        """ logging """
        debug.log(f"Trades successfully imported")

""" i,a&e
#
#   ADDRESS
#
"""
def input_address(app_data):
    input_address_args = dlg.open_address_dialog()
    if input_address_args:
        address = corp.Address(**input_address_args)
        """ logging """
        debug.log(f"Address added: {address}")
        return address

""" i,a&e
#
#   PERSON
#
"""
def input_person(app_data):
    input_person_args = dlg.open_person_dialog(app_data=app_data)
    if input_person_args:
        person = app_data.project.input_new_person(input_person_args)
        """ logging """
        debug.log(f"New person added: {person.first_name}, {person.last_name}")
        return person

def edit_person(app_data):
    person_args = dlg.open_person_dialog(app_data=app_data, loaded_person=person)
    if person_args:
        if person_args == "delete":
            app_data.project.delete_person(person)
            """ logging """
            debug.log(f"Person deleted: {person.first_name}, {person.last_name}")
        else:
            person.update(person_args)
            """ logging """
            debug.log(f"Existing person edited: {person.first_name}, {person.last_name}")
        return person

""" i,a&e
#
#   INVOICE
#
"""
@debug.log
def input_invoice(app_data, sel_job=None):
    input_invoice_args = dlg.open_invoice_dialog(app_data=app_data, sel_job=sel_job)
    if input_invoice_args:
        invoice = app_data.project.input_new_invoice(input_invoice_args)
        """ logging """
        debug.log(f"New invoice added: {invoice.id}, {invoice.uid}")
        return invoice

@debug.log
def edit_invoice(app_data, invoice):
    invoice_args = dlg.open_invoice_dialog(app_data=app_data, loaded_invoice=invoice)
    if invoice_args:
        if invoice_args == "delete":
            app_data.project.delete_invoice(invoice)
            """ logging """
            debug.log(f"Invoice deleted: {invoice.id}, {invoice.uid}")
        else:
            # need the api function, because we need to update all ivoices afterwards
            app_data.project.update_invoice(invoice, invoice_args)
            """ logging """
            debug.log(f"Existing invoice edited: {invoice.id}, {invoice.uid}")
        return invoice

@debug.log
def invoice_check(app_data, invoice, save_path=None):
    app_data.output_check_invoice(invoice)
    app_data.open_invoice_check_dir()
    debug.log(f"Invoice check file written for the invoice {invoice}")

""" i,a&e
#
#   JOB
#
"""
@debug.log
def input_job(app_data):
    # open dialog and add job to project
    input_job_args = dlg.open_job_dialog(app_data=app_data)
    if input_job_args:
        job = app_data.project.input_new_job(input_job_args)
        """ logging """
        company_name = job.company.name if job.company else "-"
        debug.log(f"New job added: {company_name}, {job.id}, {job.uid}")
        return job

@debug.log
def edit_job(app_data, job):
    job_args = dlg.open_job_dialog(app_data=app_data, loaded_job=job)
    if job_args:
        company_name = job.company.name if job.company else "-"
        if job_args == "delete":
            app_data.project.delete_job(job)
            """ logging """
            debug.log(f"Job deleted: {company_name}, {job.id}, {job.uid}")
        else:
            job.update(**job_args)
            """ logging """
            debug.log(f"Existing job edited: {company_name}, {job.id}, {job.uid}")
        return job

""" i,a&e
#
#   COMPANY
#
"""
@debug.log
def input_company(app_data):
    # open dialog and add job to project
    input_company_args = dlg.open_company_dialog(app_data=app_data)
    if input_company_args:
        company = app_data.project.input_new_company(input_company_args)
        """ logging """
        company_name = company.name if company.name else "-"
        debug.log(f"New company added: {company_name}")
        return company

@debug.log
def edit_company(app_data, company):
    company_args = dlg.open_company_dialog(app_data=app_data, loaded_company=company)
    if company_args:
        company_name = company.name if company.name else "-"
        if company_args == "delete":
            app_data.project.delete_company(company)
            """ logging """
            debug.log(f"Company deleted: {company_name}")
        else:
            company.update(**company_args)
            """ logging """
            debug.log(f"Existing company edited: {company_name}")
        return company

""" i,a&e
#
#   TRADE
#
"""
@debug.log
def input_trade(app_data):
    # open dialog and add job to project
    input_trade_args = dlg.open_trade_dialog(app_data=app_data)
    if input_trade_args:
        trade = app_data.project.input_new_trade(input_trade_args)
        """ logging """
        trade_name = trade.name if trade.name else "-"
        debug.log(f"New trade added: {trade_name}")
        return trade

@debug.log
def edit_trade(app_data, trade):
    trade_args = dlg.open_trade_dialog(app_data=app_data, loaded_trade=trade)
    if trade_args:
        trade_name = trade.name if trade.name else "-"
        trade_cost_group = trade.cost_group.id if trade.cost_group else "-"
        trade_budget = trade.budget if trade.budget else "-"
        if trade_args == "delete":
            app_data.project.delete_trade(trade)
            """ logging """
            debug.log(f"Trade deleted: {trade_name}, cost_group {trade_cost_group}, budget {trade_budget} {app_data.get_currency()}")
        else:
            trade.update(**trade_args)
            """ logging """
            debug.log(f"Existing trade edited: {trade_name}, cost_group {trade_cost_group}, budget {trade_budget} {app_data.get_currency()}")
        return trade

""" i,a&e
#
#   COST GROUP
#
"""
@debug.log
def input_cost_group(app_data):
    # open dialog and add job to project
    input_cost_group_args = dlg.open_cost_group_dialog(app_data=app_data)
    if input_cost_group_args:
        cost_group = app_data.project.input_new_cost_group(input_cost_group_args)
        """ logging """
        debug.log(f"New cost_group added: {cost_group.id}")
        return cost_group

@debug.log
def edit_cost_group(app_data, cost_group):
    cost_group_args = dlg.open_cost_group_dialog(app_data=app_data, loaded_cost_group=cost_group)
    if cost_group_args:
        cost_group_budget = cost_group.budget if cost_group.budget else "-"
        if cost_group_args == "delete":
            app_data.project.delete_cost_group(cost_group)
            """ logging """
            debug.log(f"Cost_group deleted: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}")
        else:
            cost_group.update(**cost_group_args)
            """ logging """
            debug.log(f"Existing cost_group edited: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}")
        return cost_group

""" i,a&e
#
#   CONFIG
#
"""
@debug.log
def edit_app_config(app_data):
    loaded_config = app_data.config
    default_config = app_data.get_default_config()
    loaded_config_args = dlg.open_config_dialog(loaded_config=loaded_config, default_config=default_config)
    if loaded_config_args:
        app_data.config = loaded_config_args["config"]
        app_data.save_app_config()
        """ logging """
        debug.log(f"app_data.config has been changed: {loaded_config_args}")
        return loaded_config_args["config"]

@debug.log
def edit_proj_config(app_data):
    loaded_config = app_data.project.config
    loaded_config_args = dlg.open_config_dialog(loaded_config=loaded_config)
    if loaded_config_args:
        app_data.project.config = loaded_config_args["config"]
        """ logging """
        debug.log(f"project.config has been changed: {loaded_config_args}")
        return loaded_config_args["config"]


"""
#
#   RENDER TO WIDGET
#
#
"""
def render_to_table(content, table, cols, titles, date_cols=[], amount_cols=[], currency="€"):
    sel_item = table.currentItem().data(1) if table.currentItem() else None # to restore the selection
    table.clear()

    table.setSortingEnabled(False) # disable sorting when filling the table (to abvoid bugs with da data field)
    table.setRowCount(len(content))
    # set columns of table to the list self.invoice_cols
    table.setColumnCount(len(cols)+1)
    # set column titles
    header_labels = ["UID"]+[titles[col["title"]] for col in cols]
    table.setHorizontalHeaderLabels(header_labels)
    # hide the UID column
    table.setColumnHidden(0, True)

    for i in range(len(cols)):
        table.setColumnWidth(i+1, cols[i]["width"])

    row = 0
    for content_item in content:
        add_item_to_table(content_item=content_item, table=table, cols=cols, row=row, date_cols=date_cols, amount_cols=amount_cols, currency=currency)
        row += 1
    table.setSortingEnabled(True) # enable sorting once the table is filled
    # set selection again
    if sel_item:
        select_table_item(table, sel_item)

def add_item_to_table(content_item, table, cols, row, date_cols=[], amount_cols=[], currency="€"):
    # UID
    table_item_uid = QtWidgets.QTableWidgetItem(str(getattr(content_item, "_uid")))
    table_item_uid.setData(1, content_item)
    table.setItem(row, 0, table_item_uid)

    col = 1
    for attr in cols:
        # cols is a list of dicts with "title" and "width" of a column, we need only the title/attribute
        attr = attr["title"]
        # PyQt5.QtCore.QDate into readable String
        if attr in date_cols:
            date = getattr(content_item, attr)
            cell_content = qdate_to_str(date) if date else "-"
            sorting_key = date.toJulianDay() if date else float("inf")
            table_item = customqt.DateTableWidgetItem(cell_content, sorting_key=sorting_key)
        elif attr in amount_cols:
            table_item = QtWidgets.QTableWidgetItem(amount_w_currency_str(getattr(content_item, attr), currency))
        else:
            table_item = QtWidgets.QTableWidgetItem(str(getattr(content_item, attr)))
        table_item.setData(1, content_item)
        table_item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) # make selectable but not editable
        table.setItem(row, col, table_item)
        col += 1
    return table_item

def add_item_to_list(content_item, item_date, item_id, list_widget, tooltip=None):
    item = QtWidgets.QListWidgetItem(f"{item_date} \t {item_id}")
    if tooltip:
        item.setToolTip(tooltip)
    item.setData(1, content_item)
    list_widget.addItem(item)
    return item


def add_item_to_tree(content_item, parent, cols, tooltip=None):
    item_node = QtWidgets.QTreeWidgetItem(parent, cols)
    item_node.setData(1, QtCore.Qt.UserRole, content_item)
    if tooltip:
        item_node.setToolTip(1, tooltip)
    return item_node

def select_table_item(table, content_item):
    # deselect first
    for selected_range in table.selectedRanges():
        table.setRangeSelected(selected_range, False)

    uid_item = table.findItems(str(content_item.uid), QtCore.Qt.MatchExactly)[0] if len(table.findItems(str(content_item.uid), QtCore.Qt.MatchExactly))>0 else None
    if uid_item:
        row = uid_item.row()
        # select content_item row
        item_range = QtWidgets.QTableWidgetSelectionRange(row, 0, row, table.columnCount()-1)
        table.setRangeSelected(item_range, True)
        table.setCurrentItem(uid_item)

"""
#
#   DELETE
#   Ask first via prompt, if yes close dialog and return signal -1.
#
"""
def delete(dialog, object):
    # TODO: object not needed. maybe remove or delete here...
    reply = dlg.open_delete_prompt(dialog)
    if reply == QtWidgets.QMessageBox.Yes:
        dialog.done(-1)

"""
#
#   INPUT MANAGEMENT
#   Functions for QDialog input-output management
#
"""

"""
#   input amounts
"""
def input_to_float(input_1):
    if input_1.text().replace(",", "").replace(".", "").isnumeric():
        return str_to_float(input_1.text())
    else:
        return float(0)

def two_inputs_to_float(input_1, input_2):
    input_1 = input_1.text() if input_1.text().isnumeric() else "0"
    input_2 = input_2.text() if input_2.text().isnumeric() else "0"
    amount = ".".join([input_1, input_2])
    return str_to_float(amount)

def str_to_float(string):
    return rnd(float(string.replace(",",".")))

"""
#   output amounts
"""
def amount_str(float):
    if float!=0:
        return "{:,.2f}".format(rnd(float)).replace(".","X").replace(",",".").replace("X",",")
    else:
        return "-"

def amount_w_currency_str(float, currency):
    return " ".join([amount_str(float),currency])

"""
#   output percent string
"""
def percent_str(float):
    if float!=0:
        return "{:.1f}".format(rnd(float)).replace(".",",")
    else:
        return "-"

def percent_str_w_sign(float):
    return " ".join([percent_str(float),"%"])

"""
#   handle numbers
"""
def rnd(amount):
    return round(amount, 2)

"""
#   QDate to String
"""
def qdate_to_str(qdate):
    format = '%d.%m.%Y'
    return qdate.toPyDate().strftime(format)
