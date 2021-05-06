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
    """Open a dialog and create project with default companies and trades.

    Args:
        app_data (api.AppData): Application data containing the project data
    """
    input_project_args = dlg.open_project_dialog(app_data=app_data)
    if input_project_args:
        app_data.new_project(input_project_args)
        """ logging """
        debug.log(
            f"New project created: {app_data.project.identifier}, {str(app_data.project.uid)}"
        )


def edit_project(app_data):
    """Open a dialog to edit a project.

    Args:
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        input_project_args = dlg.open_project_dialog(
            app_data=app_data, loaded_project=app_data.project
        )
        if input_project_args:
            app_data.project.update(**input_project_args)
            """ logging """
            debug.log(
                f"Project edited: {app_data.project.identifier}, {str(app_data.project.uid)}"
            )


def load_project(mainwindow, app_data):
    """Open a dialog to find a *.project file and load it as a project.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    save_dir_path = app_data.get_save_dir()
    f_dialog = QtWidgets.QFileDialog(directory=str(save_dir_path))
    file_path, _ = f_dialog.getOpenFileName(
        mainwindow, "Projekt öffnen...", "", "Project saves (*.project);;All Files (*)"
    )
    if file_path:
        app_data.load_project(file_path)
        """ logging """
        debug.log(f'Project loaded: "{app_data.project.identifier}"')


def save_project(mainwindow, app_data):
    """Save a project. If it hasn't been saved, do save_project_as.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        if app_data.project.has_been_saved():
            save_path = app_data.get_loaded_save_path()
            if save_path and os.path.isfile(save_path):
                app_data.save_project(save_path)
                """ logging """
                debug.log(f'Project saved: "{app_data.project.identifier}"')
            else:
                save_project_as(mainwindow, app_data)
        else:
            save_project_as(mainwindow, app_data)


def save_project_as(mainwindow, app_data):
    """Open a dialog to save a project to a *.project file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        save_dir_path = os.path.join(
            app_data.get_save_dir(), app_data.project.identifier + ".project"
        )
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(
            mainwindow, "Speichern...", save_dir_path, "Project save (*.project)"
        )
        if save_path:
            app_data.save_project(os.path.normpath(save_path))
            """ logging """
            debug.log(f'Project saved: "{app_data.project.identifier}" as {save_path}')


""" i,a&e
#
#   EXPORT
#
"""


def export_companies(mainwindow, app_data):
    """Open a dialog to export the list of companies to a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-companies.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(
            mainwindow,
            "Firmenverzeichniss exportieren...",
            str(save_dir_path),
            "Company-JSON (*.json)",
        )
        if save_path:
            app_data.export_companies(save_path)
            """ logging """
            debug.log(f"Companies exported to {save_path}")


def export_trades(mainwindow, app_data):
    """Open a dialog to export the list of trades to a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-trades.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(
            mainwindow,
            "Gewerkeverzeichniss exportieren...",
            str(save_dir_path),
            "Trade-JSON (*.json)",
        )
        if save_path:
            app_data.export_trades(save_path)
            """ logging """
            debug.log(f"Trades exported to {save_path}")


def export_cost_groups(mainwindow, app_data):
    """Open a dialog to export the list of cost groups to a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    if app_data.project:
        filename = f"{today_str()}-{app_data.project.identifier}-cost_groups.json"
        save_dir_path = app_data.get_save_dir() / filename
        f_dialog = QtWidgets.QFileDialog()
        save_path, _ = f_dialog.getSaveFileName(
            mainwindow,
            "Kostengruppen exportieren...",
            str(save_dir_path),
            "Kostengruppen-JSON (*.json)",
        )
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
    """Open a dialog to import a project from a *-Kostenfortschreibung_import.xlsm file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    filename = "*-Kostenfortschreibung_import.xlsm"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(
        mainwindow,
        "Projekt importieren...",
        str(save_dir_path),
        "Kostenfortschreibung-Excelmappe (*.xlsm);;All Files (*)",
    )
    if file_path:
        app_data.import_project(file_path)
        """ logging """
        debug.log(f"Project successfully imported")


def import_companies(mainwindow, app_data):
    """Open a dialog to import the list of companies from a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    filename = "companies.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(
        mainwindow,
        "Firmenverzeichniss importieren...",
        str(save_dir_path),
        "Company-JSONs (*.json);;All Files (*)",
    )
    if file_path:
        app_data.import_companies(file_path)
        """ logging """
        debug.log(f"Companies successfully imported")


def import_trades(mainwindow, app_data):
    """Open a dialog to import the list of trades from a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    filename = "trades.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(
        mainwindow,
        "Gewerkeverzeichniss importieren...",
        str(save_dir_path),
        "Trade-JSONs (*.json);;All Files (*)",
    )
    if file_path:
        app_data.import_trades(file_path)
        """ logging """
        debug.log(f"Trades successfully imported")


def import_cost_groups(mainwindow, app_data):
    """Open a dialog to import the list of cost groups1 from a JSON file.

    Args:
        mainwindow (mainwindow.MainWindow): Main window of the application
        app_data (api.AppData): Application data containing the project data
    """
    filename = "cost_groups.json"
    save_dir_path = app_data.get_save_dir() / filename
    f_dialog = QtWidgets.QFileDialog()
    file_path, _ = f_dialog.getOpenFileName(
        mainwindow,
        "Kostengruppen importieren...",
        str(save_dir_path),
        "Kostengruppen-JSONs (*.json);;All Files (*)",
    )
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
    """Open a dialog to input a new project cost calculation.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        proj.ProjectCostCalculation: New project cost calculation
    """
    input_pcc_args = dlg.open_project_cost_calculation_dialog(app_data=app_data)
    if input_pcc_args:
        pcc = app_data.project.input_new_pcc(input_pcc_args)
        """ logging """
        debug.log(f"ProjectCostCalculation added: {pcc.name}")
        return pcc


def edit_pcc(app_data, pcc):
    """Open a dialog to edit a project cost calculation.

    Args:
        app_data (api.AppData): Application data containing the project data
        pcc (proj.ProjectCostCalculation): Project cost calculation to edit

    Returns:
        proj.ProjectCostCalculation: Edited project cost calculation
    """
    pcc_args = dlg.open_project_cost_calculation_dialog(
        app_data=app_data, loaded_pcc=pcc
    )
    if pcc_args:
        if pcc_args == "delete":
            app_data.project.delete_pcc(pcc)
            """ logging """
            debug.log(
                f"ProjectCostCalculation deleted: {pcc.name}, from the {pcc.date.toPyDate()}"
            )
        else:
            pcc.update(**pcc_args)
            """ logging """
            debug.log(
                f"Existing ProjectCostCalculation edited: {pcc.name}, from the {pcc.date.toPyDate()}"
            )
        return pcc


""" i,a&e
#
#   INVENTORY ITEM
#
"""


def input_inventory_item(app_data):
    """Open a dialog to input a new inventory item.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        proj.InventoryItem: New inventory item
    """
    input_inventory_item_args = dlg.open_inventory_item_dialog(app_data)
    if input_inventory_item_args:
        input_inventory_item = proj.InventoryItem(**input_inventory_item_args)
        return input_inventory_item


def edit_inventory_item(app_data, inventory_item):
    """Open a dialog to edit a inventory item.

    Args:
        app_data (api.AppData): Application data containing the project data
        inventory_item (proj.InventoryItem): Inventory item to edit

    Returns:
        proj.InventoryItem: Edited inventory item
    """
    inventory_item_args = dlg.open_inventory_item_dialog(
        app_data=app_data, loaded_inventory_item=inventory_item
    )
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
    """Open a dialog to input a new person.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        corp.Person: New person
    """
    input_person_args = dlg.open_person_dialog()
    if input_person_args:
        person = app_data.project.input_new_person(input_person_args)
        """ logging """
        debug.log(f"New person returned: {person.first_name}, {person.last_name}")
        return person


def edit_person(app_data, person):
    """Open a dialog to edit a person.

    Args:
        app_data (api.AppData): Application data containing the project data
        person (corp.Person): Person to edit

    Returns:
        corp.Person: Edited person
    """
    person_args = dlg.open_person_dialog(loaded_person=person)
    if person_args:
        if person_args == "delete":
            app_data.project.delete_person(person)
            """ logging """
            debug.log(f"Person deleted: {person.first_name}, {person.last_name}")
        else:
            person.update(**person_args, company=person.company)
            """ logging """
            debug.log(
                f"Existing Person edited: {person.first_name}, {person.last_name}"
            )
        return person


""" i,a&e
#
#   INVOICE
#
"""


@debug.log
def input_invoice(app_data, sel_job=None):
    """Open a dialog to input a new invoice.

    Args:
        app_data (api.AppData): Application data containing the project data
        sel_job (None, optional): The job the invoice belongs to

    Returns:
        corp.Invoice: New invoice
    """
    input_invoice_args = dlg.open_invoice_dialog(app_data=app_data, sel_job=sel_job)
    if input_invoice_args:
        invoice = app_data.project.input_new_invoice(input_invoice_args)
        """ logging """
        debug.log(f"New Invoice added: {invoice.id}, {invoice.uid}")
        return invoice


@debug.log
def edit_invoice(app_data, invoice):
    """Open a dialog to edit a invoice.

    Args:
        app_data (api.AppData): Application data containing the project data
        invoice (corp.Invoice): Invoice to edit

    Returns:
        corp.Invoice: Edited invoice
    """
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
    """Open a dialog to input a new job.

    Args:
        app_data (api.AppData): Application data containing the project data
        sel_company (None, optional): The company the job belongs to

    Returns:
        corp.Job: New job
    """
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
    """Open a dialog to edit a job.

    Args:
        app_data (api.AppData): Application data containing the project data
        job (corp.Job): Job to edit

    Returns:
        corp.Job: Edited job
    """
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
    """Open a dialog to input a new safety deposite for a job.

    Args:
        job (corp.Job): The selected job
    """
    paid_safety_deposit_args = dlg.open_pay_safety_deposit_dialog()
    if paid_safety_deposit_args:
        job.pay_safety_deposit(**paid_safety_deposit_args)


@debug.log
def add_job_addition(job):
    """Open a dialog to input a new job addition for a job.

    Args:
        job (corp.Job): The selected Job
    """
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
    """Open a dialog to input a new company.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        corp.Company: New compeny
    """
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
    """Open a dialog to edit a company.

    Args:
        app_data (api.AppData): Application data containing the project data
        company (corp.Company): Company to edit

    Returns:
        corp.Company: Edited company
    """
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
    """Open a dialog to input a new trade.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        arch.Trade: New trade
    """
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
    """Open a dialog to edit a trade.

    Args:
        app_data (api.AppData): Application data containing the project data
        trade (arch.Trade): Trade to edit

    Returns:
        arch.Trade: Edited trade
    """
    trade_args = dlg.open_trade_dialog(app_data=app_data, loaded_trade=trade)
    if trade_args:
        trade_name = trade.name if trade.name else "-"
        trade_cost_group = trade.cost_group.id if trade.cost_group else "-"
        trade_budget = trade.budget if trade.budget else "-"
        if trade_args == "delete":
            app_data.project.delete_trade(trade)
            """ logging """
            debug.log(
                f"Trade deleted: {trade_name}, cost_group {trade_cost_group}, budget {trade_budget} {app_data.get_currency()}"
            )
        else:
            trade.update(**trade_args)
            """ logging """
            debug.log(
                f"Existing Trade edited: {trade_name}, cost_group {trade_cost_group}, budget {trade_budget} {app_data.get_currency()}"
            )
        return trade


""" i,a&e
#
#   COST GROUP
#
"""


@debug.log
def input_cost_group(app_data):
    """Open a dialog to input a new cost group.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        arch.CostGroup: New cost group
    """
    # open dialog and add job to project
    input_cost_group_args = dlg.open_cost_group_dialog(app_data=app_data)
    if input_cost_group_args:
        cost_group = app_data.project.input_new_cost_group(input_cost_group_args)
        """ logging """
        debug.log(f"New CostGroup added: {cost_group.id}")
        return cost_group


@debug.log
def edit_cost_group(app_data, cost_group):
    """Open a dialog to edit a cost group.

    Args:
        app_data (api.AppData): Application data containing the project data
        cost_group (arch.CostGroup): Cost group to edit

    Returns:
        arch.CostGroup: Edited cost group
    """
    cost_group_args = dlg.open_cost_group_dialog(
        app_data=app_data, loaded_cost_group=cost_group
    )
    if cost_group_args:
        cost_group_budget = cost_group.budget if cost_group.budget else "-"
        if cost_group_args == "delete":
            app_data.project.delete_cost_group(cost_group)
            """ logging """
            debug.log(
                f"CostGroup deleted: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}"
            )
        else:
            cost_group.update(**cost_group_args)
            """ logging """
            debug.log(
                f"Existing CostGroup edited: {cost_group.id}, {cost_group.name}, description {cost_group.description}, budget {cost_group_budget} {app_data.get_currency()}"
            )
        return cost_group


""" i,a&e
#
#   CONFIG
#
"""


@debug.log
def edit_app_config(app_data):
    """Open a dialog to edit the app config.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        dict: App config
    """
    loaded_config = app_data.config
    default_config = app_data.get_default_config()
    loaded_config_args = dlg.open_config_dialog(
        loaded_config=loaded_config, default_config=default_config
    )
    if loaded_config_args:
        app_data.config = loaded_config_args["config"]
        app_data.save_app_config()
        """ logging """
        debug.log(f"app_data.config has been changed: {loaded_config_args}")
        return loaded_config_args["config"]


@debug.log
def edit_proj_config(app_data):
    """Open a dialog to edit the project config.

    Args:
        app_data (api.AppData): Application data containing the project data

    Returns:
        dict: Project config
    """
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
    """Create invoice_check.pdf and company_ov.pdf (of the job if selected) at the
    invoice check and correspondence paths.

    Also creates these files and the original *.xlsx in the overviews subdir of the program dir.

    Args:
        app_data (api.AppData): Application data containing the project data
        invoice (corp.Invoice): The invoice
        curr_job_only (bool): If True, only the job of the invoice is shown in the overview
    """
    folder_name = app_data.get_invoice_check_folder_name(invoice)
    create_at_path = os.path.join(app_data.get_app_invoice_check_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_invoice_check(invoice=invoice, create_at_path=create_at_path),
        app_data.output_ov_of_company(
            company=invoice.company,
            create_at_path=create_at_path,
            selected_job=invoice.job if curr_job_only else None,
        ),
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
    correspondence_path = os.path.join(
        app_data.get_client_correspondence_dir(), folder_name
    )

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
    """Create an overview of the trades as a PDF and Xlsx files in the
    overviews subdir of the program.

    Args:
        app_data (api.AppData): Application data containing the project data
    """
    folder_name = app_data.get_trades_overview_folder_name()
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [app_data.output_ov_by_trades(create_at_path=create_at_path)]
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
    """Create an overview of the cost groups as a PDF and Xlsx files in the
    overviews subdir of the program.

    Args:
        app_data (api.AppData): Application data containing the project data
    """
    folder_name = app_data.get_cost_groups_overview_folder_name()
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [app_data.output_ov_by_cost_groups(create_at_path=create_at_path)]
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
    """Create an overview of the jobs of a company as a PDF and Xlsx files in the
    overviews subdir of the program.

    Args:
        app_data (api.AppData): Application data containing the project data
        company (corp.Company): The company
        selected_job (None, optional): The selected job
    """
    folder_name = app_data.get_company_overview_folder_name(company)
    create_at_path = os.path.join(app_data.get_app_overviews_dir(), folder_name)
    """
    #
    #   Create xlsx files
    #
    """
    xlsx_files = [
        app_data.output_ov_of_company(
            company=company, create_at_path=create_at_path, selected_job=selected_job
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
    """Create overviews of a project cost calculation as a PDF and Xlsx files in the
    overviews subdir of the program.

    Args:
        app_data (api.AppData): Application data containing the project data
        pcc (proj.ProjectCostCalculation): The project cost calculation
    """
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
        app_data.output_pcc_ov_cost_groups(
            pcc=pcc,
            cost_groups=app_data.project.main_cost_groups,
            create_at_path=create_at_path,
            filename=filename_1,
        ),
        app_data.output_pcc_ov_cost_groups(
            pcc=pcc,
            cost_groups=app_data.project.cost_groups,
            create_at_path=create_at_path,
            filename=filename_2,
        ),
        app_data.output_pcc_ov_trades(pcc=pcc, create_at_path=create_at_path),
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


def render_to_table(
    content,
    table,
    cols,
    titles,
    date_cols=[],
    amount_cols=[],
    currency="€",
    set_width=False,
):
    """Render some content to a QTable.

    Args:
        content (TYPE): Content to be rendered
        table (TYPE): Table to render to
        cols (TYPE): Columns/attributes of the content
        titles (TYPE): Titles of the columns
        date_cols (list, optional): Columns to be formatted as dates
        amount_cols (list, optional): Columns to be formatted as amounts
        currency (str, optional): Currency abbreviation
        set_width (bool, optional): If True, the col width will be set
    """
    sel_item = (
        table.currentItem().data(1) if table.currentItem() else None
    )  # to restore the selection
    table.clear()

    table.setSortingEnabled(
        False
    )  # disable sorting when filling the table (to abvoid bugs with da data field)
    table.setRowCount(len(content))
    # set columns of table to the list app_data.invoice_cols
    table.setColumnCount(len(cols) + 1)
    # set column titles
    header_labels = ["UID"] + [titles[col["title"]] for col in cols]
    table.setHorizontalHeaderLabels(header_labels)
    # set title height
    table.horizontalHeader().setFixedHeight(50)
    # let the columns be moved
    table.horizontalHeader().setSectionsMovable(True)

    # hide the UID column
    table.setColumnHidden(0, True)
    if set_width:
        for i in range(len(cols)):
            table.setColumnWidth(i + 1, cols[i]["width"])

    row = 0
    for content_item in content:
        add_item_to_table(
            content_item=content_item,
            table=table,
            cols=cols,
            row=row,
            date_cols=date_cols,
            amount_cols=amount_cols,
            currency=currency,
        )
        row += 1
    table.setSortingEnabled(True)  # enable sorting once the table is filled
    # set selection again
    if sel_item:
        select_table_item(table, sel_item)


def add_item_to_table(
    content_item, table, cols, row, date_cols=[], amount_cols=[], currency="€"
):
    """Render some item to a row of a QTable.

    Args:
        content_item (TYPE): Item to be rendered in the row
        table (TYPE): Table to render to
        cols (TYPE): Columns/attributes of the content
        row (int): Row index
        date_cols (list, optional): Columns to be formatted as dates
        amount_cols (list, optional): Columns to be formatted as amounts
        currency (str, optional): Currency abbreviation

    Returns:
        TYPE: Rendered table item
    """
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
            table_item = customqt.DateTableWidgetItem(
                cell_content, sorting_key=sorting_key
            )
        elif attr in amount_cols:
            table_item = customqt.AmountTableWidgetItem(
                amount_str(getattr(content_item, attr), currency),
                sorting_key=getattr(content_item, attr),
            )
        else:
            table_item = QtWidgets.QTableWidgetItem(str(getattr(content_item, attr)))
        table_item.setData(1, content_item)
        table_item.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        )  # make selectable but not editable
        table.setItem(row, col, table_item)
        col += 1
    return table_item


def add_item_to_list(content_item, item_date, item_id, list_widget, tooltip=None):
    """Render some item to a QList.

    Args:
        content_item (TYPE): Description
        item_date (TYPE): Description
        item_id (TYPE): Description
        list_widget (TYPE): Description
        tooltip (None, optional): Description

    Returns:
        TYPE: Description
    """
    item = QtWidgets.QListWidgetItem(f"{item_date} \t {item_id}")
    if tooltip:
        item.setToolTip(tooltip)
    item.setData(1, content_item)
    list_widget.addItem(item)
    return item


def add_item_to_tree(content_item, parent, cols, tooltip=None):
    """Render some item to a QTree.

    Args:
        content_item (TYPE): Description
        parent (TYPE): Description
        cols (TYPE): Description
        tooltip (None, optional): Description

    Returns:
        TYPE: Description
    """
    item_node = customqt.TreeWidgetItem(
        parent, cols
    )  # QtWidgets.QTreeWidgetItem(parent, cols)
    item_node.setData(1, QtCore.Qt.UserRole, content_item)
    if tooltip:
        item_node.setToolTip(1, tooltip)
    return item_node


def select_table_item(table, content_item):
    """Select a row in a table corresponding to a given object.

    Args:
        table (QTableWidget): Table to traverse
        content_item (TYPE): Object to look for
    """
    # deselect first
    for selected_range in table.selectedRanges():
        table.setRangeSelected(selected_range, False)

    uid_item = (
        table.findItems(str(content_item.uid), QtCore.Qt.MatchExactly)[0]
        if len(table.findItems(str(content_item.uid), QtCore.Qt.MatchExactly)) > 0
        else None
    )
    if uid_item:
        row = uid_item.row()
        # select content_item row
        item_range = QtWidgets.QTableWidgetSelectionRange(
            row, 0, row, table.columnCount() - 1
        )
        table.setRangeSelected(item_range, True)
        table.setCurrentItem(uid_item)


"""
#
#   FORMAT WIDGETS
#
#
"""


def resize_tree_columns(treewidget):
    """Resize the columns of a QTreeWidget to fit the headers.

    Args:
        treewidget (QTreeWidget): QTreeWidget to resize
    """
    for i in range(1, treewidget.columnCount()):
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
    """Open a dialog asking user if they want to save and,
    if confirmed, save the project.

    Args:
        dialog (TYPE): Description
        app_data (api.AppData): Application data containing the project data

    Returns:
        bool: True, if not canceled
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
    """Open a dialog asking user if they are sure to proceed.

    Args:
        dialog (QDialog): Parent dialog to the prompt

    Returns:
        bool: True if sure
    """
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
    """Open a dialog to confirm the deletion.

    Since we can only delete objects from their respective edit dialog, this prompt,
    if confirmed, closes the parent dialog with the value -1.

    Args:
        dialog (QDialog): Parent dialog to the prompt
        object (TYPE): Object to delete

    Returns:
        bool: True if deleted
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
    """Import a *.json file.

    Args:
        file_path (TYPE): path to the file
        decoder (TYPE, optional): the decoder (default: json.JSONDecoder)

    Returns:
        dict: Decoded JSON
    """
    output = None
    with open(file_path, "r") as file:
        output = json.load(file, object_hook=decoder().object_hook)
    return output


def to_json_file(data, save_path, *, encoder=json.JSONEncoder):
    """Export data to a *.json file.

    Args:
        data (any): Data to export
        save_path (Path): destination path of the file
        encoder (JSONEncoder, optional): the encoder (default: json.JSONEncoder)
    """
    with open(save_path, "w") as file:
        json.dump(data, file, cls=encoder, indent=4)


def xlsx2pdf(input_path, filename):
    """Export PDF from xlsx-file.

    Args:
        input_path (Path): path of xlsx-file
        filename (str): Filename of the PDF

    Returns:
        (Path, Path): Save path, filename
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
    """Convert an ID containing letters into a number to order the table cell.

    Args:
        cost_group_id (str): ID of the cost group

    Returns:
        int: Corresponding ordinal number
    """
    # add 1000 to make the id be listed after the last regular cost group
    id = 1000 + int("".join([f"{ord(char)}" for char in cost_group_id]))
    return id


"""
#   input amounts
"""


def input_to_float(input_1):
    """Convert the text of an QLineEdit to a float.

    Args:
        input_1 (QLineEdit): Float number

    Returns:
        float: Amount as float
    """
    # Check if it is an actual number
    if input_1.text().replace(",", "").replace(".", "").isnumeric():
        return str_to_float(input_1.text())
    else:
        return float(0)


def two_inputs_to_float(input_1, input_2):
    """Convert the texts of two QLineEdits where the decimals are in a seperated to a float.

    Args:
        input_1 (QLineEdit): Whole number
        input_2 (QLineEdit): Decimals

    Returns:
        float: Amount as float
    """
    input_1 = input_1.text() if input_1.text().isnumeric() else "0"
    input_2 = input_2.text() if input_2.text().isnumeric() else "0"
    amount = ".".join([input_1, input_2])
    return str_to_float(amount)


def str_to_float(string):
    """Convert a string to float.

    Args:
        string (str): Number

    Returns:
        float: Number rounded to two decimals
    """
    return rnd(float(string.replace(",", ".")))


"""
#   output amounts
"""


def amount_str(float, currency=""):
    """Generate a amount string from a float.

    Args:
        float (float): Amount
        currency (str, optional): Currency abbreviation

    Returns:
        str: Nicely formatted amount string
    """
    if len(currency) > 0:
        currency = f" {currency}"

    if rnd(float) != 0:
        amount = (
            "{:,.2f}".format(rnd(float))
            .replace(".", "X")
            .replace(",", ".")
            .replace("X", ",")
        )
        return f"{amount}{currency}"
    else:
        return f"-{currency}"


"""
#   output percent string
"""


def percent_str(float):
    """Generate a percent string from a float.

    Args:
        float (float): Percent

    Returns:
        str: Nicely formatted percent string
    """
    if rnd(float) != 0:
        return "{:.1f}".format(rnd(float)).replace(".", ",")
    else:
        return "-"


def percent_str_w_sign(float):
    """Generate a percent string with the percent sign ("%") from a float.

    Args:
        float (float): Percent

    Returns:
        str: Nicely formatted percent string
    """
    return " ".join([percent_str(float), "%"])


"""
#   handle numbers
"""


def rnd(amount):
    """Round a number to two decimals.

    Args:
        amount (float): Number to round

    Returns:
        float: rounded number
    """
    return float(round(amount, 2))


"""
#   QDate to String
"""


def qdate_to_str(qdate, format="%d.%m.%Y"):
    """Convert a QDate to a datetime.Date.

    Args:
        qdate (QDate): Date to convert
        format (str, optional): format of the target date

    Returns:
        datetime.Date: Converted date
    """
    return qdate.toPyDate().strftime(format)


"""
#   datetime.now() string
"""


def now_str(format="%Y-%m-%d_%H%M%S"):
    """Get a string of the current timestamp.

    Args:
        format (str, optional): Format of the string

    Returns:
        str: String of the timestamp
    """
    return datetime.datetime.now().strftime(format)


def today_str(format="%Y-%m-%d"):
    """Get a string of the current date.

    Args:
        format (str, optional): Format of the string

    Returns:
        str: String of the date today
    """
    return datetime.datetime.today().strftime(format)
