"""
#
#   PROJ
#   This is a module containing the Project-class which contains all information important to projects.
#
"""
import debug

from datetime import datetime
from PyQt5.QtCore import QDate

from core.obj import corp, arch, proj
from core.obj import IdObject
from core.obj import restore


class Project(IdObject):
    """Represents an architecture project.

    Contains all relevant variables of a project. It contains a config,
    some basic metadata, the project status, a ProjectData object containing advanced
    metadata and lists of the following obects:
    arch.ArchJob
    corp.Invoice
    Corp.Company
    arch.Trade
    arch.CostGroup
    ProjectCostCalculation
    """

    def __init__(
        self,
        identifier,
        *,
        config=None,
        uid=None,
        deleted=False,
        construction_scheme="",
        address=None,
        client=None,
        project_data=None,
        project_cost_calculations=None,
        companies=None,
        trades=None,
        cost_groups=None,
        invoices=None,
        jobs=None,
        commissioned_date=None,
        planning_finished_date=None,
        billed_date=None,
        planning_status=None,
        address_uid=None,
    ):
        super().__init__(self, uid=uid, deleted=deleted)

        #   Config (dict)
        #   Is passed at initialization from the API (api.py) and contains the following information:
        #       currency, default_vat, save_dir, autosave_subdir, template_subdir, user_save_datetime,
        #       user_save (dict: dateime, path), last_autosave (dict: datetime, path),
        #       window_size (dict: width, height), building_classes (list), planning_phases (list of tuples)
        self.config = config

        #   Basic metadata
        self.identifier = identifier
        self.construction_scheme = construction_scheme
        self._address = address
        self._client = client
        #   Project status
        self.commissioned_date = commissioned_date
        self.planning_finished_date = planning_finished_date
        self.billed_date = billed_date
        self.planning_status = planning_status

        #   ProjectData (obj.proj.ProjectData)
        #       Object containing more detailed project data like usable floor space.
        #       For more informations look at obj.proj.ProjectData.
        self._project_data = project_data

        """
        #   Invoices, Jobs
        #       Initialized empty and accumulated during the project.
        """
        self._jobs = jobs if jobs is not None else list()
        self._invoices = invoices if invoices is not None else list()
        self.sort_invoices()
        #   sort_invoices():
        #       Invoices must always be sorted by date (oldest first)
        #       because the way the previous invoices are calculated.
        #       In most cases of appending invoices, the sorting is automatically
        #       taken care of via the "setter" self.add_invoice(...).
        """
        #   Companies, Trades and CostGroups
        #       These lists are initialized with the default lists and can be
        #       extended in a project. The initialization takes place in the AppData container.
        """
        self._companies = companies if companies is not None else list()
        self._trades = trades if trades is not None else list()
        self._cost_groups = cost_groups if cost_groups is not None else list()
        #   ProjectCostCalculations
        #       TODO: descr
        #       TODO: descr
        self._project_cost_calculations = (
            project_cost_calculations
            if project_cost_calculations is not None
            else list()
        )

    """
    #
    #   Properties
    #       GETTER, SETTER and also GETTER of sub-properties
    #
    """

    @property
    def address(self):
        """Return the address of the project."""
        return self._address

    @address.setter
    def address(self, address):
        if isinstance(address, corp.Address):
            self._address = address
        else:
            raise TypeError("address is not an corp.Address type.")

    @property
    def client(self):
        """Return the client of the project."""
        return self._client

    @client.setter
    def client(self, client):
        if isinstance(client, corp.Person):
            self._client = client
        else:
            raise TypeError("client is not an corp.Person type.")

    @property
    def project_data(self):
        """Return the advanced metadata of the project."""
        return self._project_data

    @project_data.setter
    def project_data(self, project_data):
        if isinstance(project_data, proj.ProjectData):
            self._project_data = project_data
        else:
            raise TypeError("project is not an proj.ProjectData type.")

    """ properties
    #
    #   ProjectCostCalculations
    #
    """

    @property
    def project_cost_calculations(self):
        """Return the non-deleted ProjectCostCalculations of the project."""
        return [pcc for pcc in self._project_cost_calculations if pcc.is_not_deleted()]

    @project_cost_calculations.setter
    def project_cost_calculations(self, project_cost_calculations):
        if not (self._project_cost_calculations):
            self._project_cost_calculations = project_cost_calculations
        else:
            raise Exception("Existing list of project_cost_calculations is non-empty.")

    def get_deleted_project_cost_calculations(self):
        """Return the deleted ProjectCostCalculations of the project."""
        return [pcc for pcc in self._project_cost_calculations if pcc.is_deleted()]

    """ properties
    #
    #   Companies
    #
    """

    @property
    def companies(self):
        """Return the non-deleted Companies of the project."""
        return [company for company in self._companies if company.is_not_deleted()]

    @companies.setter
    def companies(self, companies):
        if not (self._companies):
            self._companies = companies
        else:
            raise Exception("Existing list of companies is non-empty.")

    def get_deleted_companies(self):
        """Return the deleted Companies of the project."""
        return [company for company in self._companies if company.is_deleted()]

    def get_companies_of_person(self, person):
        """Return the non-deleted Companies having a given person as contact person."""
        return [
            company for company in self.companies if company.contact_person is person
        ]

    """ properties
    #
    #   Trades
    #
    """

    @property
    def trades(self):
        """Return the non-deleted Trades of the project."""
        return [trade for trade in self._trades if trade.is_not_deleted()]

    @trades.setter
    def trades(self, trades):
        if not (self._trades):
            self._trades = trades
        else:
            raise Exception("Existing list of trades is non-empty.")

    def get_deleted_trades(self):
        """Return the deleted Trades of the project."""
        return [trade for trade in self._trades if trade.is_deleted()]

    def get_trade_budgets_total(self):
        """Return tne sum of the budgets of all Trades of the project."""
        return sum(trade.budget for trade in self.trades)

    """ properties
    #
    #   Cost Groups
    #
    """

    @property
    def cost_groups(self):
        cost_groups = [
            cost_group
            for cost_group in self._cost_groups
            if cost_group.is_not_deleted()
        ]
        cost_groups.sort(key=lambda cost_group: cost_group.id)
        return cost_groups

    @cost_groups.setter
    def cost_groups(self, cost_groups):
        if not (self._cost_groups):
            self._cost_groups = cost_groups
        else:
            raise Exception("Existing list of cost_groups is non-empty.")

    def get_deleted_cost_groups(self):
        return [
            cost_group for cost_group in self._cost_groups if cost_group.is_deleted()
        ]

    @property
    def main_cost_groups(self):
        return [
            cost_group
            for cost_group in self._cost_groups
            if cost_group.is_main_group() and cost_group.is_not_deleted()
        ]

    def get_sub_cost_groups(self, cost_group):
        return [
            child for child in self.cost_groups if child.is_sub_group_of(cost_group)
        ]

    def get_budget_sub_cost_groups(self, cost_group):
        return sum(
            cost_group.budget for cost_group in self.get_sub_cost_groups(cost_group)
        )

    def get_cost_group_budget_total(self):
        return sum(cost_group.budget for cost_group in self.cost_groups)

    """ properties
    #
    #   Invoices
    #
    """

    @property
    def invoices(self):
        return [invoice for invoice in self._invoices if invoice.is_not_deleted()]

    @invoices.setter
    def invoices(self, invoices):
        if not (self._invoices):
            self._invoices = invoices
            self.sort_invoices()
        else:
            raise Exception("Existing list of invoices is non-empty.")

    def get_deleted_invoices(self):
        return [invoice for invoice in self._invoices if invoice.is_deleted()]

    def get_invoices_of_job(self, job):
        return [invoice for invoice in self.invoices if invoice.job is job]

    def get_invoices_of_company(self, company):
        return [invoice for invoice in self.invoices if invoice.company is company]

    def get_invoices_of_trade(self, trade):
        return [invoice for invoice in self.invoices if invoice.trade is trade]

    def get_invoices_of_cost_group(self, cost_group):
        return [
            invoice
            for invoice in self.invoices
            if invoice.cost_group and invoice.cost_group.is_sub_group_of(cost_group)
        ]

    def get_approved_amounts_of_trade(self, trade):
        return sum(
            invoice.approved_amount
            for invoice in self.invoices
            if invoice.trade is trade
        )

    def get_approved_amounts_of_sub_cost_groups(self, cost_group):
        return sum(
            invoice.approved_amount
            for invoice in self.invoices
            if invoice.cost_group and invoice.cost_group.is_sub_group_of(cost_group)
        )

    def get_approved_amounts_total(self):
        return sum(invoice.approved_amount for invoice in self.invoices)

    """ properties
    #
    #   Jobs
    #
    """

    @property
    def jobs(self):
        return [job for job in self._jobs if job.is_not_deleted()]

    @jobs.setter
    def jobs(self, jobs):
        if not (self._jobs):
            self._jobs = jobs
        else:
            raise Exception("Existing jobs of companies is non-empty.")

    def get_deleted_jobs(self):
        return [job for job in self._jobs if job.is_deleted()]

    def get_job(self, company, id):
        return [job for job in self.jobs if job.company is company and job.id == id][0]

    def get_jobs_of_company(self, company):
        return [job for job in self.jobs if job.company is company]

    def get_jobs_of_trade(self, trade):
        return [
            job
            for job in self.jobs
            if isinstance(job, arch.ArchJob) and job.trade is trade
        ]

    def get_jobs_of_cost_group(self, cost_group):
        return [
            job
            for job in self.jobs
            if isinstance(job, arch.ArchJob) and job.cost_group is cost_group
        ]

    def get_jobs_of_sub_cost_groups(self, cost_group):
        return [
            job
            for job in self.jobs
            if isinstance(job, arch.ArchJob)
            and job.cost_group
            and job.cost_group.is_sub_group_of(cost_group)
        ]

    def get_max_job_number(self, company):
        return max([job.id for job in self.jobs if job.company is company] + [0])

    def get_job_sums_of_trade(self, trade):
        return sum([job.job_sum_w_additions for job in self.get_jobs_of_trade(trade)])

    def get_job_sums_of_cost_group(self, cost_group):
        return sum(
            [job.job_sum_w_additions for job in self.get_jobs_of_cost_group(cost_group)]
        )

    def get_job_sums_of_sub_cost_groups(self, cost_group):
        return sum(
            [
                job.job_sum_w_additions
                for job in self.get_jobs_of_sub_cost_groups(cost_group)
            ]
        )

    def get_job_sums_total(self):
        return sum(job.job_sum_w_additions for job in self.jobs)

    def get_psds_of_trade(self, trade):
        return sum(
            [job.paid_safety_deposits_sum for job in self.get_jobs_of_trade(trade)]
        )

    def get_psds_of_cost_group(self, cost_group):
        return sum(
            job.paid_safety_deposits_sum
            for job in self.get_jobs_of_cost_group(cost_group)
        )

    def get_psds_of_sub_cost_groups(self, cost_group):
        return sum(
            job.paid_safety_deposits_sum
            for job in self.get_jobs_of_sub_cost_groups(cost_group)
        )

    def get_psds_total(self):
        return sum(job.paid_safety_deposits_sum for job in self.jobs)

    """ properties
    #
    #   People
    #
    """

    @property
    def people(self):
        client = [self.client] if self.client else list()
        people = client + [
            company.contact_person
            for company in self.companies
            if company.contact_person
        ]
        return [person for person in people if person.is_not_deleted()]

    def get_deleted_people(self):
        client = [self.client] if self.client else list()
        people = client + [
            company.contact_person
            for company in self.companies
            if company.contact_person
        ]
        return [person for person in people if person.is_deleted()]

    """ properties
    #
    #   Addresses
    #
    """

    @property
    def addresses(self):
        return self._addresses

    @addresses.setter
    def addresses(self, addresses):
        if not (self._addresses):
            self._addresses = addresses
        else:
            raise Exception("Existing list of people is non-empty.")

    """ properties
    #
    #    Config
    #
    """
    """
    #   Currency
    """

    @debug.log
    def get_currency(self):
        return self.config["currency"]

    """
    #   VAT
    """

    @debug.log
    def get_vat(self):
        return self.config["default_vat"]

    """
    #   Save Path / Time
    """

    @debug.log
    def get_usersave_path(self):
        return Path(self.config["user_save"]["path"])

    @debug.log
    def get_usersave_datetime(self):
        return self.config["user_save"]["datetime"]

    #   Set the save path in the project config.
    #       This gets called from the api upon saving.
    @debug.log
    def set_save_path(self, save_path, datetime=datetime.now()):
        self.config["user_save"]["datetime"] = datetime
        self.config["user_save"]["path"] = str(save_path)

    """
    #   Autosave Path / Time
    """

    @debug.log
    def get_autosave_path(self):
        return Path(self.config["last_auto_save"]["path"])

    @debug.log
    def get_autosave_datetime(self):
        return self.config["last_auto_save"]["datetime"]

    #   Set the autosave path in the project config.
    #       This gets called from the api upon autosaving.
    @debug.log
    def set_autosave_path(self, save_path, datetime=datetime.now()):
        self.config["last_auto_save"]["datetime"] = datetime
        self.config["last_auto_save"]["path"] = str(save_path)

    """
    #
    #   Functionality
    #       Functions helping with handling the project like
    #       adding or removing an invoice or person.
    #
    """
    """ func
    #
    #   ProjectCostCalculation
    #
    """

    @debug.log
    def input_new_pcc(self, input_pcc_args):
        new_pcc = ProjectCostCalculation(**input_pcc_args)
        self.add_pcc(new_pcc)
        return new_pcc

    @debug.log
    def add_pcc(self, pcc):
        if isinstance(pcc, ProjectCostCalculation):
            self._project_cost_calculations.append(pcc)
        else:
            raise TypeError("pcc is not an ProjectCostCalculation type.")

    @debug.log
    def delete_pcc(self, pcc):
        pcc.delete()
        # TODO: What happens with linked objects?
        return pcc

    """
    #   APPLY BUDGETS
    #   After calculating the costs, apply these as budgets
    """

    @debug.log
    def apply_budgets(self, pcc):
        self.apply_cost_group_budgets(pcc)
        self.apply_trade_budgets(pcc)

    @debug.log
    def apply_cost_group_budgets(self, pcc):
        for cost_group in self.cost_groups:
            self.apply_cost_group_budget(pcc, cost_group)

    @debug.log
    def apply_trade_budgets(self, pcc):
        for trade in self.trades:
            self.apply_trade_budget(pcc, trade)

    @debug.log
    def apply_cost_group_budget(self, pcc, cost_group):
        cost_group.budget = pcc.get_cost_group_prognosis(cost_group)

    @debug.log
    def apply_trade_budget(self, pcc, trade):
        trade.budget = pcc.get_trade_prognosis(trade)

    """ func
    #
    #   Jobs
    #
    """

    @debug.log
    def input_new_job(self, input_job_args):
        new_job = arch.ArchJob(**input_job_args)
        self.add_job(new_job)
        return new_job

    @debug.log
    def add_job(self, job):
        if isinstance(job, corp.Job):
            self._jobs.append(job)
        else:
            raise TypeError("job is not an corp.Job type.")

    @debug.log
    def delete_job(self, job):
        job.delete()
        # TODO: What happens with linked objects?
        return job

    def job_exists(self, id, company):
        exists = [job for job in self.jobs if job.id == id and job.company is company]
        if exists:
            return True
        return False

    """ func
    #
    #   Invoices
    #
    """

    @debug.log
    def input_new_invoice(self, invoice_args):
        new_invoice = corp.Invoice(**invoice_args)
        self.add_invoice(new_invoice)
        return new_invoice

    @debug.log
    def add_invoice(self, invoice):
        if isinstance(invoice, corp.Invoice):
            self._invoices.append(invoice)
            self.update_all_prev_invoices()
        else:
            raise TypeError("invoice is not an corp.Invoice type.")

    @debug.log
    def update_invoice(self, invoice, invoice_args):
        invoice.update(**invoice_args)
        self.update_all_prev_invoices()
        return invoice

    @debug.log
    def delete_invoice(self, invoice):
        invoice.delete()
        self.update_all_prev_invoices()
        return invoice

    @debug.log
    def sort_invoices(self):
        self.invoices.sort(key=lambda invoice: invoice.invoice_date, reverse=True)

    @debug.log
    def update_all_prev_invoices(self):
        # sort_invoices needed here, because we dont know if an invoice was edited
        self.sort_invoices()
        for invoice in self.invoices:
            prev_invoices = self.get_prev_invoices(invoice=invoice)
            invoice.prev_invoices = prev_invoices
            invoice.update_prev_invoices_amount()

    """
    #
    #   get_prev_invoices
    #       Get the previous invoices based on either an invoice, or the info
    #       of company, job, date and (for same date invoices) date of the creation
    #       The invoices MUST be sorted reversely by date (see: sort_invoices()).
    #       For perfomance's sake, the invoices are not sorted everytime, but only
    #       at the points, after the invoices-list got edited.
    #
    """

    @debug.log
    def get_prev_invoices(
        self,
        *,
        invoice=None,
        invoice_uid=None,
        company=None,
        job=None,
        invoice_date=None,
        invoice_created_date=None,
        cumulative=True,
    ):
        prev_invoices = list()
        if cumulative:
            invoices = [invoice for invoice in self.invoices if invoice.cumulative]
            if isinstance(invoice, corp.Invoice):
                invoice_uid = invoice.uid
                company = invoice.company
                job = invoice.job
                invoice_date = invoice.invoice_date
                invoice_created_date = invoice.uid.created_date
            if [company, job, invoice_date, invoice_created_date]:
                """company and job have to be the same"""
                prev_invoices_company_job = [
                    prev_invoice
                    for prev_invoice in invoices
                    if prev_invoice.uid is not invoice_uid
                    and prev_invoice.company is company
                    and prev_invoice.job is job
                ]
                """ invoice date must be earlier or IF same date, date_created must be earlier """
                prev_invoices = [
                    prev_invoice
                    for prev_invoice in prev_invoices_company_job
                    if prev_invoice.invoice_date.toJulianDay()
                    < invoice_date.toJulianDay()
                    or (
                        prev_invoice.invoice_date.toJulianDay()
                        == invoice_date.toJulianDay()
                        and prev_invoice.uid.created_date < invoice_created_date
                    )
                ]
        return prev_invoices

    """ func
    #
    #   Companies
    #
    """

    @debug.log
    def input_new_company(self, company_args):
        new_company = corp.Company(**company_args)
        self.add_company(new_company)
        return new_company

    @debug.log
    def add_company(self, company):
        if isinstance(company, corp.Company):
            self._companies.append(company)
        else:
            raise TypeError("job is not an corp.Company type.")

    @debug.log
    def delete_company(self, company):
        company.delete()
        if company.contact_person:
            company.contact_person.delete()
        return company

    """ func
    #
    #   Trades
    #
    """

    @debug.log
    def input_new_trade(self, trade_args):
        new_trade = arch.Trade(**trade_args)
        self.add_trade(new_trade)
        return new_trade

    @debug.log
    def add_trade(self, trade):
        if isinstance(trade, arch.Trade):
            self._trades.append(trade)
        else:
            raise TypeError("trade is not an arch.Trade type.")

    @debug.log
    def delete_trade(self, trade):
        trade.delete()
        # TODO: What happens with linked objects?
        return trade

    """ func
    #
    #   CostGroups
    #
    """

    @debug.log
    def input_new_cost_group(self, cost_group_args):
        new_cost_group = arch.CostGroup(**cost_group_args)
        self.add_cost_group(new_cost_group)
        return new_cost_group

    @debug.log
    def add_cost_group(self, cost_group):
        if isinstance(cost_group, arch.CostGroup):
            self._cost_groups.append(cost_group)
        else:
            raise TypeError("cost_group is not an arch.CostGroup type.")

    @debug.log
    def delete_cost_group(self, cost_group):
        cost_group.delete()
        cost_group_children = [
            cg_child
            for cg_child in self.cost_groups
            if cg_child.is_sub_group_of(cost_group)
        ]
        for cg_child in cost_group_children:
            cg_child.delete()
        return cost_group

    @debug.log
    def get_cost_groups_of_level(self, level):
        return [
            cost_group
            for cost_group in self.cost_groups
            if cost_group.get_tree_level() == level
        ]

    """
    #
    #   set_cost_group_budget
    #       Set the budget of the sum of budgets of the subgroups
    #
    """

    @debug.log
    def set_cost_group_budget(self, cost_group):
        cost_group.budget = self.get_cost_group_budget(cost_group)

    @debug.log
    def get_cost_group_budget(self, cost_group):
        budget_sum = sum(
            cg.budget for cg in self.cost_groups if cg.is_sub_group_of(cost_group)
        )
        return budget_sum

    """ func
    #
    #   People
    #
    """

    @debug.log
    def input_new_person(self, person_args):
        #   input_new_person, the function name is deceiving,
        #   and originates from a different data structure, which was changed,
        #   since only companies contain an attribute with people. We are now
        #   generating the project.people list from the company list and
        #   hence we dont need to append the person object to a people list.
        new_person = corp.Person(**person_args)
        return new_person

    @debug.log
    def delete_person(self, person):
        person.delete()
        if person.company and person.company.contact_person is person:
            person.company.contact_person = None
        return person

    @debug.log
    def update(
        self,
        identifier,
        *,
        construction_scheme="",
        address=None,
        client=None,
        project_data=None,
        commissioned_date=None,
        planning_finished_date=None,
        billed_date=None,
        planning_status=None,
        **kwargs,
    ):
        """Update instance variables."""
        self.identifier = identifier
        self.construction_scheme = construction_scheme
        self.address = address
        self._client = client
        self.project_data = project_data

        """ project status """
        self.commissioned_date = commissioned_date
        self.planning_finished_date = planning_finished_date
        self.billed_date = billed_date
        self.planning_status = planning_status

        self.edited()

    @debug.log
    def restore(self):
        """Restore pointers from UID.

        Function that help to reconstruct the data-structure after loading.
        When loading, we can restore pointers by UID, since they were all
        created in the same project and hence the UIDs are known. If that
        is not the case, use restore_after_import().
        """
        self.restore_people()
        self.restore_cost_groups()
        self.restore_project_cost_calculations()
        self.restore_trades()
        self.restore_companies()
        self.restore_jobs()
        self.restore_invoices()
        self.update_all_prev_invoices()

    @debug.log
    def restore_after_import(self):
        """Restore pointers from name/id/... .

        Function that help to reconstruct the data-structure after import.
        When importing, we don't know the UID and have to use other attributes,
        like name, id, etc. to restore the links.
        If UID is known, use restore().
        """
        self.restore_after_import_people()
        self.restore_after_import_cost_groups()
        self.restore_after_import_project_cost_calculations()
        self.restore_after_import_trades()
        self.restore_after_import_companies()
        self.restore_after_import_jobs()
        self.restore_after_import_invoices()
        self.update_all_prev_invoices()

    """
    #   AFTER LOADING
    """

    def restore_project_cost_calculations(self):
        for pcc in self.project_cost_calculations:
            pcc.restore(self)

    def restore_people(self):
        for person in self.people:
            person.restore(self)

    def restore_companies(self):
        for company in self.companies:
            company.restore(self)

    def restore_jobs(self):
        for job in self.jobs:
            job.restore(self)

    def restore_invoices(self):
        for invoice in self.invoices:
            invoice.restore(self)

    def restore_trades(self):
        for trade in self.trades:
            trade.restore(self)

    def restore_cost_groups(self):
        for cost_group in self.cost_groups:
            cost_group.restore(self)

    """
    #   AFTER IMPORT
    """

    def restore_after_import_project_cost_calculations(self):
        for pcc in self.project_cost_calculations:
            pcc.restore_after_import(self)

    def restore_after_import_people(self):
        for person in self.people:
            person.restore_after_import(self)

    def restore_after_import_companies(self):
        for company in self.companies:
            company.restore_after_import(self)

    def restore_after_import_jobs(self):
        for job in self.jobs:
            job.restore_after_import(self)

    def restore_after_import_invoices(self):
        for invoice in self.invoices:
            invoice.restore_after_import(self)

    def restore_after_import_trades(self):
        for trade in self.trades:
            trade.restore_after_import(self)

    def restore_after_import_cost_groups(self):
        for cost_group in self.cost_groups:
            cost_group.restore_after_import(self)

    """
    #
    #   Utility
    #
    #
    """

    def has_been_saved(self):
        return True if self.config["user_save"]["path"] else False


class ProjectData(IdObject):
    """Encapsulates the advanced project data.

    This Object contains all hardfacts of a project, i.e. its
    property size or the building class.
    """

    def __init__(
        self,
        commissioned_services=None,
        property_size=0,
        usable_floor_space_nuf=0,
        usable_floor_space_bgf=0,
        rental_space=0,
        building_class=None,
        construction_costs_kg300_400=0,
        production_costs=0,
        contract_fee=0,
        execution_period=None,
        *,
        uid=None,
        deleted=False,
    ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.commissioned_services = commissioned_services
        self.property_size = property_size
        self.usable_floor_space_nuf = usable_floor_space_nuf
        self.usable_floor_space_bgf = usable_floor_space_bgf
        self.rental_space = rental_space
        self.building_class = building_class
        self.construction_costs_kg300_400 = construction_costs_kg300_400
        self.production_costs = production_costs
        self.contract_fee = contract_fee
        self.execution_period = execution_period


class ProjectCostCalculation(IdObject):
    """Represents a cost calculation.

    A project costcalculation is mainly a list
    of objects (dicts), which represent some
    item or service and they belong to a CostGroup
    and/or Trade, with cost per unit and units.
    Then we can make a pre-calculation of the project
    costs. During a project, these calculation can
    be updated and the Trade/CostGroup budgets
    updated w.r.t. this.
    """

    PCC_TYPES = [
        "Kostenrahmen (LP1)",
        "Kostenschätzung (LP2)",
        "Kostenberechnung (LP3)",
        "Kostenvoranschlag (LP4->LP5)",
        "Kostenanschlag (LP6, LP7, LP8)",
    ]

    def __init__(self, name, type, uid=None, deleted=False, date=None, inventory=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
        self.type = type
        self.date = date
        self._inventory = inventory if inventory else list()

    """
    #
    #   PROPERTIES
    #
    #
    """

    @property
    def inventory(self):
        return [item for item in self._inventory if item.is_not_deleted()]

    def add_inventory_item(self, inventory_item):
        self._inventory.append(inventory_item)

    def delete_inventory_item(self, inventory_item):
        inventory_item.delete()

    @property
    def total_cost(self):
        return sum(item.total_price for item in self.inventory if item.is_active)

    """
    #
    #   Cost Prognosis
    #       Make a prognosis of the costs of a project via the inventory
    #
    """

    def get_sub_cost_groups_prognosis(self, cost_group, cost_groups):
        """Get the sum of the prognosises of strict subgroups of a given cost group.

        Since the 100,200,... cost groups also have their own budgets,
        the actual budget for the X00 cost group is the sum of the X00
        cost group plus the sum of all cost group that are below in the
        tree i.e., X00 is their parent or their parents parent
        """
        cost_group_sum = sum(
            self.get_cost_group_prognosis(sub_cost_group)
            for sub_cost_group in cost_groups
            if sub_cost_group.is_sub_group_of(cost_group)
        )
        return cost_group_sum

    def get_cost_group_prognosis(self, cost_group):
        """Get the cost prognosis of a cost group."""
        cost_group_sum = sum(self.get_cost_group_items(cost_group))
        return cost_group_sum

    def get_trade_prognosis(self, trade):
        trade_sum = sum(self.get_trade_items(trade))
        return trade_sum

    def get_cost_group_trade_prognosis(self, cost_group, trade):
        trade_sum = sum(self.get_cost_group_trade_items(cost_group, trade))
        return trade_sum

    """
    #
    #   Items
    #       Get items of trade/cost_group
    #
    """

    def get_cost_group_items(self, cost_group):
        cost_group_items = [
            item.total_price
            for item in self.inventory
            if item.is_active and item.cost_group is cost_group
        ]
        return cost_group_items

    def get_trade_items(self, trade):
        trade_items = [
            item.total_price
            for item in self.inventory
            if item.is_active and item.trade is trade
        ]
        return trade_items

    def get_cost_group_trade_items(self, cost_group, trade):
        trade_items = [
            item.total_price
            for item in self.inventory
            if item.is_active and item.cost_group is cost_group and item.trade is trade
        ]
        return trade_items

    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the cost_group
    #
    """

    @debug.log
    def update(self, name, type, date, inventory):
        self.name = name
        self.type = type
        self.date = date
        self._inventory = inventory
        """ set edited date """
        self.edited()

    """
    #
    #   RESTORE
    #   Fuctions to restore pointers
    #
    """

    @debug.log
    def restore(self, project):
        self.restore_items(project)

    def restore_items(self, project):
        for item in self._inventory:
            item.restore(project)

    """
    #
    #   __FUNCTIONS__
    #
    #
    """

    def __copy__(self, copy_index=0):
        new_inventory = list()
        for item in self.inventory:
            new_item = InventoryItem(
                name=item.name,
                description=item.description,
                unit_price=item.unit_price,
                units=item.units,
                unit_type=item.unit_type,
                is_active=item.is_active,
                cost_group=item.cost_group,
                cost_group_ref=item._cost_group_ref,
                trade=item.trade,
                trade_ref=item._trade_ref,
            )
            new_inventory.append(new_item)
            name = f"{self.name} copy{' '+copy_index if copy_index>0 else ''}"
        new_pcc = ProjectCostCalculation(
            name=name, type=self.type, date=QDate.currentDate(), inventory=new_inventory
        )
        return new_pcc


class InventoryItem(IdObject):

    DEFAULT_UNIT_TYPES = ["m", "m²", "m³", "kg", "h", "Tag", "Wo.", "Stk.", "Psch."]

    """docstring for InventoryItem"""

    def __init__(
        self,
        name="",
        *args,
        ordinal_number="",
        description="",
        unit_price=0,
        units=0,
        unit_type="",
        is_active=True,
        cost_group=None,
        cost_group_ref=None,
        trade=None,
        trade_ref=None,
        uid=None,
        deleted=False,
        **kwargs,
    ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
        self.ordinal_number = ordinal_number
        self.description = description
        self.unit_price = unit_price
        self.units = units
        self.unit_type = unit_type
        #   is_active
        #       count the item in the calculation only if True
        self.is_active = is_active
        self.cost_group = cost_group
        self.trade = trade

        """ for restoration only """
        self._cost_group_ref = cost_group_ref
        self._trade_ref = trade_ref

    """
    #
    #   PROPERTIES
    #
    #
    """

    @property
    def total_price(self):
        return self.unit_price * self.units

    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the cost_group
    #
    """

    @debug.log
    def update(
        self,
        name,
        ordinal_number,
        description,
        unit_price,
        units,
        unit_type,
        is_active,
        cost_group,
        trade,
    ):
        self.name = name
        self.ordinal_number = ordinal_number
        self.description = description
        self.unit_price = unit_price
        self.units = units
        self.unit_type = unit_type
        #   is_active
        #       count the item in the calculation only if True
        self.is_active = is_active
        self.cost_group = cost_group
        self.trade = trade
        """ set edited date """
        self.edited()

    """
    #
    #   RESTORE
    #   Fuctions to restore pointers
    #
    """

    @debug.log
    def restore(self, project):
        self.cost_group = restore.restore_by(
            self.cost_group, self._cost_group_ref, project.cost_groups
        )
        self.trade = restore.restore_by(self.trade, self._trade_ref, project.trades)

    """
    #
    #   __FUNCTIONS__
    #
    #
    """

    def __copy__(self):
        args = vars(self).copy()
        args["name"] = args["name"] + " copy"
        new_item = InventoryItem(**args)
        return new_item
