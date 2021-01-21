"""
#
#   ENCODER
#   Encoding objects into JSON-format
#
"""
"""
#
#   ULTRA JSON
#       More performance de- and encoding
#
#"""
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json
from json import JSONEncoder

from core.obj import corp, proj, arch

# maybe stupid
class AllEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, proj.Project):
            ProjectEncoder.default(o)
        elif isinstance(o. proj.ProjectData):
            ProjectDataEncoder.default(o)
        elif isinstance(o, corp.Company):
            CompanyEncoder.default(o)
        elif isinstance(o, arch.Trade):
            TradeEncoder.default(o)
        elif isinstance(o, arch.CostGroup):
            CostGroupEncoder.default(o)
        elif isinstance(o, corp.Person):
            PersonEncoder.default(o)
        elif isinstance(o, corp.Address):
            AddressEncoder.default(o)
        elif isinstance(o, ArchJob):
            ArchJobEncoder.default(o)
        elif isinstance(o, corp.Job):
            JobEncoder.default(o)
        elif isinstance(o. corp.Invoice):
            InvoiceEncoder.default(o)
        return JSONEncoder.default(self, o)


class ProjectEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, proj.Project):
            encoded_project = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "config": o.config,
                "construction_scheme": o.construction_scheme,
                "identifier": o.identifier,
                "address": AddressEncoder().default(o.address) if o.address else None,
                "client_uid": o.client.uid_to_json() if o.client else None,
                "project_data": ProjectDataEncoder().default(o.project_data),
                "commissioned_date": o.commissioned_date.toString() if o.commissioned_date else None,
                "planning_finished_date": o.planning_finished_date.toString() if o.planning_finished_date else None,
                "billed_date": o.billed_date.toString() if o.billed_date else None,
                "planning_status": o.planning_status
            }
            return encoded_project
        return JSONEncoder.default(self, o)

class ProjectDataEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, proj.ProjectData):
            encoded_project_data = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "commissioned_services": o.commissioned_services,
                "property_size": o.property_size,
                "usable_floor_space_nuf": o.usable_floor_space_nuf,
                "usable_floor_space_bgf": o.usable_floor_space_bgf,
                "building_class": o.building_class,
                "construction_costs_kg300_400": o.construction_costs_kg300_400,
                "production_costs": o.production_costs,
                "contract_fee": o.contract_fee,
                "execution_period" : (o.execution_period[0].toString(), o.execution_period[1].toString()) if o.execution_period else None
            }
            return encoded_project_data
        return JSONEncoder.default(self, o)

class ProjectCostCalculationEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, proj.ProjectCostCalculation):
            encoded_pcc = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "name": o.name,
                "date": o.date.toString(),
                "inventory": [InventoryItemEncoder().default(item) for item in o.inventory]
            }
            return encoded_pcc
        return JSONEncoder.default(self, o)

class InventoryItemEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, proj.InventoryItem):
            encoded_inventory_item = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "name": o.name,
                "description": o.description,
                "price_per_unit": o.price_per_unit,
                "units": o.units,
                "unit_type": o.unit_type,
                "is_active": o.is_active,
                "cost_group_uid": o.cost_group.uid_to_json(),
                "trade_uid": o.trade.uid_to_json()
            }
            return encoded_inventory_item
        return JSONEncoder.default(self, o)

class CompanyEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, corp.Company):
            encoded_company = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "name": o.name,
                "service": o.service,
                "service_type": o.service_type,
                "budget": o.budget,
                "contact_person_ref":
                {
                "uid": o.contact_person.uid_to_json() if o.contact_person else None,  # needs to be encoded properly (or uid only)
                "first_name": o.contact_person.first_name if o.contact_person else None,
                "last_name": o.contact_person.last_name if o.contact_person else None,
                }
            }
            return encoded_company
        return JSONEncoder.default(self, o)

class TradeEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, arch.Trade):
            encoded_trade = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "name": o.name,
                "cost_group_ref":
                {
                    "uid": o.cost_group.uid_to_json(),
                    "id": o.cost_group.id
                } if o.cost_group else None,
                "budget": o.budget,
                "comment": o.comment
            }
            return encoded_trade
        return JSONEncoder.default(self, o)

class CostGroupEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, arch.CostGroup):
            encoded_cost_group = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "id": o.id,
                "name": o.name,
                "description": o.description,
                "budget": o.budget,
                "parent_ref":
                {
                    "uid": o.parent.uid_to_json(),
                    "id": o.parent.id
                } if o.parent else None,
            }
            return encoded_cost_group
        return JSONEncoder.default(self, o)

class PersonEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, corp.Person):
            encoded_person = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "first_name": o.first_name,
                "last_name": o.last_name,
                "address": AddressEncoder().default(o.address) if o.address else None,
                "telephone": o.telephone,
                "fax": o.fax,
                "mobile": o.mobile,
                "email": o.email,
                "company_uid": o.company.uid_to_json() if o.company else None,
            }
            return encoded_person
        return JSONEncoder.default(self, o)

class AddressEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, corp.Address):
            encoded_address = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "street": o.street,
                "house_number": o.house_number,
                "city": o.city,
                "state": o.state,
                "zipcode": o.zipcode,
                "country": o.country
            }
            return encoded_address
        return JSONEncoder.default(self, o)

class JobEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, corp.Job):
            encoded_job = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "id": o.id,
                "company_uid": o.company.uid_to_json() if o.company else None,
                "job_sum": o.job_sum
            }
            return encoded_job
        return JSONEncoder.default(self, o)

class ArchJobEncoder(JobEncoder):

    def default(self, o):
        if isinstance(o, arch.ArchJob):
            encoded_job = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "id": o.id,
                "company_uid": o.company.uid_to_json() if o.company else None,
                "job_sum": o.job_sum,
                "trade_uid": o.trade.uid_to_json() if o.trade else None,
                "job_additions": [{"date": job_addition["date"].toString(), "name": job_addition["name"], "amount": job_addition["amount"], "comment": job_addition["comment"]} for job_addition in o.job_additions],
                "paid_safety_deposits": [{"date": psd["date"].toString(), "amount": psd["amount"], "comment": psd["comment"]} for psd in o.paid_safety_deposits],
            }
            return encoded_job
        return JobEncoder.default(self, o)

class InvoiceEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, corp.Invoice):
            encoded_invoice = {
                # meta data
                o.__class__.__name__: True,
                "uid": o.uid_to_json(),
                "deleted": o.is_deleted(),
                #  data
                "id": o.id,
                "company_uid": o.company.uid_to_json() if o.company else None,
                "job_uid": o.job.uid_to_json() if o.job else None,
                "cumulative": o.cumulative,
                "invoice_date": o.invoice_date.toString() if o.invoice_date else None,
                "inbox_date": o.inbox_date.toString() if o.inbox_date else None,
                "checked_date": o.checked_date.toString() if o.checked_date else None,
                "amount": o.amount,
                "verified_amount": o.verified_amount,
                "rebate": o.rebate,
                "reduction_insurance_costs": o.reduction_insurance_costs,
                "reduction_usage_costs": o.reduction_usage_costs,
                "reduce_prev_invoices": o.reduce_prev_invoices,
                "prev_invoices_amount": o.prev_invoices_amount,
                "prev_invoices_uids": [invoice.uid_to_json() for invoice in o.prev_invoices],
                "VAT": o.VAT,
                "safety_deposit": o.safety_deposit,
                "safety_deposit_amount": o._safety_deposit_amount,
                "discount": o.discount,
                "due_date": o.due_date.toString(),
                "due_date_discount": o.due_date_discount.toString() if o.due_date_discount else None
            }
            return encoded_invoice
        return JSONEncoder.default(self, o)
