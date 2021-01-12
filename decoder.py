"""
#
#   DECODER
#   Decoding JSON into objects
#
"""
import debug

import uuid
import json
from json import JSONDecoder
from datetime import datetime

from PyQt5.QtCore import QDate

from core.obj import corp, proj, arch, uid
#maybe stupid
class AllDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "UID" in dct:
            UIDDecoder.dict_to_object(dct)
        elif "Project" in dct:
            ProjectDecoder.dict_to_object(dct)
        elif "ProjectData" in dct:
            ProjectDataDecoder.dict_to_object(dct)
        elif "Company" in dct:
            CompanyDecoder.dict_to_object(dct)
        elif "Trade" in dct:
            TradeDecoder.dict_to_object(dct)
        elif "CostGroup" in dct:
            CostGroupDecoder.dict_to_object(dct)
        elif "Person" in dct:
            PersonDecoder.dict_to_object(dct)
        elif "Address" in dct:
            AddressDecoder.dict_to_object(dct)
        elif "Job" in dct:
            JobDecoder.dict_to_object(dct)
        elif "ArchJob" in dct:
            ArchJobDecoder.dict_to_object(dct)
        elif "Invoice" in dct:
            InvoiceDecoder.dict_to_object(dct)
        return dct


class UIDDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "UID" in dct:
            args = {
                "class_name": dct["class_name"],
                "uid":  uuid.UUID(dct["uid"]),
                "created_date": datetime.fromisoformat(dct["created_date"]),
                "edited_date":  datetime.fromisoformat(dct["edited_date"]) if dct["edited_date"] else None
            }
            return uid.UID(**args)
        return dct

class ProjectDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Project" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "config": dct["config"],
                "identifier": dct["identifier"],
                "construction_scheme": dct["construction_scheme"],
                "address": AddressDecoder().object_hook(dct["address"]) if dct["address"] else None,
                "client_uid": UIDDecoder().object_hook(dct["client_uid"]) if dct["client_uid"] else None,
                "project_data": ProjectDataDecoder().object_hook(dct["project_data"]) if dct["project_data"] else None,
                "commissioned_date": QDate.fromString(dct["commissioned_date"]) if dct["commissioned_date"] else None,
                "planning_finished_date": QDate.fromString(dct["planning_finished_date"]) if dct["planning_finished_date"] else None,
                "billed_date": QDate.fromString(dct["billed_date"]) if dct["billed_date"] else None,
                "planning_status": dct["planning_status"]
            }
            return proj.Project(**args)
        return dct

class ProjectDataDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "ProjectData" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "commissioned_services": dct["commissioned_services"],
                "property_size": dct["property_size"],
                "usable_floor_space_nuf": dct["usable_floor_space_nuf"],
                "usable_floor_space_bgf": dct["usable_floor_space_bgf"],
                "building_class": dct["building_class"],
                "construction_costs_kg300_400": dct["construction_costs_kg300_400"],
                "production_costs": dct["production_costs"],
                "contract_fee": dct["contract_fee"],
                "execution_period" : (QDate.fromString(dct["execution_period"][0]), QDate.fromString(dct["execution_period"][1])) if dct["execution_period"] else None
            }
            return proj.ProjectData(**args)
        return dct

class CompanyDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Company" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "name": dct["name"],
                "service": dct["service"],
                "service_type": dct["service_type"],
                "budget": dct["budget"],
                "contact_person_ref":
                {
                    "uid": UIDDecoder().object_hook(dct["contact_person_ref"]["uid"]) if dct["contact_person_ref"]["uid"] else None, # needs to be encoded properly (or uid only)
                    "first_name": dct["contact_person_ref"]["first_name"],
                    "last_name": dct["contact_person_ref"]["last_name"]
                }
            }
            return corp.Company(**args)
        return dct

class TradeDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Trade" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "name": dct["name"],
                "cost_group_ref":
                {
                    "uid": UIDDecoder().object_hook(dct["cost_group_ref"]["uid"]) if dct["cost_group_ref"]["uid"] else None,
                    "id": dct["cost_group_ref"]["id"]
                },
                "budget": dct["budget"],
                "comment": dct["comment"]
            }
            return arch.Trade(**args)
        return dct

class CostGroupDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "CostGroup" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "id": dct["id"],
                "name": dct["name"],
                "description": dct["description"],
                "budget": dct["budget"]
            }
            return arch.CostGroup(**args)
        return dct

class PersonDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Person" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "first_name": dct["first_name"],
                "last_name": dct["last_name"],
                "address": AddressDecoder().object_hook(dct["address"]) if dct["address"] else None,
                "telephone": dct["telephone"],
                "fax": dct["fax"],
                "mobile": dct["mobile"],
                "email": dct["email"],
            }
            return corp.Person(**args)
        return dct

class AddressDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Address" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "street": dct["street"],
                "house_number": dct["house_number"],
                "city": dct["city"],
                "state": dct["state"],
                "zipcode": dct["zipcode"],
                "country": dct["country"]
            }
            return corp.Address(**args)
        return dct

class JobDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Job" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "id": dct["id"],
                "company_uid": UIDDecoder().object_hook(dct["company_uid"]) if dct["company_uid"] else None,
                "job_sum": dct["job_sum"]
            }
            return corp.Job(**args)
        return dct

class ArchJobDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "ArchJob" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "id": dct["id"],
                "company_uid": UIDDecoder().object_hook(dct["company_uid"]) if dct["company_uid"] else None,
                "job_sum": dct["job_sum"],
                "trade_uid": UIDDecoder().object_hook(dct["trade_uid"]) if dct["trade_uid"] else None,
                "paid_safety_deposits": [{"date": datetime.fromisoformat(psd["date"]), "amount": psd["amount"]} for psd in dct["paid_safety_deposits"]]
            }
            return arch.ArchJob(**args)
        return dct

class InvoiceDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    @debug.log
    def dict_to_object(self, dct):
        if "Invoice" in dct:
            args = {
                "uid": UIDDecoder().object_hook(dct["uid"]),
                "deleted": dct["deleted"],
                "id": dct["id"],
                "company_uid": UIDDecoder().object_hook(dct["company_uid"]) if dct["company_uid"] else None,
                "job_uid": UIDDecoder().object_hook(dct["job_uid"]) if dct["job_uid"] else None,
                "cumulative": dct["cumulative"],
                "invoice_date": QDate.fromString(dct["invoice_date"]) if dct["invoice_date"] else None,
                "inbox_date": QDate.fromString(dct["inbox_date"]) if dct["inbox_date"] else None,
                "checked_date": QDate.fromString(dct["checked_date"]) if dct["checked_date"] else None,
                "amount": dct["amount"],
                "verified_amount": dct["verified_amount"],
                "rebate": dct["rebate"],
                "reduction_insurance_costs": dct["reduction_insurance_costs"],
                "reduction_usage_costs": dct["reduction_usage_costs"],
                "reduce_prev_invoices": dct["reduce_prev_invoices"],
                "prev_invoices_uids": [UIDDecoder().object_hook(uid) for uid in dct["prev_invoices_uids"]] if dct["prev_invoices_uids"] else None,
                "prev_invoices_amount": dct["prev_invoices_amount"],
                "VAT": dct["VAT"],
                "safety_deposit": dct["safety_deposit"],
                "safety_deposit_amount": dct["safety_deposit_amount"] if dct["safety_deposit_amount"] else None,
                "discount": dct["discount"],
                "due_date": QDate.fromString(dct["due_date"]) if dct["due_date"] else None,
                "due_date_discount": QDate.fromString(dct["due_date_discount"]) if dct["due_date_discount"] else None
            }
            return corp.Invoice(**args)
        return dct
