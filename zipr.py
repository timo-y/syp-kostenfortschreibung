"""
#
#   ZIPR
#   Modified version of the zip-creation class from https://bbengfort.github.io/
#   used to save and load multiple files from one zip-file.
#
"""
import debug

import os
import json
import zipfile
import encoder, decoder

class Zipr(object):

    def __enter__(self):
        # Makes this thing a context manager
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Makes this thing a context manager
        self.close()

    def close(self):
        self.zobj.close()

class ZipArchive(Zipr):

    def __init__(self, path, mode="r"):
        self.zobj = zipfile.ZipFile(
            path, mode, compression=zipfile.ZIP_STORED,
            allowZip64=True, compresslevel=None
        )
        self.root, _ = os.path.splitext(os.path.basename(path))

    def open(self, path, mode='r'):
        # Write into a directory instead of the root of the zip file
        path = os.path.join(self.root, path)
        return ZipArchiveFile(self.zobj.open(path, mode))

class ZipArchiveFile(Zipr):

    def __init__(self, zobj, encoding="utf-8"):
        self.zobj = zobj
        self.encoding = encoding

    def write(self, data):
        if isinstance(data, str):
            data = data.encode(self.encoding)
        self.zobj.write(data)

@debug.log
def save_project(path, app_data):
    """Save a project to a *.project file.

    Args:
        path (Path): Path to save to
        app_data (api.AppData): Application data containing the project data
    """
    # Less annoying make archive with workaround classes
    with ZipArchive(path, "w") as z:

        # project config
        with z.open("proj_config.json", "w") as file:
            data = app_data.project.config
            json.dump(data, file, indent=4)

        # project info
        with z.open("project.json", "w") as file:
            data = app_data.project
            json.dump(data, file, cls=encoder.ProjectEncoder, indent=4)

        # project cost calculations
        with z.open("project_cost_calculations.json", "w") as file:
            data = app_data.project.project_cost_calculations
            json.dump(data, file, cls=encoder.ProjectCostCalculationEncoder, indent=4)

        # companies
        with z.open("companies.json", "w") as file:
            data = app_data.project.companies
            json.dump(data, file, cls=encoder.CompanyEncoder, indent=4)

        # trades
        with z.open("trades.json", "w") as file:
            data = app_data.project.trades
            json.dump(data, file, cls=encoder.TradeEncoder, indent=4)

        # invoices
        with z.open("invoices.json", "w") as file:
            data = app_data.project._invoices
            json.dump(data, file, cls=encoder.InvoiceEncoder, indent=4)

        # jobs
        with z.open("jobs.json", "w") as file:
            data = app_data.project.jobs
            json.dump(data, file, cls=encoder.ArchJobEncoder, indent=4)

        # cost groups
        with z.open("cost_groups.json", "w") as file:
            data = app_data.project.cost_groups
            json.dump(data, file, cls=encoder.CostGroupEncoder, indent=4)


@debug.log
def open_project(path):
    """Open a *.project file.

    Args:
        path (Path): Path to saved project

    Returns:
        dict: Project as a dict
    """
    loaded_args = dict()
    with zipfile.ZipFile(path, "r") as z:

        root, _ = os.path.splitext(os.path.basename(path))

        # project config
        with z.open(root+"/proj_config.json", "r") as file:
            loaded_args["project_config"] = json.load(file)

        # project
        with z.open(root+"/project.json", "r") as file:
            loaded_args["project"] = json.load(file, object_hook=decoder.ProjectDecoder().object_hook)

        # cost groups
        with z.open(root+"/project_cost_calculations.json", "r") as file:
            loaded_args["project_cost_calculations"] = json.load(file, object_hook=decoder.ProjectCostCalculationDecoder().object_hook)

        # companies
        with z.open(root+"/companies.json", "r") as file:
            loaded_args["companies"] = json.load(file, object_hook=decoder.CompanyDecoder().object_hook)

        # trades
        with z.open(root+"/trades.json", "r") as file:
            loaded_args["trades"] = json.load(file, object_hook=decoder.TradeDecoder().object_hook)

        # invoices
        with z.open(root+"/invoices.json", "r") as file:
            loaded_args["invoices"] = json.load(file, object_hook=decoder.InvoiceDecoder().object_hook)

        # jobs
        with z.open(root+"/jobs.json", "r") as file:
            loaded_args["jobs"] = json.load(file, object_hook=decoder.ArchJobDecoder().object_hook)

        # cost groups
        with z.open(root+"/cost_groups.json", "r") as file:
            loaded_args["cost_groups"] = json.load(file, object_hook=decoder.CostGroupDecoder().object_hook)

    return loaded_args
