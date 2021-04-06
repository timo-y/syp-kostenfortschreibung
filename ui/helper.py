"""
#
#   HELPER
#   Module with helper functions that connect the api to the ui.
#
#
"""
import debug

import os
from pathlib import Path
import datetime
import json
import shutil

from ui import dlg
from ui import customqt

from PyQt5 import QtWidgets, QtCore

import pdfexportr
from core.obj import proj

"""
#
#   INPUT, ADD and EDIT
#   Input, add and edit objects.
#
"""

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
    f_dialog = QtWidgets.QFileDialog(directory=str(save_dir_path))
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Projekt öffnen...",  "", "Project saves (*.project);;All Files (*)")
    if file_path:
        app_data.load_project(file_path)
        """ logging """
        debug.log(f"Project loaded: \"{app_data.project.identifier}\"")

def save_project(mainwindow, app_data):
    if app_data.project:
        if app_data.project.has_been_saved():
            save_path = app_data.get_loaded_save_path()
            if save_path and os.path.isfile(save_path):
                app_data.save_project(save_path)
                """ logging """
                debug.log(f"Project saved: \"{app_data.project.identifier}\"")
            else:
                save_project_as(mainwindow, app_data)
        else:
            save_project_as(mainwindow, app_data)

def save_project_as(mainwindow, app_data):
    if app_data.project:
        save_dir_path = os.path.join(app_data.get_save_dir(), app_data.project.identifier+".project")
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Speichern...", save_dir_path, "Project save (*.project)")
        if save_path:
            app_data.save_project(os.path.normpath(save_path))
            """ logging """
            debug.log(f"Project saved: \"{app_data.project.identifier}\" as {save_path}")

""" i,a&e
#
#   EXPORT
#
"""
def export_companies(mainwindow, app_data):
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-companies.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Firmenverzeichniss exportieren...", str(save_dir_path), "Company-JSON (*.json)")
        if save_path:
            app_data.export_companies(save_path)
            """ logging """
            debug.log(f"Companies exported to {save_path}")

def export_trades(mainwindow, app_data):
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-trades.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Gewerkeverzeichniss exportieren...", str(save_dir_path), "Trade-JSON (*.json)")
        if save_path:
            app_data.export_trades(save_path)
            """ logging """
            debug.log(f"Trades exported to {save_path}")

def export_cost_groups(mainwindow, app_data):
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-cost_groups.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(mainwindow,"Kostengruppen exportieren...", str(save_dir_path), "Kostengruppen-JSON (*.json)")
        if save_path:
            app_data.export_cost_groups(save_path)
            """ logging """
            debug.log(f"CostGroups exported to {save_path}")

""" i,a&e
#
#   IMPORT
#
"""
def import_project(mainwindow, app_data):
    filename = "*-Kostenfortschreibung_import.xlsm"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Projekt importieren...",  str(save_dir_path), "Kostenfortschreibung-Excelmappe (*.xlsm);;All Files (*)")
    if file_path:
        app_data.import_project(file_path)
        """ logging """
        debug.log(f"Project successfully imported")

def import_companies(mainwindow, app_data):
    filename = "companies.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Firmenverzeichniss importieren...",  str(save_dir_path), "Company-JSONs (*.json);;All Files (*)")
    if file_path:
        app_data.import_companies(file_path)
        """ logging """
        debug.log(f"Companies successfully imported")

def import_trades(mainwindow, app_data):
    filename = "trades.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Gewerkeverzeichniss importieren...",  str(save_dir_path), "Trade-JSONs (*.json);;All Files (*)")
    if file_path:
        app_data.import_trades(file_path)
        """ logging """
        debug.log(f"Trades successfully imported")

def import_cost_groups(mainwindow, app_data):
    filename = "cost_groups.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(mainwindow,"Kostengruppen importieren...",  str(save_dir_path), "Kostengruppen-JSONs (*.json);;All Files (*)")
    if file_path:
        app_data.import_cost_groups(file_path)
        """ logging """
        debug.log(f"CostGroups successfully imported")

""" i,a&e
#
#   PROJECT COST CALCULATION
#
"""
def input_pcc(app_data):
    input_pcc_args = dlg.open_project_cost_calculation_dialog(app_data=app_data)
    if input_pcc_args:
        pcc = app_data.project.input_new_pcc(input_pcc_args)
        """ logging """
        debug.log(f"ProjectCostCalculation added: {pcc.name}")
        return pcc

def edit_pcc(app_data, pcc):
    pcc_args = dlg.open_project_cost_calculation_dialog(app_data=app_data, loaded_pcc=pcc)
    if pcc_args:
        if pcc_args == "delete":
            app_data.project.delete_pcc(pcc)
            """ logging """
            debug.log(f"ProjectCostCalculation deleted: {pcc.name}, from the {pcc.date.toPyDate()}")
        else:
            pcc.update(**pcc_args)
            """ logging """
            debug.log(f"Existing ProjectCostCalculation edited: {pcc.name}, from the {pcc.date.toPyDate()}")
        return pcc

""" i,a&e
#
#   INVENTORY ITEM
#
"""
def input_inventory_item(app_data):
    input_inventory_item_args = dlg.open_inventory_item_dialog(app_data)
    if input_inventory_item_args:
        input_inventory_item = proj.InventoryItem(**input_inventory_item_args)
        return input_inventory_item

def edit_inventory_item(app_data, inventory_item):
    inventory_item_args = dlg.open_inventory_item_dialog(app_data=app_data, loaded_inventory_item=inventory_item)
    if inventory_item_args:
        if inventory_item_args == "delete":
            inventory_item.delete()
            """ logging """
            debug.log(f"InventoryItem deleted: {inventory_item.name}")
        else:
            inventory_item.update(**inventory_item_args)
            """ logging """
            debug.log(f"Existing InventoryItem edited: {inventory_item.name}")
        return inventory_item

""" i,a&e
#
#   PERSON
#
"""
def input_person(app_data):
    input_person_args = dlg.open_person_dialog()
    if input_person_args:
        person = app_data.project.input_new_person(input_person_args)
        """ logging """
        debug.log(f"New person returned: {person.first_name}, {person.last_name}")
        return person

def edit_person(app_data, person):
    person_args = dlg.open_person_dialog(loaded_person=person)
    if person_args:
        if person_args == "delete":
            app_data.project.delete_person(person)
            """ logging """
            debug.log(f"Person deleted: {person.first_name}, {person.last_name}")
        else:
            person.update(**person_args, company=person.company)
            """ logging """
            debug.log(f"Existing Person edited: {person.first_name}, {person.last_name}")
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
        debug.log(f"New Invoice added: {invoice.id}, {invoice.uid}")
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
            debug.log(f"Existing Invoice edited: {invoice.id}, {invoice.uid}")
        return invoice

""" i,a&e
#
#   JOB
#
"""
@debug.log
def input_job(app_data, sel_company=None):
    # open dialog and add job to project
    input_job_args = dlg.open_job_dialog(app_data=app_data, sel_company=sel_company)
    if input_job_args:
        job = app_data.project.input_new_job(input_job_args)
        """ logging """
        company_name = job.company.name if job.company else "-"
        debug.log(f"New Job added: {company_name}, {job.id}, {job.uid}")
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
            debug.log(f"Existing Job edited: {company_name}, {job.id}, {job.uid}")
        return job

@debug.log
def pay_safety_deposit(job):
        paid_safety_deposit_args = dlg.open_pay_safety_deposit_dialog()
        if paid_safety_deposit_args:
            job.pay_safety_deposit(**paid_safety_deposit_args)

@debug.log
def add_job_addition(job):
        job_addition_args = dlg.open_add_job_addition_dialog()
        if job_addition_args:
            job.add_job_addition(**job_addition_args)
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
        debug.log(f"New Company added: {company_name}")
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
            debug.log(f"Existing Company edited: {company_name}")
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
        debug.log(f"New Trade added: {trade_name}")
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
            debug.log(f"Existing Trade edited: {trade_name}, cost_group {trade_cost_group}, budget {trade_budget} {app_data.get_currency()}")
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
        debug.log(f"New CostGroup added: {cost_group.id}")
        return cost_group

@debug.log
def edit_cost_group(app_data, cost_group):
    cost_group_args = dlg.open_cost_group_dialog(app_data=app_data, loaded_cost_group=cost_group)
    if cost_group_args:
        cost_group_budget = cost_group.budget if cost_group.budget else "-"
        if cost_group_args == "delete":
            app_data.project.delete_cost_group(cost_group)
            """ logging """
            debug.log(f"CostGroup deleted: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}")
        else:
            cost_group.update(**cost_group_args)
            """ logging """
            debug.log(f"Existing CostGroup edited: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}")
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
#   OUTPUT
#       Output files
#
"""
"""
#   INVOICE CHECK
"""
@debug.log
def invoice_check(app_data, invoice, curr_job_only):
    folder_name = app_data.get_invoice_check_folder_name(invoice)
    create_at_path = os.path.join(app_data.get_app_invoice_check_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_invoice_check(invoice=invoice,
                                create_at_path=create_at_path),
        app_data.output_ov_of_company(company=invoice.company,
                              create_at_path=create_at_path,
                              selected_job=invoice.job if curr_job_only else None
                              )
    ]
    """
    #
    #   Convert to PDF
    #
    """
    pdf_files = [xlsx2pdf(*file) for file in xlsx_files]
    """
    #
    #   Copy to Folders
    #
    """
    #   Invoice check path
    inv_check_path = os.path.join(app_data.get_invoice_check_dir(), folder_name)

    # create directory if non-existing
    if not os.path.exists(inv_check_path):
        os.makedirs(inv_check_path)
    for file in pdf_files:
        shutil.copy(file[0], os.path.join(inv_check_path, file[1]))

    #   Correspondence path
    correspondence_path = os.path.join(app_data.get_client_correspondence_dir(), folder_name)

    # create directory if non-existing
    if not os.path.exists(correspondence_path):
        os.makedirs(correspondence_path)
    for file in pdf_files:
        shutil.copy(file[0], os.path.join(correspondence_path, file[1]))
    """
    #    log
    """
    debug.log(f"Invoice check file written for the Invoice {invoice}")

"""
#   TRADES OVERVIEW
"""
@debug.log
def trades_ov(app_data):
    folder_name = app_data.get_trades_overview_folder_name()
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_ov_by_trades(create_at_path=create_at_path)
    ]
    """
    #
    #   Convert to PDF
    #
    """
    pdf_files = [xlsx2pdf(*file) for file in xlsx_files]
    """
    #    log
    """
    debug.log(f"Trades OV file written")

"""
#   COST GROUPS OVERVIEW
"""
@debug.log
def cost_groups_ov(app_data):
    folder_name = app_data.get_cost_groups_overview_folder_name()
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_ov_by_cost_groups(create_at_path=create_at_path)
    ]
    """
    #
    #   Convert to PDF
    #
    """
    pdf_files = [xlsx2pdf(*file) for file in xlsx_files]
    """
    #    log
    """
    debug.log(f"Trades OV file written")

"""
#   COMPANY OVERVIEW
"""
@debug.log
def company_ov(app_data, company, selected_job=None):
    folder_name = app_data.get_company_overview_folder_name(company)
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_ov_of_company(company=company,
                              create_at_path=create_at_path,
                              selected_job=selected_job
                              )
    ]
    """
    #
    #   Convert to PDF
    #
    """
    pdf_files = [xlsx2pdf(*file) for file in xlsx_files]
    """
    #    log
    """
    debug.log(f"Company OV file written for the company {company.name}")

"""
#   PCC OVERVIEW
"""
@debug.log
def pcc_overviews(app_data, pcc):
    folder_name = app_data.get_pcc_overview_folder_name(pcc)
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    date = today_str()
    filename_1 = f"{date}-costcalculation_overview-main-{app_data.project.identifier}"
    filename_2 = f"{date}-costcalculation_overview-all-{app_data.project.identifier}"
    xlsx_files = [
        app_data.output_pcc_ov_cost_groups(pcc=pcc,
                                        cost_groups=app_data.project.main_cost_groups,
                                        create_at_path=create_at_path,
                                        filename=filename_1),
        app_data.output_pcc_ov_cost_groups(pcc=pcc,
                                        cost_groups=app_data.project.cost_groups,
                                        create_at_path=create_at_path,
                                        filename=filename_2),
        app_data.output_pcc_ov_trades(pcc=pcc,
                                        create_at_path=create_at_path)
    ]
    """
    #
    #   Convert to PDF
    #
    """
    pdf_files = [xlsx2pdf(*file) for file in xlsx_files]

    """
    #    log
    """
    debug.log(f"ProjectCostCalculation overview written for the pcc {pcc.name}")

"""
#
#   RENDER TO WIDGET
#
#
"""
def render_to_table(content, table, cols, titles, date_cols=[], amount_cols=[], currency="€", set_width=False):
    sel_item = table.currentItem().data(1) if table.currentItem() else None # to restore the selection
    table.clear()

    table.setSortingEnabled(False) # disable sorting when filling the table (to abvoid bugs with da data field)
    table.setRowCount(len(content))
    # set columns of table to the list app_data.invoice_cols
    table.setColumnCount(len(cols)+1)
    # set column titles
    header_labels = ["UID"]+[titles[col["title"]] for col in cols]
    table.setHorizontalHeaderLabels(header_labels)
    # set title height
    table.horizontalHeader().setFixedHeight(50)
    # let the columns be moved
    table.horizontalHeader().setSectionsMovable(True)

    # hide the UID column
    table.setColumnHidden(0, True)
    if set_width:
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
            table_item = customqt.AmountTableWidgetItem(amount_str(getattr(content_item, attr), currency), sorting_key=getattr(content_item, attr))
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
    item_node = customqt.TreeWidgetItem(parent, cols) #QtWidgets.QTreeWidgetItem(parent, cols)
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
#   FORMAT WIDGETS
#
#
"""
def resize_tree_columns(treewidget):
    for i in range(1,treewidget.columnCount()):
        treewidget.resizeColumnToContents(i)

"""
#
#   PROMPTS
#
#
"""
"""
#   WANT TO SAVE?
#   Open a prompt asking if you want to save.
"""
def save_curr_project_prompt(dialog, app_data):
    """  Open a dialog asking user if they want to save and,
    if confirmed, save tne project.
    """
    reply = dlg.open_save_curr_project_prompt(dialog)
    if reply == QtWidgets.QMessageBox.Save:
        save_project(dialog, app_data)
    elif reply == QtWidgets.QMessageBox.Cancel:
        return False
    return True

"""
#   ARE YOU SURE?
#   Open a prompt asking if sure to do action.
"""
def u_sure_prompt(dialog):
    """  Open a dialog asking user if they are sure to proceed. """
    reply = dlg.open_u_sure_prompt(dialog)
    if reply == QtWidgets.QMessageBox.Yes:
        return True
    return False

"""
#   DELETE
#       This function is called within the a dialo from ui.dlg.
#       Ask first via prompt, if yes close dialog and return signal -1.
"""
def delete(dialog, object):
    """ Open a dialog to confirm the deletion.

    Since we can only delete objects from their respective edit dialog, this prompt,
    if confirmed, closes the parent dialog with the value -1.
    """
    # TODO: object not needed. maybe remove or delete here...
    reply = dlg.open_delete_prompt(dialog)
    if reply == QtWidgets.QMessageBox.Yes:
        # close dialog with the value -1
        dialog.done(-1)
        return True
    else:
        return False

"""
#
#   CONVERSION
#       Convert data, files etc.
#
"""
def from_json_file(file_path, *, decoder=json.JSONDecoder):
    """ Import a *.json file.

    Arguments:
    file_path -- path to the file
    decoder -- the decoder (default: json.JSONDecoder)
    """
    output = None
    with open(file_path, "r") as file:
        output = json.load(file, object_hook=decoder().object_hook)
    return output

def to_json_file(data, save_path, *, encoder=json.JSONEncoder):
    """ Export data to a *.json file.

    Arguments:
    save_path -- destination path of the file
    encoder -- the encoder (default: json.JSONEncoder)
    """
    with open(save_path, "w") as file:
        json.dump(data, file, cls=encoder, indent=4)

def xlsx2pdf(input_path, filename):
    """ Export PDF from xlsx-file.

    Arguments:
    input_path -- path of xlsx-file
    filename -- destination path of PDF
    """
    dir_path = os.path.dirname(input_path)
    pdf_filename = f"{filename}.pdf"
    pdf_save_path = os.path.join(dir_path, pdf_filename)
    pdfexportr.PDFExportr().create_pdf(input_path, pdf_save_path)
    return pdf_save_path, pdf_filename



"""
#
#   INPUT MANAGEMENT
#   Functions for QDialog input-output management
#
"""

def to_lex(cost_group_id):
    """ Convert an ID containing letters into a number to rder the table cell. """
    # add 1000 to make the id be listed after the last regular cost group
    id = 1000+int("".join([f"{ord(char)}" for char in cost_group_id]))
    return id

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
def amount_str(float, currency=""):
    if len(currency)>0:
        currency = f" {currency}"

    if rnd(float)!=0:
        amount = "{:,.2f}".format(rnd(float)).replace(".","X").replace(",",".").replace("X",",")
        return f"{amount}{currency}"
    else:
        return f"-{currency}"

"""
#   output percent string
"""
def percent_str(float):
    if rnd(float)!=0:
        return "{:.1f}".format(rnd(float)).replace(".",",")
    else:
        return "-"

def percent_str_w_sign(float):
    return " ".join([percent_str(float),"%"])

"""
#   handle numbers
"""
def rnd(amount):
    return float(round(amount, 2))

"""
#   QDate to String
"""
def qdate_to_str(qdate, format="%d.%m.%Y"):
    return qdate.toPyDate().strftime(format)


"""
#   datetime.now() string
"""
def now_str(format="%Y-%m-%d_%H%M%S"):
    return datetime.datetime.now().strftime(format)

def today_str(format="%Y-%m-%d"):
    return datetime.datetime.today().strftime(format)
