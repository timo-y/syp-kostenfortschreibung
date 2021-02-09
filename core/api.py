"""
#
#   API
#   The AppData-class is the API of the data structure.
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

import main # just for root directory
MAIN_DIRECTORY = main.MAIN_DIRECTORY
del main

import os
import webbrowser
import json
import shutil

import zipr, importr, templatr, pdfexportr, encoder, decoder
from ui import helper
from core.obj import  (proj, corp, arch)


class AppData:
    def __init__(self, project=None, init_companies=None, init_trades=None):
        self.config = None
        self.load_app_config()

        #   TITLES (dict)
        #   The titles of the language. This dict contains all translations. So far only the header of tables are affected
        #   but at some point also messages, buttons and everything else will be controlled by this instance.
        self.titles = self.get_titles()

        self._project = project

    @property
    def project(self):
        return self._project
    @project.setter
    def project(self, project):
        if isinstance(project, proj.Project):
            self._project = project
        else:
            raise TypeError("project is not an proj.Project type.")

    """
    #
    #   CREATE NEW PROJECT
    #   Functions for the initialization of a new project
    #
    """
    @debug.log
    def new_project(self, args):
        new_project = proj.Project(**args, config=self.get_init_proj_config())
        self.project = new_project

        # companies and trades are only for initiating a project
        self.project.companies = self.get_init_companies()
        self.project.cost_groups = self.get_init_cost_groups()
        self.project.trades = self.get_init_trades()
        # init cost_groups and trades need to be restored
        self.restore_pointers_after_import()

        return new_project

    """
    #
    #   OPEN, SAVE, IMPORT, EXPORT
    #   Functions for the file-programm-exchange
    #
    """
    """
    #   SAVING & LOADING PROJECT
    """
    @debug.log
    def save_project(self, save_path):
        zipr.save_project(save_path, self)
        self.set_usersave_path(save_path)
        self.save_app_config()

    @debug.log
    def autosave_project(self):
        autosave_path, autosave_datetime = self.get_autosave_path_datetime()
        #   Create directory if non-existing
        if not os.path.exists(os.path.dirname(autosave_path)):
            os.makedirs(os.path.dirname(autosave_path))
        #   Save project
        zipr.save_project(autosave_path, self)
        #   Set the save path in the app and project config
        self.set_last_autosave_path_(autosave_path, autosave_datetime)
        #   Save the app config
        self.save_app_config()

    @debug.log
    def delete_old_autosaves(self):
        max_autosaves = self.config["max_autosaves"]
        debug.debug_msg(f"deleting old autosaves (max_autosaves={max_autosaves})...")
        autosave_dir_path = self.get_autosave_dir()
        file_suffix = self.get_autosave_filename_suffix()
        if os.path.isdir(autosave_dir_path):
            autosaves = [f for f in os.listdir(autosave_dir_path) if f.endswith(file_suffix) and os.path.isfile(os.path.join(autosave_dir_path, f))]
            autosaves.sort(reverse=True) # reversed, so the oldest save(s) gets deleted
            for autosave in autosaves[max_autosaves:]:
                os.remove(os.path.join(autosave_dir_path, autosave))
            debug.debug_msg(f"...{len(autosaves[max_autosaves:])} file(s) deleted...")
        else:
            debug.debug_msg("autosave dir does not exist. Nothing to delete...")

    @debug.log
    def load_project(self, file_path):
        loaded_args = zipr.open_project(file_path)
        self.config["loaded_save_path"] = file_path
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
    #   Restore the pointers of the objects of a projcet
    """
    @debug.log
    def restore_pointers(self):
        self.project.restore()

    @debug.log
    def restore_pointers_after_import(self):
        self.project.restore_after_import()
    """
    #   EXPORT
    """
    @debug.log
    def export_companies(self, save_path):
        helper.to_json_file(data=self.project.companies, save_path=save_path, encoder=encoder.CompanyEncoder)

    @debug.log
    def export_trades(self, save_path):
        helper.to_json_file(data=self.project.trades, save_path=save_path, encoder=encoder.TradeEncoder)

    @debug.log
    def export_cost_groups(self, save_path):
        helper.to_json_file(data=self.project.cost_groups, save_path=save_path, encoder=encoder.CostGroupEncoder)

    """
    #   IMPORT
    """
    @debug.log
    def import_project(self, file_path):
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
    """
    #   INVOICE CHECK
    """
    @debug.log
    def run_invoice_check(self, invoice, curr_job_only):
        folder_name = self.get_invoice_check_folder_name(invoice)
        create_at_path = os.path.join(self.get_app_invoice_check_dir(), folder_name)
        """
        #
        #   Create xlsx files
        #
        """
        xlsx_files = [
            self.output_invoice_check(invoice=invoice,
                                    create_at_path=create_at_path),
            self.output_ov_of_company(company=invoice.company,
                                  create_at_path=create_at_path,
                                  selected_job=invoice.job if curr_job_only else None
                                  )
        ]
        """
        #
        #   Convert to PDF
        #
        """
        pdf_files = [helper.xlsx2pdf(*file) for file in xlsx_files]
        """
        #
        #   Copy to Folders
        #
        """
        #   Invoice check path
        inv_check_path = os.path.join(self.get_invoice_check_dir(), folder_name)

        # create directory if non-existing
        if not os.path.exists(inv_check_path):
            os.makedirs(inv_check_path)
        for file in pdf_files:
            shutil.copy(file[0], os.path.join(inv_check_path, file[1]))

        #   Correspondence path
        correspondence_path = os.path.join(self.get_client_correspondence_dir(), folder_name)

        # create directory if non-existing
        if not os.path.exists(correspondence_path):
            os.makedirs(correspondence_path)
        for file in pdf_files:
            shutil.copy(file[0], os.path.join(correspondence_path, file[1]))

    """
    #   PCC OVERVIEW
    """
    @debug.log
    def run_pcc_overview(self, pcc):
        folder_name = self.get_pcc_overview_folder_name(pcc)
        create_at_path = os.path.join(self.get_app_overviews_dir(), folder_name)
        """
        #
        #   Create xlsx files
        #
        """
        date = helper.today_str()
        filename_1 = f"{date}-costcalculation_overview-main-{self.project.identifier}"
        filename_2 = f"{date}-costcalculation_overview-all-{self.project.identifier}"
        xlsx_files = [
            self.output_pcc_ov_cost_groups(pcc=pcc,
                                            cost_groups=self.project.main_cost_groups,
                                            create_at_path=create_at_path,
                                            filename=filename_1),
            self.output_pcc_ov_cost_groups(pcc=pcc,
                                            cost_groups=self.project.cost_groups,
                                            create_at_path=create_at_path,
                                            filename=filename_2),
            self.output_pcc_ov_trades(pcc=pcc,
                                            create_at_path=create_at_path)
        ]
        """
        #
        #   Convert to PDF
        #
        """
        pdf_files = [helper.xlsx2pdf(*file) for file in xlsx_files]


    """
    #   OUTPUT
    """
    def output_invoice_check(self, invoice, create_at_path):
        # Create xlsx-File
        invoice_check_xlsx = templatr.InvoiceCheckExcelTemplate(app_data=self,
                                                            invoice=invoice,
                                                            save_dir=create_at_path)
        invoice_check_xlsx.make_file()
        return (invoice_check_xlsx.save_path, invoice_check_xlsx.filename)

    # TODO
    def output_ov_by_trades(self):
        pass

    # TODO
    def output_ov_by_job(self):
        pass

    def output_ov_of_company(self, company, create_at_path, selected_job=None):
        # Create xlsx-File
        overview_xlsx = templatr.CompanyOVExcelTemplate(app_data=self,
                                                            company=company,
                                                            save_dir=create_at_path,
                                                            selected_job=selected_job)
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_pcc_ov_cost_groups(self, pcc, cost_groups, create_at_path, filename=None):
        # Create xlsx-File
        overview_xlsx = templatr.PCCCostGroupsOVExcelTemplate(app_data=self,
                                                            pcc=pcc,
                                                            cost_groups=cost_groups,
                                                            save_dir=create_at_path,
                                                            filename=filename)
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    def output_pcc_ov_trades(self, pcc, create_at_path, filename=None):
        # Create xlsx-File
        overview_xlsx = templatr.PCCTradesOVExcelTemplate(app_data=self,
                                                            pcc=pcc,
                                                            save_dir=create_at_path,
                                                            filename=filename)
        overview_xlsx.make_file()
        return (overview_xlsx.save_path, overview_xlsx.filename)

    """
    #
    #   UTILITY FUNCTIONS
    #
    """

    """
    #   APP CONFIG
    """
    @debug.log
    def load_app_config(self):
        if os.path.isfile("app_config.json"):
            debug.debug_msg("app_config.json found, loading into app_data.config...")
            with open("app_config.json", "r") as file:
                self.config = json.load(file)
                debug.debug_msg("app_data.config loaded!")
        else:
            debug.debug_msg("app_config.json has not been set up, initializing default config...")
            with open("app_config.json", "w") as file:
                default_app_config = self.get_default_config()
                json.dump(default_app_config, file, indent=4)
                debug.debug_msg("app_config.json has been set up")
                self.config = default_app_config
                debug.debug_msg("app_data.config loaded!")
    """
    #   LANGUAGE TITLES
    """
    @debug.log
    def get_titles(self):
        file_path = os.path.join(self.get_lang_dir(), self.get_lang()+".json")
        return helper.from_json_file(file_path)

    @debug.log
    def save_app_config(self):
        with open("app_config.json", "w") as file:
            data = self.config
            json.dump(data, file, indent=4)

    """ util
    #
    #   CONFIG INFO
    #
    """
    def project_loaded(self):
        return True if self.project else False

    def get_currency(self):
        return self.config["currency"]

    def get_lang(self):
        return self.config["language"]

    """ util>config
    #   PATHS & DIRECTORIES
    """
    # CREATE
    @debug.log
    def create_dir(self, dir_path):
        # create directory if non-existing
        if not os.path.exists(os.path.dirname(dir_path)):
            os.makedirs(os.path.dirname(dir_path))

    # OPEN
    @debug.log
    def open_dir(self):
        path = self.get_dir()
        webbrowser.open(os.path.realpath(path))

    @debug.log
    def open_autosave_dir(self):
        path = self.get_autosave_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_save_dir(self):
        path = self.get_save_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_invoice_check_dir(self):
        path = self.get_invoice_check_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_overviews_dir(self):
        path = self.get_app_overviews_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_client_correspondence_dir(self):
        path = self.get_client_correspondence_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_syp_dir(self):
        path = self.get_syp_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    @debug.log
    def open_project_dir(self):
        path = self.get_project_dir()
        if os.path.exists(path):
            webbrowser.open(os.path.realpath(path))
        else:
            self.open_dir()

    # GET
    def get_dir(self):
        dir_path = MAIN_DIRECTORY
        return dir_path

    def get_syp_dir(self):
        return self.config["SYP_dir"]

    def get_project_dir(self):
        if self.project:
            path = os.path.join(self.config["SYP_dir"], "02 Projekte", self.project.identifier)
            return path

    def get_app_invoice_check_dir(self):
        if self.project:
            path = os.path.join(self.config["save_dir"], self.project.identifier, self.config["invoice_check_subdir"])
            return path

    def get_app_overviews_dir(self):
        if self.project:
            path = os.path.join(self.config["save_dir"], self.project.identifier, self.config["overviews_subdir"])
            return path

    def get_autosave_dir(self):
        autosave_dir_path = os.path.join(self.config["save_dir"], self.config["autosave_subdir"])
        return autosave_dir_path

    def get_save_dir(self):
        save_dir_path = self.config["save_dir"]
        return save_dir_path

    def get_lang_dir(self):
        lang_dir_path = self.config["lang_dir"]
        return lang_dir_path

    def get_invoice_check_dir(self):
        #  TODO: maybe outsource this into the config
        invoice_check_dir = "03 Kosten/01 Rechnungsprüfung/"
        invoice_check_dir_path = os.path.join(self.get_project_dir(), invoice_check_dir)
        return invoice_check_dir_path

    def get_client_correspondence_dir(self):
        #  TODO: maybe outsource this into the config
        correspondence_dir = "02 Schriftverkehr/Bauherr/Ausgang"
        correspondence_dir_path = os.path.join(self.get_project_dir(), correspondence_dir)
        return correspondence_dir_path

    def get_autosave_filename_suffix(self):
        autosave_filename_suffix = f"autosave-{self.project.identifier}.project"
        return autosave_filename_suffix

    def get_autosave_path_datetime(self):
        autosave_datetime = helper.now_str()
        autosave_filename = f"{autosave_datetime}-{self.get_autosave_filename_suffix()}"
        autosave_path = os.path.join(self.get_dir(), self.get_autosave_dir(), autosave_filename)
        return autosave_path, autosave_datetime

    def get_invoice_check_folder_name(self, invoice):
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-{invoice.id}"
            return dir_name

    def get_pcc_overview_folder_name(self, pcc):
        if self.project_loaded():
            dir_name = f"{helper.now_str()}-{self.project.identifier}-{pcc.name}"
            return dir_name

    def get_loaded_save_path(self):
        return self.config["loaded_save_path"]

    def set_usersave_path(self, save_path, datetime_str=helper.now_str()):
        self.project.set_save_path(save_path, datetime_str)
        self.config["loaded_save_path"] = save_path

    def set_last_autosave_path_(self, save_path, datetime_str=helper.now_str()):
        self.project.set_autosave_path(save_path, datetime_str)
        self.config["last_auto_save"]["datetime"] = datetime_str
        self.config["last_auto_save"]["path"] = save_path

    """ util
    #
    #   INIT and DEFAULT VALUES
    #
    """
    @debug.log
    def get_init_proj_config(self):
        init_proj_config = {
            "currency": self.config["currency"],
            "default_vat":  self.config["default_vat"],
            "user_save": {"datetime": None,"path": None},
            "last_auto_save": {"datetime": None,"path": None}
        }
        return init_proj_config

    @debug.log
    def get_init_companies(self):
        file_path = "resources/default_companies.json"
        companies = helper.from_json_file(file_path=file_path, decoder=decoder.CompanyDecoder)
        return companies

    @debug.log
    def get_init_trades(self):
        file_path = "resources/default_trades.json"
        trades = helper.from_json_file(file_path=file_path, decoder=decoder.TradeDecoder)
        return trades

    @debug.log
    def get_init_cost_groups(self):
        file_path = "resources/default_cost_groups.json"
        cost_groups = helper.from_json_file(file_path=file_path, decoder=decoder.CostGroupDecoder)
        return cost_groups

    @debug.log
    def get_default_config(self):
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
        return self.config["debug"]
