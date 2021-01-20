"""
#
#   PROJ
#   This is a module containing the Project-class which contains all information important to projects.
#
"""
import debug

from datetime import datetime
from PyQt5.QtCore import QDate

from core.obj import IdObject
from core.obj import corp, arch, proj

class Project(IdObject):

    def __init__(self, identifier, *, config=None, uid=None, deleted=False,  construction_scheme="", address=None, client=None,
                        project_data=None, project_cost_calculations=None, companies=None, trades=None, cost_groups=None,
                        invoices=None, jobs=None, people=None, commissioned_date=None, planning_finished_date = None,
                        billed_date=None, planning_status=None, address_uid=None, client_uid=None
                        ):
        super().__init__(self, uid=uid, deleted=deleted)

        #   Config (dict)
        #   Is passed at initialization from the API (api.py) and contains the following information:
        #       currency, default_vat, save_dir, autosave_subdir, template_subdir, user_save_datetime,
        #       user_save (dict: dateime, path), last_autosave (dict: datetime, path),
        #       window_size (dict: width, height), building_classes (list), planning_phases (list of tuples)
        self.config = config

        self.identifier = identifier
        self.construction_scheme = construction_scheme
        self._address = address
        self._client = client

        #   ProjectData (obj.proj.ProjectData)
        #       Object containing more detailed project data like usable floor space.
        #       For more informations look at obj.proj.ProjectData.
        self._project_data = project_data
        #   ProjectCostCalculations
        #       TODO: descr
        #       TODO: descr
        self._project_cost_calculations = project_cost_calculations if project_cost_calculations is not None else list()
        """
        #   Companies, Trades and COST_GROUPS
        #       These lists are initialized with the default lists and can be
        #       extended in a project.
        """
        self._companies = companies if companies is not None else list()
        self._trades = trades if trades is not None else list()
        self._cost_groups = cost_groups if cost_groups is not None else list()
        """
        #   Invoices, JOBS and PEOPLE
        #       Initialized empty and accumulated during the project.
        """
        self._invoices = invoices if invoices is not None else list()
        #   self.sort_invoices():
        #       Invoices must always be sorted by date (oldest first)
        #       because the way the previous invoices are calculated.
        #       In most cases of appending invoices, the sorting is automatically
        #       taken care of via the "setter" self.add_invoice(...).
        self.sort_invoices()
        self._jobs = jobs if jobs is not None else list()
        self._people = people if people is not None else list()


        #   Client
        #       At initialization, the client is created before the project in the dialog and needs to be
        #       added to the list of people of the project.
        if client:
            self._people.append(client)

        """ project status """
        self.commissioned_date = commissioned_date
        self.planning_finished_date = planning_finished_date
        self.billed_date = billed_date
        self.planning_status = planning_status

        """ for restoration only """
        self._client_uid = client_uid

    """
    #
    #   Properties
    #       GETTER, SETTER and also GETTER of sub-properties
    #
    """
    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, address):
        if isinstance(address, corp.Address):
            self._address = address
        else:
            raise TypeError("address is not an corp.Address type.")

    @property
    def client(self):
        return self._client
    @client.setter
    def client(self, client):
        if isinstance(client, corp.Person):
            self._client = client
        else:
            raise TypeError("client is not an corp.Person type.")

    @property
    def project_data(self):
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
        return [pcc for pcc in self._project_cost_calculations if pcc.is_not_deleted()]
    @project_cost_calculations.setter
    def project_cost_calculations(self, project_cost_calculations):
        if not(self._project_cost_calculations):
            self._project_cost_calculations = project_cost_calculations
        else:
            raise Exception("Existing list of project_cost_calculations is non-empty.")

    def get_deleted_project_cost_calculations(self):
        return [pcc for pcc in self._project_cost_calculations if pcc.is_deleted()]

    """ properties
    #
    #   Companies
    #
    """
    @property
    def companies(self):
        return [company for company in self._companies if company.is_not_deleted()]
    @companies.setter
    def companies(self, companies):
        if not(self._companies):
            self._companies = companies
        else:
            raise Exception("Existing list of companies is non-empty.")

    def get_deleted_companies(self):
        return [company for company in self._companies if company.is_deleted()]

    def get_companies_of_person(self, person):
        return [company for company in self.companies if company.contact_person is person]

    """ properties
    #
    #   Trades
    #
    """
    @property
    def trades(self):
        return [trade for trade in self._trades if trade.is_not_deleted()]
    @trades.setter
    def trades(self, trades):
        if not(self._trades):
            self._trades = trades
        else:
            raise Exception("Existing list of trades is non-empty.")

    def get_deleted_trades(self):
        return [trade for trade in self._trades if trade.is_deleted()]

    @property
    def cost_groups(self):
        return [cost_group for cost_group in self._cost_groups if cost_group.is_not_deleted()]
    @cost_groups.setter
    def cost_groups(self, cost_groups):
        if not(self._cost_groups):
            self._cost_groups = cost_groups
        else:
            raise Exception("Existing list of cost_groups is non-empty.")

    def get_deleted_cost_groups(self):
        return [cost_group for cost_group in self._cost_groups if cost_group.is_deleted()]

    @property
    def main_cost_groups(self):
        return [cost_group for cost_group in self._cost_groups if cost_group.is_main_group() and cost_group.is_not_deleted()]

    def get_children_of_cost_group(self, cost_group):
        return [child for child in self.cost_groups if child.is_sub_group_of(cost_group)]


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
        if not(self._invoices):
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
        if not(self._jobs):
            self._jobs = jobs
        else:
            raise Exception("Existing jobs of companies is non-empty.")

    def get_deleted_jobs(self):
        return [job for job in self._jobs if job.is_deleted()]

    def get_job(self, company, id):
        return [job for job in self.jobs if job.company is company and job.id == id][0]

    def get_jobs_of_company(self, company):
        return [job for job in self.jobs if job.company is company]

    def get_max_job_number(self, company):
        return max([job.id for job in self.jobs if job.company is company]+[0])

    """ properties
    #
    #   People
    #
    """
    @property
    def people(self):
        return [person for person in self._people if person.is_not_deleted()]
    @people.setter
    def people(self, people):
        if not(self._people):
            self._people = people
        else:
            raise Exception("Existing list of people is non-empty.")

    def get_deleted_people(self):
        return [person for person in self._people if person.is_deleted()]

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
        if not(self._addresses):
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
        return self.config["user_save"]["path"]

    @debug.log
    def get_usersave_datetime(self):
        return self.config["user_save"]["datetime"]

    #   Set the save path in the project config.
    #       This gets called from the api upon saving.
    @debug.log
    def set_save_path(self, save_path, datetime=datetime.now()):
        self.config["user_save"]["datetime"] = datetime
        self.config["user_save"]["path"] = save_path

    """
    #   Autosave Path / Time
    """
    @debug.log
    def get_autosave_path(self):
        return self.config["last_auto_save"]["path"]

    @debug.log
    def get_autosave_datetime(self):
        return self.config["last_auto_save"]["datetime"]

    #   Set the autosave path in the project config.
    #       This gets called from the api upon autosaving.
    @debug.log
    def set_autosave_path(self, save_path, datetime=datetime.now()):
        self.config["last_auto_save"]["datetime"] = datetime
        self.config["last_auto_save"]["path"] = save_path

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
        #TODO: What happens with linked objects?
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
            cost_group_children = self.get_children_of_cost_group(cost_group)
            cost_group.budget = sum(pcc.get_cost_group_prognosis(child) for child in cost_group_children) + pcc.get_cost_group_prognosis(cost_group)

    @debug.log
    def apply_trade_budgets(self, pcc):
        for trade in self.trades:
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
        #TODO: What happens with linked objects?
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
        self.invoices.sort(key=lambda invoice:invoice.invoice_date, reverse=True)

    @debug.log
    def update_all_prev_invoices(self):
        self.sort_invoices()
        for invoice in self.invoices:
            prev_invoices = self.get_prev_invoices(invoice=invoice)
            invoice.prev_invoices = prev_invoices
            invoice.update_prev_invoices_amount()

    @debug.log
    def get_prev_invoices(self, *, invoice=None, invoice_uid=None, company=None, job=None, invoice_date=None, invoice_created_date=None, cumulative=True):
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
                """ company and job have to be the same """
                prev_invoices_company_job = [prev_invoice for prev_invoice in invoices if prev_invoice.uid is not invoice_uid and prev_invoice.company is company and prev_invoice.job is job]
                """ invoice date must be earlier or IF same date, date_created must be earlier """
                prev_invoices = [prev_invoice for prev_invoice in prev_invoices_company_job if prev_invoice.invoice_date.toJulianDay() < invoice_date.toJulianDay() or (prev_invoice.invoice_date.toJulianDay() == invoice_date.toJulianDay() and prev_invoice.uid.created_date < invoice_created_date)]
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
        if new_company.contact_person:
            new_company.contact_person.company = new_company
            self.add_person(new_company.contact_person)
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
        #TODO: What happens with linked objects?
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
        #TODO: What happens with linked objects?
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
        #TODO: What happens with linked objects?
        return cost_group

    #   Check, if setting the parent to an existing
    #   cost_group is allowed (i.e. there is no recursion)
    @debug.log
    def cost_group_parent_allowed(self, cost_group, parent):
        if parent.parent:
            if parent.parent is cost_group:
                return False
            else:
                self.cost_group_parent_allowed(cost_group, parent.parent)
        else:
            return True

    """ func
    #
    #   People
    #
    """
    @debug.log
    def input_new_person(self, person_args):
        new_person = corp.Person(**person_args)
        self.add_person(new_person)
        return new_person

    @debug.log
    def add_person(self, person):
        if isinstance(person, corp.Person):
            if person not in self._people:
                self._people.append(person)
        else:
            raise TypeError("person is not an corp.Person type.")

    @debug.log
    def delete_person(self, person):
        person.delete()
        #TODO: What happens with linked objects?
        return person

    """
    #
    #   Update
    #   Fuctions updating a project
    #
    """
    @debug.log
    def update(self, identifier, * ,construction_scheme="", address=None, client=None, project_data=None,
                commissioned_date=None, planning_finished_date = None, billed_date=None, planning_status=None, **kwargs
                ):
        self.identifier = identifier
        self.construction_scheme = construction_scheme
        self.address = address
        self._client = client
        self.project_data = project_data

        if client:
            self.add_person(client)

        """ project status """
        self.commissioned_date = commissioned_date
        self.planning_finished_date = planning_finished_date
        self.billed_date = billed_date
        self.planning_status = planning_status

        self.edited()

    """
    #
    #   Restore
    #       Functions that help to reconstruct the data-structure after loading
    #
    """
    @debug.log
    def restore(self):
        self.restore_client()
        self.restore_people()
        self.restore_project_cost_calculations()
        self.restore_companies()
        self.restore_jobs()
        self.restore_invoices()
        self.restore_trades()
        self.restore_cost_groups()

    @debug.log
    def restore_client(self):
        if self._client_uid and not(self.client):
            self.client = [person for person in self.people if person.uid == self._client_uid][0]
            self._client_uid = None
        elif self._client_uid and self.client:
            raise Exception(f"Cannot restore client: client_uid ({self._client_uid}) stored and the client (uid: {self.client.uid}) was already set.")

    @debug.log
    def restore_project_cost_calculations(self):
        for pcc in self.project_cost_calculations:
            pcc.restore(self)

    @debug.log
    def restore_people(self):
        for person in self.people:
            person.restore(self)

    @debug.log
    def restore_companies(self):
        for company in self.companies:
            company.restore(self)

    @debug.log
    def restore_jobs(self):
        for job in self.jobs:
            job.restore(self)

    @debug.log
    def restore_invoices(self):
        for invoice in self.invoices:
            invoice.restore(self)

    @debug.log
    def restore_trades(self):
        for trade in self.trades:
            trade.restore(self)

    @debug.log
    def restore_cost_groups(self):
        for cost_group in self.cost_groups:
            cost_group.restore(self)
    """
    #
    #   Utility
    #
    #
    """
    def has_been_saved(self):
        return True if self.config["user_save"]["path"] else False

"""
#
#   ProjectData
#       This Object contains all hardfacts of a project, i.e. its
#       property size or the building class.
#
"""
class ProjectData(IdObject):
    """ docstring for ProjectData """

    def __init__(self, commissioned_services=None, property_size=None,
                    usable_floor_space_nuf=None, usable_floor_space_bgf=None,
                    building_class=None, construction_costs_kg300_400=None,
                    production_costs=None, contract_fee=None, execution_period=None,
                    *, uid=None, deleted=False
                    ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.commissioned_services = commissioned_services
        self.property_size = property_size
        self.usable_floor_space_nuf = usable_floor_space_nuf
        self.usable_floor_space_bgf = usable_floor_space_bgf
        self.building_class = building_class
        self.construction_costs_kg300_400 = construction_costs_kg300_400
        self.production_costs = production_costs
        self.contract_fee = contract_fee
        self.execution_period = execution_period

"""
#
#   ProjectCostCalculation
#       A project costcalculation is mainly a list of objects (dicts), which represent
#       some item or service and they belong to a CostGroup and/or Trade, with cost per unit and units.
#       Then we can make a pre-calculation of the project costs.
#       During a project, these calculation can be updated and the Trade/CostGroup budgets updated w.r.t. this.
#
"""
class ProjectCostCalculation(IdObject):
    """docstring for CostCalculation"""
    def __init__(self, name, uid=None, deleted=False, date=None, inventory=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
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
    """
    #
    #   Maybe this is not needed
    #
    def input_inventory_item(self, name, description="", price_per_unit=0, units=0,
                            unit_type="", is_active=True, cost_group=None, trade=None):
        inventory_item = InventoryItem(name=name, description=description,
                                        price_per_unit=price_per_unit, units=units,
                                        unit_type=unit_type, is_active=is_active,
                                        cost_group=cost_group, trade=trade)
        self.add_inventory_item(inventory_item)
    """
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
    """
    #
    #   get_main_cost_group_prognosis
    #       Since the 100,200,... CostGroups also have their own budgets, the actual budget for the X00 CostGroup
    #       is the sum of the X00 CostGroup plus the sum of all CostGroups that are below in the CostGroup-tree
    #       i.e., X00 is their parent or their parents parent
    #
    """
    def get_main_cost_group_prognosis(self, main_cost_group, cost_groups):
        if main_cost_group.parent is None:
            cost_group_sum = sum(self.get_cost_group_prognosis(cost_group) for cost_group in cost_groups if (cost_group is main_cost_group or cost_group.is_sub_group_of(main_cost_group)))
            return cost_group_sum
        else:
            raise Exception("main_cost_group is not a main cost_group!")

    def get_cost_group_prognosis(self, cost_group):
        cost_group_sum = sum(self.get_cost_group_items(cost_group))
        return cost_group_sum

    def get_trade_prognosis(self, trade):
        trade_sum = sum(self.get_trade_items(trade))
        return trade_sum

    """
    #
    #   Items
    #       Get items of trade/cost_group
    #
    """
    def get_cost_group_items(self, cost_group):
        cost_group_items = [item.total_price for item in self.inventory if item.is_active and item.cost_group is cost_group]
        return cost_group_items

    def get_trade_items(self, trade):
        trade_items = [item.total_price for item in self.inventory if item.is_active and item.trade is trade]
        return trade_items


    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the cost_group
    #
    """
    @debug.log
    def update(self, name, date, inventory):
        self.name = name
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

    @debug.log
    def restore_items(self, project):
        for item in self._inventory:
            item.restore(project)

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __copy__(self):
        new_inventory = list()
        for item in self.inventory:
            new_item = InventoryItem(name=item.name, description=item.description, price_per_unit=item.price_per_unit,
                                    units=item.units, unit_type=item.unit_type, is_active=item.is_active, cost_group=item.cost_group,
                                    cost_group_uid=item._cost_group_uid, trade=item.trade, trade_uid=item._trade_uid)
            new_inventory.append(new_item)
        new_pcc = ProjectCostCalculation(name=f"{self.name} copy", date=QDate.currentDate(), inventory=new_inventory)
        return new_pcc



class InventoryItem(IdObject):
    """docstring for InventoryItem"""
    def __init__(self, name, *, description="", price_per_unit=0, units=0,
                        unit_type="", is_active=True,
                        cost_group=None, cost_group_uid=None,
                        trade=None, trade_uid=None,
                         uid=None, deleted=False
                        ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
        self.description = description
        self.price_per_unit = price_per_unit
        self.units = units
        self.unit_type = unit_type
        #   is_active
        #       count the item in the calculation only if True
        self.is_active = is_active
        self.cost_group = cost_group
        self.trade = trade

        """ for restoration only """
        self._cost_group_uid = cost_group_uid
        self._trade_uid = trade_uid

    """
    #
    #   PROPERTIES
    #
    #
    """
    @property
    def total_price(self):
        return self.price_per_unit * self.units
    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the cost_group
    #
    """
    @debug.log
    def update(self, name, description, price_per_unit, units,
                    unit_type, is_active, cost_group, trade):
        self.name = name
        self.description = description
        self.price_per_unit = price_per_unit
        self.units = units
        self.unit_type = unit_type
        #   is_active
        #       count the item in the calculation only if True
        self.is_active = is_active
        self._cost_group = cost_group
        self._trade = trade
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
        self.restore_cost_group(project.cost_groups)
        self.restore_trade(project.trades)

    @debug.log
    def restore_cost_group(self, cost_groups):
        if self._cost_group_uid and not(self.cost_group):
            self.cost_group = [cost_group for cost_group in cost_groups if cost_group.uid == self._cost_group_uid][0]
            self._cost_group_uid = None
        elif self._cost_group_uid and self.cost_group:
            raise Exception(f"Cannot restore cost_group: cost_group_uid ({self._cost_group_uid}) stored and the cost_group (uid: {self.cost_group.uid}) was already set.")

    @debug.log
    def restore_trade(self, trades):
        if self._trade_uid and not(self.trade):
            self.trade = [trade for trade in trades if trade.uid == self._trade_uid][0]
            self._trade_uid = None
        elif self._trade_uid and self.trade:
            raise Exception(f"Cannot restore trade: trade_uid ({self._trade_uid}) stored and the trade (uid: {self.trade.uid}) was already set.")
