"""
#
#   API
#   The API of the data structure.
#
#
"""
import debug

DEFAULT_LANGUAGE = "de-DE"
DEFAULT_CURRENCY = "€"
DEFAULT_VAT = 0.19
DEFAULT_SYP_DIR = "G:/SYP/"
DEFAULT_SAVE_DIR = "projects"
DEFAULT_LANG_DIR = "lang"
DEFAULT_AUTOSAVE_SUBDIR = "autosaves"
DEFAULT_TEMPLATE_SUBDIR = "templates"
DEFAULT_INVOICE_CHECK_SUBDIR = "invoice_check"
DEFAULT_OVERVIEWS_SUBDIR = "overviews"
DEFAULT_LOG_FILENAME = 'log.log'
import main # just for app directory
APP_DIRECTORY = main.APP_DIRECTORY
del main

import os
import json
from pathlib import Path
import webbrowser # for opening directory windows
import appdirs # for user data/app config paths

import zipr, importr, templatr, pdfexportr, encoder, decoder
from ui import helper
from core.obj import  (proj, corp, arch)

class AppData:
    """ Contains the project (if one is loaded) and is basically the interface
    of the app.

    Instance variables:
    config -- the basic configuration (i.e. dirs, vat, lang, ...)
    project -- the currently loaded project
    """
    def __init__(self, project=None, init_companies=None, init_trades=None):
        # app config
        self.config = None
        self.load_app_config()
        # project
        self._project = project

    #   Project
    #   The loaded project. Setter to make sure its a proj.Project object.
    @property
    def project(self):
        return self._project
    @project.setter
    def project(self, project):
        if isinstance(project, proj.Project):
            self._project = project
        else:
            raise TypeError("project is not an proj.Project type.")

    #   Titles (dict)
    #   The titles of the language. This dict contains all translations. So far only the header of tables are affected
    #   but at some point also messages, buttons and everything else will be controlled by this instance.
    @property
    def titles(self):
        return self.get_titles()

    """
    #
    #   NEW, OPEN, SAVE, IMPORT, EXPORT
    #   Functions to create, open and save a project and
    #   import/export companies/cost groups/trades.
    #
    """
    @debug.log
    def new_project(self, args):
        """ Create new projekt. """
        new_project = proj.Project(**args, config=self.get_init_proj_config())
        self.project = new_project

        # companies, cost groups and trades are only for initializing a project
        self.project.companies = self.get_init_companies()
        self.project.cost_groups = self.get_init_cost_groups()
        self.project.trades = self.get_init_trades()
        # init cost_groups and trades need to be restored
        self.restore_pointers_after_import()

        return new_project

    @debug.log
    def save_project(self, save_path):
        """ Save loaded project. """
        zipr.save_project(save_path, self)
        self.set_usersave_path(save_path)
        self.save_app_config()

    @debug.log
    def autosave_project(self):
        """ Create an autosave of the loaded project. """
        autosave_path, autosave_datetime = self.get_autosave_path_datetime()
        #   Create directory if non-existing
        if not autosave_path.parent.exists():
            autosave_path.parent.mkdir()
        #   Save project
        zipr.save_project(autosave_path, self)
        #   Set the save path in the app and project config
        self.set_last_autosave_path_(autosave_path, autosave_datetime)
        #   Save the app config
        self.save_app_config()

    @debug.log
    def delete_old_autosaves(self):
        """ Delete autosaves of loaded project, if the number of autosaves
        exceeds the max_autosaves value defined in the config.
        """
        max_autosaves = self.config["max_autosaves"]
        debug.debug_msg(f"deleting old autosaves (max_autosaves={max_autosaves})...")
        autosave_dir_path = self.get_autosave_dir()
        file_suffix = self.get_autosave_filename_suffix()
        if autosave_dir_path.is_dir():
            autosaves = [f for f in autosave_dir_path.iterdir()
                            if f.suffix == file_suffix
                            and (autosave_dir_path / f).is_file()]
            autosaves.sort(reverse=True) # reversed, so the oldest save(s) gets deleted
            for autosave in autosaves[max_autosaves:]:
               (autosave_dir_path / autosave).unlink()
            debug.debug_msg(f"...{len(autosaves[max_autosaves:])} file(s) deleted...")
        else:
            debug.debug_msg("autosave dir does not exist. Nothing to delete...")

    @debug.log
    def load_project(self, file_path):
        """ Load a saved project from file. """
        loaded_args = zipr.open_project(file_path)
        self.config["loaded_save_path"] = str(Path(file_path))
        self.project = loaded_args["project"]
        self.project.config = loaded_args["project_config"]
        self.project.project_cost_calculations = loaded_args["project_cost_calculations"]
        self.project.companies = loaded_args["companies"]
        self.project.trades = loaded_args["trades"]
        self.project.invoices = loaded_args["invoices"]
        self.project.jobs = loaded_args["jobs"]
        self.project.cost_groups = loaded_args["cost_groups"]

        #   Restore the pointers.
        #   These are lost when saving and recreated using uids
        self.restore_pointers()

        return self.project

    """
    #   RESTORING A PROJECT
    #
    """
    @debug.log
    def restore_pointers(self):
        """ Restore the pointers of the objects of a project from their UID. """
        self.project.restore()

    @debug.log
    def restore_pointers_after_import(self):
        """ Restore the pointers of the objects of a project from their name/id/... . """
        self.project.restore_after_import()

    """
    #   EXPORT
    """
    @debug.log
    def export_companies(self, save_path):
        """ Export companies to a file. """
        helper.to_json_file(data=self.project.companies, save_path=save_path, encoder=encoder.CompanyEncoder)

    @debug.log
    def export_trades(self, save_path):
        """ Export trades to a file. """
        helper.to_json_file(data=self.project.trades, save_path=save_path, encoder=encoder.TradeEncoder)

    @debug.log
    def export_cost_groups(self, save_path):
        """ Export cost groups to a file. """
        helper.to_json_file(data=self.project.cost_groups, save_path=save_path, encoder=encoder.CostGroupEncoder)

    """
    #   IMPORT
    """
    @debug.log
    def import_project(self, file_path):
        """ Import a project from a *-Kostenfortschreibung.xlsx file. """
        kf_importer = importr.KFImporter(file_path=file_path)
        kf_importer.import_data()
        kf_importer.create_objects()

        project = proj.Project(config=self.get_init_proj_config(), cost_groups=self.get_init_cost_groups(),
                                identifier=kf_importer.identifier, companies=kf_importer.companies,
                                trades=kf_importer.trades, jobs=kf_importer.jobs, invoices=kf_importer.invoices)

        self.project = project
        self.restore_pointers_after_import()

    @debug.log
    def import_companies(self, file_path):
        """ Import companies from a companies.json file. """
        imported_companies = helper.from_json_file(file_path=file_path, decoder=decoder.CompanyDecoder)
        for import_company in imported_companies:
            if import_company.name not in [company.name for company in self.project.companies]:
                import_company.uid.reset_uid()
                import_company.restore_after_import(self.project)
                self.project.add_company(import_company)
            else:
                debug.log_warning(f"Skipping the import of company {import_company.name} because there already exists a company with the same name!")

    @debug.log
    def import_trades(self, file_path):
        """ Import trades from a trades.json file. """
        imported_trades = helper.from_json_file(file_path=file_path, decoder=decoder.TradeDecoder)
        for import_trade in imported_trades:
            if import_trade.name not in [trade.name for trade in self.project.trades]:
                import_trade.uid.reset_uid()
                import_trade.restore_after_import(self.project)
                self.project.add_trade(import_trade)
            else:
                debug.log_warning(f"Skipping the import of trade {import_trade.name} because there already exists a trade with the same name!")

    @debug.log
    def import_cost_groups(self, file_path):
        """ Import cost_groups from a cost_groups.json file. """
        imported_cost_groups = helper.from_json_file(file_path=file_path, decoder=decoder.CostGroupDecoder)
        for import_cost_group in imported_cost_groups:
            if import_cost_group.id not in [cost_group.id for cost_group in self.project.cost_groups]:
                import_cost_group.uid.reset_uid()
                self.project.add_cost_group(import_cost_group)
            else:
                debug.log_warning(f"Skipping the import of cost_group {import_cost_group.id} because there already exists a trade with the same id!")
        #   Restore the link within cost_groups (parent).
        #   Since they are connected within, this can only happen
        #   once the import is complete
        for cost_group in self.project.cost_groups:
            cost_group.restore_after_import(self.project)



    """
    #
    #   OUTPUT
    #   Functions for exporting data into new formats (for printing or other purposes)
    #
    """
    # TODO
    def output_cost_stand_cost_groups_ov(self, app_data):
        pass

    # TODO
    def output_cost_stand_trades_ov(self, app_data):
        pass

    def output_invoice_check(self, invoice, create_at_path):
        """ Output an invoice check of a given invoice as *.xlsx file.

        Arguments:
        invoice -- the invoice providing the data
        create_at_path -- the path to the directory where to make the file
        """
        invoice_check_xlsx = templatr.InvoiceCheckExcelTemplate(app_data=self,
                                                            invoice=invoice,
                                                            save_dir=create_at_path)
        # Create xlsx-File
        invoice_check_xlsx.make_file()
        return (invoice_check_xlsx.save_path, invoice_check_xlsx.filename)


    def output_ov_by_trades(self, create_at_path):
        """ Output an overview of the project costs ordered by trades of the loaded project as *.xlsx file.

        Arguments:
        create_at_path -- the path to the directory where to make the file
        """
        overview_xlsx = templatr.TradesOVExcelTemplate(app_data=self,
                                                            save_dir=create_at_path)
         # Create xlsx-File
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_ov_by_cost_groups(self, create_at_path):
        """ Output an overview of the project costs ordered by cost groups of the loaded project as *.xlsx file.

        Arguments:
        create_at_path -- the path to the directory where to make the file
        """
        overview_xlsx = templatr.CostGroupsOVExcelTemplate(app_data=self,
                                                            save_dir=create_at_path)
         # Create xlsx-File
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_ov_of_company(self, company, create_at_path, selected_job=None):
        """ Output an overview of the invoices of a company ordered by job of a given company as *.xlsx file.

        Arguments:
        company -- the selected company
        create_at_path -- the path to the directory where to make the file
        selected_job -- if given, only the data of that particular job is shown
        """
        overview_xlsx = templatr.CompanyOVExcelTemplate(app_data=self,
                                                            company=company,
                                                            save_dir=create_at_path,
                                                            selected_job=selected_job)
         # Create xlsx-File
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_pcc_ov_cost_groups(self, pcc, cost_groups, create_at_path, filename=None):
        """ Output an overview of a project cost calculation ordered by cost groups as *.xlsx file.

        Arguments:
        pcc -- the project cost calculation providing the data
        cost_groups -- the cost groups shown in the doc (e.g. used to only show main cost groups)
        create_at_path -- the path to the directory where to make the file
        filename -- if given, the file will use this as its filename
        """
        overview_xlsx = templatr.PCCCostGroupsOVExcelTemplate(app_data=self,
                                                            pcc=pcc,
                                                            cost_groups=cost_groups,
                                                            save_dir=create_at_path,
                                                            filename=filename)
        # Create xlsx-File
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_pcc_ov_trades(self, pcc, create_at_path, filename=None):
        """ Output an overview of a project cost calculation ordered by trades as *.xlsx file.

        Arguments:
        pcc -- the project cost calculation providing the data
        create_at_path -- the path to the directory where to make the file
        filename -- if given, the file will use this as its filename
        """
        overview_xlsx = templatr.PCCTradesOVExcelTemplate(app_data=self,
                                                            pcc=pcc,
                                                            save_dir=create_at_path,
                                                            filename=filename)
        # Create xlsx-File
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    """
    #
    #   UTILITY FUNCTIONS
    #
    """
    def project_loaded(self):
        """ Returns if a project is loaded. """
        return True if self.project else False

    @debug.log
    def get_titles(self):
        """ Load the titles of the selected languge. """
        file_path = self.get_lang_dir() / (self.get_lang() + ".json")
        return helper.from_json_file(file_path)

    """ util
    #
    #   APP CONFIG
    #
    """
    @debug.log
    def load_app_config(self):
        """ Load the app config from file.
        If it doesn't exist or is faulty, it will be reset to the default app config.
        """
        app_config_path = self.get_app_config_path()
        self.create_dir(app_config_path)
        if app_config_path.is_file():
            debug.debug_msg("app_config.json found, loading into app_data.config...")
            try:
                with open(app_config_path, "r") as file:
                    self.config = json.load(file)
            except:
                debug.warning_msg("app_config.json not valid, resetting app config...")
                with open(app_config_path, "w") as file:
                    default_app_config = self.get_default_config()
                    json.dump(default_app_config, file, indent=4)
                    debug.debug_msg("app_config.json has been set up")
                    self.config = default_app_config
            finally:
                debug.debug_msg("app_data.config loaded!")
        else:
            debug.debug_msg("app_config.json has not been set up, initializing default config...")
            with open(app_config_path, "w") as file:
                default_app_config = self.get_default_config()
                json.dump(default_app_config, file, indent=4)
                debug.debug_msg("app_config.json has been set up")
                self.config = default_app_config
                debug.debug_msg("app_data.config loaded!")

    @debug.log
    def save_app_config(self):
        """ Save the app config to a file. """
        app_config_path = self.get_app_config_path()
        with open(app_config_path, "w") as file:
            data = self.config
            json.dump(data, file, indent=4)

    """ util
    #
    #   CONFIG INFO
    #
    """
    def get_currency(self):
        """ Get the currency as a string. """
        return self.config["currency"]

    def get_lang(self):
        """ Get the language as a string in locale format, i.e. 'de-DE' for German. """
        return self.config["language"]

    """ util>config
    #   PATHS & DIRECTORIES
    """
    # CREATE
    @debug.log
    def create_dir(self, dir_path):
        """ Create directory if non-existing. """
        if not dir_path.exists():
            dir_path.mkdir()

    # OPEN
    @debug.log
    def open_dir(self):
        """ Open the app directory. """
        path = self.get_dir()
        webbrowser.open(path)

    @debug.log
    def open_autosave_dir(self):
        """ Open the autosave directory. """
        path = self.get_autosave_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_save_dir(self):
        """ Open the save directory. """
        path = self.get_save_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_invoice_check_dir(self):
        """ Open the invoice check directory of the current project (in SYP directory).
        Created to get the path to export the invoice check files as PDF.
        """
        path = self.get_invoice_check_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_overviews_dir(self):
        """ Open the directory where the overviews are output of the current project (in app directory). """
        path = self.get_app_overviews_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_client_correspondence_dir(self):
        """ Open the client correspondence directory of the current project (in SYP directory).
        Created to get the path to export the invoice check files as PDF.
        """
        path = self.get_client_correspondence_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_syp_dir(self):
        """ Open the SYP directory. """
        path = self.get_syp_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    @debug.log
    def open_project_dir(self):
        """ Open the project directory (in SYP directory). """
        path = self.get_project_dir()
        if path.exists():
            webbrowser.open(path)
        else:
            self.open_dir()

    # GET
    def get_app_config_path(self):
        """ Get the app config path. It is located in the systems appdata directory of the machine. """
        # TODO: set this path dependent on the machine
        dir = appdirs.user_data_dir("SYP-Kostenfortschreibung", "Timo_Yu")
        filename = "app_config.json"
        return Path(dir, filename)

    def get_dir(self):
        """ Get the app directory. """
        return Path(APP_DIRECTORY)

    def get_syp_dir(self):
        """ Get the SYP directory. """
        return Path(self.config["SYP_dir"])

    def get_project_dir(self):
        """ Get the project directory (in SYP directory), if a project is loaded. """
        if self.project:
            return Path(self.config["SYP_dir"], "02 Projekte", self.project.identifier)

    def get_app_invoice_check_dir(self):
        """ Get the invoice check directory (in app directory), if a project is loaded. """
        if self.project:
            return Path(self.config["save_dir"], self.project.identifier, self.config["invoice_check_subdir"])

    def get_app_overviews_dir(self):
        """ Get the directory of overviews (in app directory), if a project is loaded. """
        if self.project:
            return Path(self.config["save_dir"], self.project.identifier, self.config["overviews_subdir"])

    def get_autosave_dir(self):
        """ Get the autosave directory (in app directory), if a project is loaded. """
        return Path(self.config["save_dir"], self.config["autosave_subdir"])

    def get_save_dir(self):
        """ Get the save directory (in app directory). """
        return Path(self.config["save_dir"])

    def get_lang_dir(self):
        """ Get the directory of language files (in app directory). """
        return Path(self.config["lang_dir"])

    def get_invoice_check_dir(self):
        """ Get the invoice check directory (in SYP directory). """
        #  TODO: maybe outsource this into the config
        invoice_check_dir = "03 Kosten/01 Rechnungsprüfung/"
        return Path(self.get_project_dir(), invoice_check_dir)

    def get_client_correspondence_dir(self):
        """ Get the client correspondence directory (in SYP directory). """
        #  TODO: maybe outsource this into the config
        correspondence_dir = "02 Schriftverkehr/Bauherr/Ausgang"
        return Path(self.get_project_dir(), correspondence_dir)

    def get_autosave_filename_suffix(self):
        """ Get the suffix of an autosave for the loaded project. """
        autosave_filename_suffix = f"autosave-{self.project.identifier}.project"
        return autosave_filename_suffix

    def get_autosave_path_datetime(self):
        """ Get the path (as Path) and date (as string) for an autosave. """
        autosave_datetime = helper.now_str()
        autosave_filename = f"{autosave_datetime}-{self.get_autosave_filename_suffix()}"
        autosave_path = Path(self.get_dir(), self.get_autosave_dir(), autosave_filename)
        return autosave_path, autosave_datetime

    def get_invoice_check_folder_name(self, invoice):
        """ Get the foldername (w/ date and invoice id) for an invoice check. """
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-{invoice.id}"
            return dir_name

    def get_company_overview_folder_name(self, company):
        """ Get the foldername (w/ project id and company name) for a project cost overview of a company. """
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-{company.name.replace(' ', '_').replace('.', '')}"
            return dir_name

    def get_trades_overview_folder_name(self, trade=None):
        """ Get the foldername (w/ project id) for a project cost overview by trades. """
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-trades"
            if trade:
                dir_name += f"-{trade.name.replace(' ', '_')}"
            return dir_name

    def get_cost_groups_overview_folder_name(self, cost_group=None):
        """ Get the foldername (w/ project id) for a project cost overview by cost_groups. """
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-cost_groups"
            if cost_group:
                dir_name += f"-{cost_group.id}"
            return dir_name

    def get_pcc_overview_folder_name(self, pcc):
        """ Get the foldername (w/ project id and pcc name) for a project cost calculation overview by cost_groups. """
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-{pcc.name}"
            return dir_name

    def get_loaded_save_path(self):
        """ Get the path of the loaded project. """
        return Path(self.config["loaded_save_path"])

    def set_usersave_path(self, save_path, datetime_str=helper.now_str()):
        """ Set the path of the usersave in the configs. """
        self.project.set_save_path(save_path, datetime_str)
        self.config["loaded_save_path"] = str(save_path)

    def set_last_autosave_path_(self, save_path, datetime_str=helper.now_str()):
        """ Set the path of the autosave in the configs. """
        self.project.set_autosave_path(save_path, datetime_str)
        self.config["last_auto_save"]["datetime"] = datetime_str
        self.config["last_auto_save"]["path"] = str(save_path)

    """ util
    #
    #   INIT and DEFAULT VALUES
    #
    """
    @debug.log
    def get_init_proj_config(self):
        """ Get an initial project config for creating a new project. """
        init_proj_config = {
            "currency": self.config["currency"],
            "default_vat":  self.config["default_vat"],
            "user_save": {"datetime": None,"path": None},
            "last_auto_save": {"datetime": None,"path": None}
        }
        return init_proj_config

    @debug.log
    def get_init_companies(self):
        """ Get an initial companies for a new project. """
        file_path = "resources/default_companies.json"
        companies = helper.from_json_file(file_path=file_path, decoder=decoder.CompanyDecoder)
        return companies

    @debug.log
    def get_init_trades(self):
        """ Get an initial trades for a new project. """
        file_path = Path("resources/default_trades.json")
        trades = helper.from_json_file(file_path=file_path, decoder=decoder.TradeDecoder)
        return trades

    @debug.log
    def get_init_cost_groups(self):
        """ Get an initial cost groups for a new project. """
        file_path = Path("resources/default_cost_groups.json")
        cost_groups = helper.from_json_file(file_path=file_path, decoder=decoder.CostGroupDecoder)
        return cost_groups

    @debug.log
    def get_default_config(self):
        """ Get an initial app config. """
        default_config = {
        "language": DEFAULT_LANGUAGE,
        "currency": DEFAULT_CURRENCY,
        "default_vat": DEFAULT_VAT,
        "SYP_dir": DEFAULT_SYP_DIR,
        "save_dir": DEFAULT_SAVE_DIR,
        "lang_dir": DEFAULT_LANG_DIR,
        "autosave_subdir": DEFAULT_AUTOSAVE_SUBDIR,
        "template_subdir": DEFAULT_TEMPLATE_SUBDIR,
        "invoice_check_subdir": DEFAULT_INVOICE_CHECK_SUBDIR,
        "overviews_subdir": DEFAULT_OVERVIEWS_SUBDIR,
        "loaded_save_path": None,
        "last_auto_save": {
            "datetime": None,
            "path": None
        },
        "autosave_time": 240000,
        "max_autosaves": 5,
        "window_size": {
            "height": None,
            "width": None
        },
        "building_classes": [
                "GK 1a",
                "GK 1b",
                "GK 2",
                "GK 3",
                "GK 5"
        ],
        "planning_phases": [
                ("LP1", "Grundlagenermittlung"),
                ("LP2", "Vorplanung"),
                ("LP3", "Entwurfsplanung"),
                ("LP4", "Genehmigungsplanung"),
                ("LP5", "Ausführungsplanung"),
                ("LP6", "Vorbereitung der Vergabe"),
                ("LP7", "Mitwirkung bei der Vergabe"),
                ("LP8", "Objektüberwachung – Bauüberwachung und Dokumentation"),
                ("LP9", "Objektbetreuung")
        ],
        "log_filename": DEFAULT_LOG_FILENAME,
        "debug": False
        }
        return default_config

    """
    #
    #   DEBUG
    #
    #
    """
    def debug_on(self):
        """ Check whether the debug mode is on. """
        return self.config["debug"]
