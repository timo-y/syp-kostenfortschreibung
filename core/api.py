"""
#
#   API
#   The AppData-class is the API of the data structure.
#
"""
import debug

DEFAULT_LANGUAGE = "de-DE"
DEFAULT_CURRENCY = "€"
DEFAULT_VAT = 0.16
DEFAULT_SYP_DIR = "G:/SYP/"
DEFAULT_SAVE_DIR = "projects"
DEFAULT_LANG_DIR = "lang"
DEFAULT_AUTOSAVE_SUBDIR = "autosaves"
DEFAULT_TEMPLATE_SUBDIR = "templates"
DEFAULT_INVOICE_CHECK_SUBDIR = "invoice_check"
DEFAULT_LOG_FILENAME = 'info.log'

import os
import webbrowser
import json
from datetime import datetime

import zipr, templatr, pdfexportr, encoder, decoder
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
        self.set_usersave_path(save_path)
        zipr.save_project(save_path, self)
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
        debug.log_debug(f"deleting old autosaves (max_autosaves={max_autosaves})...")
        autosave_dir_path = self.get_autosave_dir()
        file_suffix = self.get_autosave_filename_suffix()

        autosaves = [f for f in os.listdir(autosave_dir_path) if f.endswith(file_suffix) and os.path.isfile(os.path.join(autosave_dir_path, f))]
        autosaves.sort(reverse=True) # reversed, so the oldest save(s) gets deleted
        for autosave in autosaves[max_autosaves:]:
            os.remove(os.path.join(autosave_dir_path, autosave))
        debug.log_debug(f"...{len(autosaves[max_autosaves:])} file(s) deleted...")

    @debug.log
    def load_project(self, filename):
        loaded_args = zipr.open_project(filename)
        self.project = loaded_args["project"]
        self.project.config = loaded_args["project_config"]
        self.project.companies = loaded_args["companies"]
        self.project.trades = loaded_args["trades"]
        self.project._invoices = loaded_args["invoices"]
        self.project.jobs = loaded_args["jobs"]
        self.project.people = loaded_args["people"]
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

    """
    #   EXPORT
    """
    @debug.log
    def export_companies(self, save_path):
        self.to_json_file(data=self.project.companies, save_path=save_path, encoder=encoder.CompanyEncoder)

    @debug.log
    def export_trades(self, save_path):
        self.to_json_file(data=self.project.trades, save_path=save_path, encoder=encoder.TradeEncoder)

    """
    #   IMPORT
    """
    @debug.log
    def import_companies(self, file_path):
        imported_companies = self.from_json_file(file_path=file_path, decoder=decoder.CompanyDecoder)
        for import_company in imported_companies:
            if import_company.name not in [company.name for company in self.project.companies]:
                import_company.uid.reset_uid()
                import_company.restore_after_import(self.project)
                self.project.add_company(import_company)
            else:
                debug.log_warning(f"Skipping the import of company {import_company.name} because there already exists a company with the same name!")

    @debug.log
    def import_trades(self, file_path):
        imported_trades = self.from_json_file(file_path=file_path, decoder=decoder.TradeDecoder)
        for import_trade in imported_trades:
            if import_trade.name not in [trade.name for trade in self.project.trades]:
                import_trade.uid.reset_uid()
                import_trade.restore_after_import(self.project)
                self.project.add_trade(import_trade)
            else:
                debug.log_warning(f"Skipping the import of trade {import_trade.name} because there already exists a trade with the same name!")

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
    def output_check_invoice(self, invoice, save_path=None):
        xlsx_template = templatr.InvoiceCheckExcelTemplate(project_identifier=self.project.identifier, app_data_config=self.config, invoice=invoice, save_path=save_path)
        xlsx_template.make_file()
        # Export PDF
        dir_path = os.path.dirname(os.path.realpath(xlsx_template.save_path))
        pdf_save_path = os.path.join(dir_path, f"{xlsx_template.default_filename}.pdf")
        pdfexportr.PDFExportr().create_pdf(xlsx_template.save_path, pdf_save_path)

    """
    #   OVERVIEWs
    """
    #TODO
    def output_ov_by_trades(self):
        pass
    #TODO
    def output_ov_by_job(self):
        pass
    #TODO
    def output_ov_by_company(self):
        pass

    """
    #
    #   UTILITY FUNCTIONS
    #
    """

    """ util
    #
    #   FILES
    #   Functions to get files, the programm needs to load (apart from project files)
    #
    """
    @debug.log
    def from_json_file(self, file_path, *, decoder=json.JSONDecoder):
        output = None
        with open(file_path, "r") as file:
            output = json.load(file, object_hook=decoder().object_hook)
        return output

    @debug.log
    def to_json_file(self, data, save_path, *, encoder=json.JSONEncoder):
        with open(save_path, "w") as file:
            json.dump(data, file, cls=encoder, indent=4)

    """
    #   APP CONFIG
    """
    @debug.log
    def load_app_config(self):
        if os.path.isfile("app_config.json"):
            debug.log_debug("app_config.json found, loading into app_data.config...")
            with open("app_config.json", "r") as file:
                self.config = json.load(file)
                debug.log_debug("app_data.config loaded!")
        else:
            debug.log_debug("app_config.json has not been set up, initializing default config...")
            with open("app_config.json", "w") as file:
                default_app_config = self.get_default_config()
                json.dump(default_app_config, file, indent=4)
                debug.log_debug("app_config.json has been set up")
                self.config = default_app_config
                debug.log_debug("app_data.config loaded!")
    """
    #   LANGUAGE TITLES
    """
    @debug.log
    def get_titles(self):
        file_path = os.path.join(self.get_lang_dir(), self.get_lang()+".json")
        return self.from_json_file(file_path)

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
    # OPEN
    @debug.log
    def open_dir(self):
        path = self.get_dir()
        webbrowser.open(os.path.realpath(path))

    @debug.log
    def open_autosave_dir(self):
        path = self.get_autosave_dir()
        webbrowser.open(os.path.realpath(path))

    @debug.log
    def open_save_dir(self):
        path = self.get_save_dir()
        webbrowser.open(os.path.realpath(path))

    @debug.log
    def open_invoice_check_dir(self):
        path = self.get_invoice_check_dir()
        webbrowser.open(os.path.realpath(path))

    # GET
    @debug.log
    def get_dir(self):
        dir_path = os.getcwd()
        return dir_path

    @debug.log
    def get_syp_dir(self):
        return self.config["SYP_dir"]

    @debug.log
    def get_autosave_dir(self):
        autosave_dir_path = os.path.join(os.getcwd(), self.config["save_dir"], self.project.identifier, self.config["autosave_subdir"])
        return autosave_dir_path

    @debug.log
    def get_save_dir(self):
        save_dir_path = os.path.join(os.getcwd(), self.config["save_dir"])
        return save_dir_path

    @debug.log
    def get_lang_dir(self):
        lang_dir_path = os.path.join(os.getcwd(), self.config["lang_dir"])
        return lang_dir_path

    @debug.log
    def get_invoice_check_dir(self):
        invoice_check_dir_path = os.path.join(os.getcwd(), self.config["save_dir"], self.project.identifier, self.config["invoice_check_subdir"])
        return invoice_check_dir_path

    @debug.log
    def get_autosave_filename_suffix(self):
        autosave_filename_suffix = f"autosave-{self.project.identifier}.project"
        return autosave_filename_suffix

    @debug.log
    def get_autosave_path_datetime(self):
        autosave_datetime = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        autosave_filename = f"{autosave_datetime}-{self.get_autosave_filename_suffix()}"
        autosave_path = os.path.join(self.get_autosave_dir(), autosave_filename)
        return autosave_path, autosave_datetime

    @debug.log
    def set_usersave_path(self, save_path, datetime_str=datetime.now().strftime('%Y-%m-%d_%H%M%S')):
        self.project.set_save_path(save_path, datetime_str)
        self.config["user_save"]["datetime"] = datetime_str
        self.config["user_save"]["path"] = save_path

    @debug.log
    def set_last_autosave_path_(self, save_path, datetime_str=datetime.now().strftime('%Y-%m-%d_%H%M%S')):
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
        companies = list()
        with open("resources/companies.csv", encoding='utf8') as f:
            line = f.readline().strip("\n")
            line = f.readline().strip("\n")
            args = line.split(";")
            while line:
                companies.append(corp.Company(*args))
                line = f.readline().strip("\n")
                args = line.split(";")
        return companies

    @debug.log
    def get_init_trades(self):
        trades = list()
        with open("resources/trades.csv", encoding='utf8') as f:
            line = f.readline().strip("\n")
            line = f.readline().strip("\n")
            args = line.split(";")
            while line:
                name = args[0]
                cost_group = [cost_group for cost_group in self.project.cost_groups if str(cost_group.id) == args[1]][0]
                budget = args[2]
                comment = args[3]
                trades.append(arch.Trade(name=name, cost_group=cost_group, budget=budget, comment=comment))
                line = f.readline().strip("\n")
                args = line.split(";")
        return trades

    @debug.log
    def get_init_cost_groups(self):
        cost_groups = list()
        with open("resources/cost_groups.csv", encoding='utf8') as f:
            line = f.readline().strip("\n")
            line = f.readline().strip("\n")
            args = line.split(";")
            while line:
                id = args[0]
                name = args[1]
                description = args[2]
                cost_groups.append(arch.CostGroup(id=id, name=name, description=description))
                line = f.readline().strip("\n")
                args = line.split(";")
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
        "user_save": {
            "datetime": None,
            "path": None
        },
        "last_auto_save": {
            "datetime": None,
            "path": None
        },
        "autosave_time": 80000,
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
        }
        return default_config
