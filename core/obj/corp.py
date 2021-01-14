"""
#
#   CORP
#   This is a module for all the basic (corporate) objects.
#
"""
import debug

from core.obj.uid import IdObject
DEFAULT_VAT = 0.16

class Company(IdObject):
    """docstring for Company"""

    def __init__(self, name, service, service_type, *, uid=None, deleted=False, budget=0, contact_person=None, contact_person_ref=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
        self.service = service
        self.service_type = service_type
        self.budget = budget
        self.contact_person = contact_person

        """ for restoration only """
        self._contact_person_ref = contact_person_ref

    """
    #
    #   UPDATE
    #   Fuctions updating a company
    #
    """
    @debug.log
    def update(self, name, service, service_type, budget, contact_person):
        self.name = name
        self.service = service
        self.service_type = service_type
        self.budget = budget
        self.contact_person = contact_person
        if contact_person:
            contact_person.company = self
        """ set edited date """
        self.edited()

    """
    #
    #   RESTORE
    #   Generally to restore pointers after loading a project.
    #
    """
    @debug.log
    def restore(self, project):
        self.restore_contact_person(project.people)

    """
    #
    #   RESTORE AFTER IMPORT
    #   When importing, the saved uid might not make sense and probably doesnt exist.
    #   With this restore, we are comparing names, ids and/or other data to set pointers.
    #
    """
    @debug.log
    def restore_after_import(self, project):
        self.restore_contact_person_by_name(project.people)

    @debug.log
    def restore_contact_person(self, people):
        if self._contact_person_ref["uid"] and not(self.contact_person):
            self.contact_person = [person for person in people if person.uid == self._contact_person_ref["uid"]][0]
            self._contact_person_ref = None
        elif self._contact_person_ref and self.contact_person:
            raise Exception(f"Cannot restore contact_person: contact_person_uid ({self._contact_person_ref['uid']}) stored and the contact_person (uid: {self.contact_person.uid}) was already set.")

    @debug.log
    def restore_contact_person_by_name(self, people):
        if isinstance(self.contact_person, str):
            temp_list = [contact_person for contact_person in people if contact_person.first_name == self._contact_person_ref["first_name"] and contact_person.last_name == self._contact_person_ref["last_name"]]
            self.contact_person = temp_list[0] if len(temp_list)>0 else None
            self._contact_person_ref = None
    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return str(self.name)

    # for importing companies, dont import, if they have the same name
    def __eq__(self):
        return str(self.name)

class Person(IdObject):
    """docstring for Person"""

    def __init__(self,*, first_name="", last_name="", uid=None, deleted=False,  address=None,
                telephone=None, fax=None, mobile=None, email=None, company=None, company_uid=None
                ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.first_name = first_name
        self.last_name = last_name
        # kwargs
        self.address = address
        self.telephone = telephone
        self.fax = fax
        self.mobile = mobile
        self.email = email
        self.company = company

        """ for restoration only """
        self._company_uid = company_uid

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    """
    #
    #   UPDATE
    #   Fuctions updating a person
    #
    """
    @debug.log
    def update(self, first_name, last_name, address,
                telephone, fax, mobile, email, company):
        self.first_name = first_name
        self.last_name = last_name
        # kwargs
        self.address = address
        self.telephone = telephone
        self.fax = fax
        self.mobile = mobile
        self.email = email
        self.company = company
        """ set edited date """
        self.edited()

    """
    #
    #   RESTORE
    #
    #
    """
    @debug.log
    def restore(self, project):
        self.restore_company(project.companies)

    @debug.log
    def restore_company(self, companies):
        if self._company_uid and not(self.company):
            self.company = [company for company in companies if company.uid == self._company_uid][0]
            self._company_uid = None
        elif self._company_uid and self.company:
            raise Exception(f"Cannot restore company: company_uid ({self._company_uid}) stored and the company (uid: {self.company.uid}) was already set.")

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return " ".join([self.first_name, self.last_name])


class Address(IdObject):
    """docstring for Address"""

    def __init__(self, street, house_number, city, state, zipcode, country, *, uid=None, deleted=False):
        super().__init__(self, uid=uid, deleted=deleted)
        self.street = street
        self.house_number = house_number
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country

    def validate(self):
        # validate address
        pass

    """
    #
    #   UPDATE
    #   Fuctions updating an address
    #
    """
    @debug.log
    def update(self, street, house_number, city, state, zipcode, country):
        self.street = street
        self.house_number = house_number
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country
        """ set edited date """
        self.edited()

class Job(IdObject):
    """docstring for Job"""

    def __init__(self, id, *, uid=None, deleted=False,  company=None, job_sum=None, company_uid=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.id = id
        self.company = company
        self.job_sum = job_sum

        """ for restoration only """
        self._company_uid = company_uid

    """
    #
    #   UPDATE
    #   Fuctions updating a job
    #
    """
    @debug.log
    def update(self, id, company, job_sum):
        self.id = id
        self.company = company
        self.job_sum = job_sum
        """ set edited date """
        self.edited()

    """
    #
    #   RESTORE
    #
    #
    """
    @debug.log
    def restore(self, project):
        self.restore_company(project.companies)

    @debug.log
    def restore_company(self, companies):
        if self._company_uid and not(self.company):
            self.company = [company for company in companies if company.uid == self._company_uid][0]
            self._company_uid = None
        elif self._company_uid and self.company:
            raise Exception(f"Cannot restore company: company_uid ({self._company_uid}) stored and the company (uid: {self.company.uid}) was already set.")

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return str(self.id)

class Invoice(IdObject):
    """docstring for Invoice"""

    def __init__(self, *, id=None, uid=None, deleted=False,  company=None, job=None, cumulative=True,
                    invoice_date=None, inbox_date=None, checked_date=None,
                    amount=0, verified_amount=0, rebate=0, reduction_insurance_costs=0,
                    reduction_usage_costs=0, reduce_prev_invoices=True, prev_invoices=None, prev_invoices_uids=None,
                    prev_invoices_amount=None, VAT=DEFAULT_VAT, safety_deposit=0, safety_deposit_amount=None, discount=0,
                    due_date=None, due_date_discount=None, company_uid=None, job_uid=None
                    ):
        super().__init__(self, uid=uid, deleted=deleted)
        self.id = id
        self.company = company
        self.job = job
        self.cumulative = cumulative
        self.invoice_date = invoice_date
        self.inbox_date = inbox_date
        self.checked_date = checked_date
        self.amount = amount
        self.verified_amount = verified_amount
        self.rebate = rebate
        self.reduction_insurance_costs = reduction_insurance_costs
        self.reduction_usage_costs = reduction_usage_costs
        self.reduce_prev_invoices = reduce_prev_invoices
        self._prev_invoices = prev_invoices if prev_invoices is not None else list()
        self._prev_invoices_amount =  self.get_prev_invoices_amount() if prev_invoices_amount is None else prev_invoices_amount
        self.VAT = VAT
        self.safety_deposit = safety_deposit
        self._safety_deposit_amount = safety_deposit_amount
        self.discount = discount
        self.due_date = due_date
        self.due_date_discount = due_date_discount

        """ for restoration only """
        self._company_uid = company_uid
        self._job_uid = job_uid
        self._prev_invoices_uids = prev_invoices_uids if prev_invoices_uids is not None else list()

    """
    #
    #   PROPERTIES
    #
    #
    """
    """
    #   second level properties
    """
    @property
    def trade(self):
        return self.job.trade

    @property
    def cost_group(self):
        return self.job.trade.cost_group if self.job.trade else None

    """
    #   calculated properties
    """
    @property
    def amount_VAT_amount(self):
        return self.amount * self.VAT

    @property
    def amount_w_VAT(self):
        return self.amount + self.amount_VAT_amount

    @property
    def verified_amount_VAT_amount(self):
        return self.verified_amount * self.VAT

    @property
    def verified_amount_w_VAT(self):
        return self.verified_amount + self.verified_amount_VAT_amount

    """ previous payments """
    @property
    def prev_invoices(self):
        return self._prev_invoices
    @prev_invoices.setter
    def prev_invoices(self, invoices):
        self._prev_invoices = [invoice for invoice in invoices if self.no_recursion(invoice)]
        if len(self._prev_invoices) != len(invoices):
           debug.log_warning("setting prev_invoices, there was recursion detected, which has been denied. Some data may be lost if the invoices were not sorted by date before omitting.")

    @property
    def prev_invoices_amount(self):
        return self._prev_invoices_amount
    @prev_invoices_amount.setter
    def prev_invoices_amount(self, amount):
        raise Exception("prev_invoices_amount cannot be set. Use the update_prev_invoices_amount() function to set.")
    def get_prev_invoices_amount(self):
        if self.prev_invoices and self.reduce_prev_invoices and self.cumulative:
            """
            #
            #   Find most max date from previous invoices
            #   then filter previous invoices
            """
            most_recent_invoice_date = max(invoice.invoice_date for invoice in self.prev_invoices if invoice.cumulative)
            invoices = [invoice for invoice in self.prev_invoices if invoice.invoice_date == most_recent_invoice_date and invoice.cumulative]
            if len(invoices)>1:
                """
                #
                #   If there exist more than one previous invoice with
                #   this date, look at the date created and take the most recent one
                #   (this is unique).
                """
                most_recent_created_date = max(invoice.uid.created_date for invoice in invoices)
                invoices = [invoice for invoice in invoices if invoice.uid.created_date is most_recent_created_date]
            return [invoice.verified_amount for invoice in invoices][0]
        else:
            return 0

    def update_prev_invoices_amount(self):
        self._prev_invoices_amount = self.get_prev_invoices_amount()

    @property
    def amount_wout_prev_payments(self):
        return self.verified_amount - self.prev_invoices_amount

    """ reductions """
    @property
    def rebate_amount(self):
        return self.amount_wout_prev_payments * self.rebate

    @property
    def reduction_insurance_costs_amount(self):
        return self.amount_wout_prev_payments * self.reduction_insurance_costs

    @property
    def reduction_usage_costs_amount(self):
        return self.amount_wout_prev_payments * self.reduction_usage_costs

    @property
    def reduction_total(self):
        return self.reduction_insurance_costs + self.reduction_usage_costs

    @property
    def reduction_total_amount(self):
        return self.amount_wout_prev_payments * self.reduction_total

    @property
    def amount_a_reductions_amount(self):
        return self.amount_wout_prev_payments - self.rebate_amount - self.reduction_insurance_costs_amount - self.reduction_usage_costs_amount

    @property
    def amount_a_reductions_amount_VAT_amount(self):
        return self.amount_a_reductions_amount * self.VAT

    @property
    def amount_a_reductions_amount_w_VAT(self):
        return self.amount_a_reductions_amount+self.amount_a_reductions_amount_VAT_amount

    """ approved amount """
    @property
    def safety_deposit_amount(self):
        safety_deposit_amount = self._safety_deposit_amount if self._safety_deposit_amount is not None else self.amount_a_reductions_amount_w_VAT * self.safety_deposit
        return safety_deposit_amount

    @property
    def approved_amount(self):
        return self.amount_a_reductions_amount_w_VAT - self.safety_deposit_amount

    @property
    def discount_amount(self):
        return self.approved_amount * self.discount

    @property
    def approved_amount_a_discount_amount(self):
        return self.approved_amount - self.discount_amount

    """
    #
    #   UPDATE
    #   Fuctions updating an invoice
    #
    """
    @debug.log
    def update(self, *, id, company, job,
                cumulative, invoice_date, inbox_date,
                checked_date, amount, verified_amount,
                rebate, reduction_insurance_costs,
                reduction_usage_costs, reduce_prev_invoices,
                prev_invoices_amount=None,
                prev_invoices, VAT,
                safety_deposit, safety_deposit_amount=None,
                discount, due_date, due_date_discount
                ):
        self.id = id
        self.company = company
        self.job = job
        self.cumulative = cumulative
        self.invoice_date = invoice_date
        self.inbox_date = inbox_date
        self.checked_date = checked_date
        self.amount = amount
        self.verified_amount = verified_amount
        self.rebate = rebate
        self.reduction_insurance_costs = reduction_insurance_costs
        self.reduction_usage_costs = reduction_usage_costs
        self.reduce_prev_invoices = reduce_prev_invoices
        self._prev_invoices_amount = self.get_prev_invoices_amount() if prev_invoices_amount is None else prev_invoices_amount
        self.prev_invoices = prev_invoices
        self.VAT = VAT
        self.safety_deposit = safety_deposit
        self._safety_deposit_amount = safety_deposit_amount
        self.discount = discount
        self.due_date = due_date
        self.due_date_discount = due_date_discount
        """ set edited date """
        self.edited()

    """ prev invoices """
    @debug.log
    def add_prev_invoice(self, invoice):
        if not(self._prev_invoices):
            if isinstance(invoice, Invoice):
                if self.no_recursion(invoice):
                    self.prev_invoices.append(invoice)
                else:
                    raise Exception("Invoices cant be prev_invoices of each other (recursion will go infinite)!")
            else:
                raise TypeError("Invoice is not a corp.Invoice object.")
        else:
            raise Exception("Restore the previous invoices first (restore_prev_invoices())!")

    @debug.log
    def remove_prev_invoice(self, invoice):
        if isinstance(invoice, Invoice):
            self.prev_invoices.remove(invoice)
        else:
            raise TypeError("Invoice is not a corp.Invoice object.")

    @debug.log
    def clear_prev_invoices(self):
        self.prev_invoices=list()

    """
    #
    #   RESTORE
    #
    #
    """
    @debug.log
    def restore(self, project):
        self.restore_prev_invoices(project.invoices)
        self.restore_company(project.companies)
        self.restore_job(project.jobs)

    @debug.log
    def restore_prev_invoices(self, invoices):
        if self._prev_invoices_uids and len(self.prev_invoices)==0:
            self.prev_invoices = [invoice for invoice in invoices if invoice.uid in self._prev_invoices_uids]
            self._prev_invoices_uids = None
        elif self._prev_invoices_uids and len(self.prev_invoices)>0 :
            raise Exception("Cannot restore invoices, prev_invoices is non-empty!")

    @debug.log
    def restore_company(self, companies):
        if self._company_uid and not(self.company):
            self.company = [company for company in companies if company.uid == self._company_uid][0]
            self._company_uid = None
        elif self._company_uid and self.company:
            raise Exception(f"Cannot restore company: company_uid ({self._company_uid}) stored and the company (uid: {self.company.uid}) was already set.")

    @debug.log
    def restore_job(self, jobs):
        if self._job_uid and not(self.job):
            self.job = [job for job in jobs if job.uid == self._job_uid][0]
            self._job_uid = None
        elif self._job_uid and self.job:
            raise Exception(f"Cannot restore job: job_uid ({self._job_uid}) stored and the job (uid: {self.job.uid}) was already set.")

    """
    #
    #   UTILITY
    #
    #
    """
    @debug.log
    def no_recursion(self, invoice):
        if self.uid is invoice.uid:
            return False
        elif invoice._prev_invoices_uids and self.uid in invoice._prev_invoices_uids:
            return False
        elif invoice.prev_invoices and self in invoice.prev_invoices:
            return False
        return True

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return str(self.id)
