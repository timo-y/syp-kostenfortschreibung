"""
#
#   ARCH
#   This modules is for the architecture/construction related classes.
#
"""
import debug

from core.obj.uid import IdObject
from core.obj import corp

class ArchJob(corp.Job):
    """docstring for ArchJob"""

    def __init__(self,  id, *, uid=None, deleted=False,  company=None, job_sum=None,
                    company_uid=None, trade=None, trade_uid=None, job_additions=None,
                    paid_safety_deposits=None):
        super(ArchJob, self).__init__(id, uid=uid, deleted=deleted, company=company, job_sum=job_sum, company_uid=company_uid)
        self.trade = trade
        """
        #   job_additions
        #   List containing dicts d with d.keys() = ["date", "amount", "comment"], where d["date"]  = "date of addition" and  d["amount"] = "amount added".
        #   These are to extend the job_sum. The final job_sum then, is the initial job_sum plus sum of the amounts in this dict.
        #
        """
        self._job_additions = job_additions if job_additions else list()

        """
        #   payed_safety_deposits
        #   List containing dicts d with d.keys() = ["date", "amount", "comment"], where d["date"]  = "date of payment" and  d["amount"] = "payment amount".
        #   Then, the sum of these should eventually equal the sum of safety deposits of the invoices of the
        #   ArchJob. This would indicate, that the safety deposit is fully payed.
        #
        """
        self._paid_safety_deposits = paid_safety_deposits if paid_safety_deposits else list()

        """ for restoration only """
        self._trade_uid = trade_uid

    """
    #
    #   PROPERTIES
    #
    #
    """
    @property
    def job_additions(self):
        return self._job_additions

    @job_additions.setter
    def job_additions(self, list):
        raise Exception("You can't set job_additions. Use add_job_addition(date, amount) instead!")

    @property
    def job_sum_w_additions(self):
        return self.job_sum+sum([job_addition["amount"] for job_addition in self._job_additions])

    def add_job_addition(self, date, name, amount, comment=""):
        self._job_additions.append({"date": date, "name": name, "amount": amount, "comment": comment})

    def remove_job_addition(self, job_addition):
        self._job_additions.remove(job_addition)

    @property
    def paid_safety_deposits(self):
        return self._paid_safety_deposits

    @paid_safety_deposits.setter
    def paid_safety_deposits(self, list):
        raise Exception("You can't set paid_safety_deposits. Use pay_safety_deposit(date, amount) instead!")

    @property
    def paid_safety_deposits_sum(self):
        return sum([psd["amount"] for psd in self._paid_safety_deposits])

    def pay_safety_deposit(self, date, amount, comment=""):
        self._paid_safety_deposits.append({"date": date, "amount": amount, "comment": comment})

    def remove_psd(self, psd):
        self._paid_safety_deposits.remove(psd)

    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the job
    #
    """
    @debug.log
    def update(self, *,id, company, job_sum, trade, paid_safety_deposits):
        super(ArchJob, self).update(id=id, company=company, job_sum=job_sum)
        self.trade = trade
        self._paid_safety_deposits = paid_safety_deposits

    """
    #
    #   RESTORE
    #
    #
    """
    @debug.log
    def restore(self, project):
        super(ArchJob, self).restore(project)
        self.restore_trade(project.trades)

    @debug.log
    def restore_trade(self, trades):
        if self._trade_uid and not(self.trade):
            self.trade = [trade for trade in trades if trade.uid == self._trade_uid][0]
            self._trade_uid = None
        elif self._trade_uid and self.trade:
            raise Exception(f"Cannot restore trade: trade_uid ({self._trade_uid}) stored and the trade (uid: {self.trade.uid}) was already set.")


class Trade(IdObject):
    """docstring for Trade"""

    def __init__(self, *, name, budget, comment, uid=None, deleted=False,  cost_group=None, cost_group_ref=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.name = name
        self.cost_group = cost_group
        self.budget = 0 if budget == "" else budget
        self.comment = comment

        """ for restoration only """
        self._cost_group_ref = cost_group_ref

    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the trade
    #
    """
    @debug.log
    def update(self, name, cost_group, budget, comment):
        self.name = name
        self.cost_group = cost_group
        self.budget = 0 if budget == "" else budget
        self.comment = comment
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
        self.restore_cost_group(project.cost_groups)

    @debug.log
    def restore_after_import(self, project):
        self.restore_cost_group_by_id(project.cost_groups)

    @debug.log
    def restore_cost_group(self, cost_groups):
        if self._cost_group_ref and not(self.cost_group):
            self.cost_group = [cost_group for cost_group in cost_groups if cost_group.uid == self._cost_group_ref["uid"]][0]
            self._cost_group_ref = None
        elif self._cost_group_ref and self.cost_group:
            raise Exception(f"Cannot restore cost_group: cost_group_uid ({self._cost_group_ref['uid']}) stored and the cost_group (uid: {self.cost_group.uid}) was already set.")

    @debug.log
    def restore_cost_group_by_id(self, cost_groups):
        if self._cost_group_ref and not(self.cost_group):
            temp_list = [cost_group for cost_group in cost_groups if cost_group.id == self._cost_group_ref["id"]]
            if len(temp_list)>0:
                self.cost_group = temp_list[0]
                self._cost_group_ref = None
            else:
                debug.log_warning(f"Can't restore cost_group by id, since there was no cost_group with the given id")

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return self.name

class CostGroup(IdObject):
    """docstring for CostGroup"""

    def __init__(self, id, name="", description="", *, uid=None, deleted=False, budget=0, parent=None, parent_ref=None):
        super().__init__(self, uid=uid, deleted=deleted)
        self.id = id
        self.name = name
        self.description = description
        self.budget = budget
        self.parent = parent

        """ for restoration only """
        self._parent_ref = parent_ref

    """
    #
    #   PROPERTIES
    #
    #
    """
    def is_main_group(self):
        if self.parent is None:
            return True
        else:
            return False

    def is_sub_group(self):
        return not(self.is_main_group())

    def is_sub_group_of(self, cost_group):
        if self.parent is None:
            return False
        else:
            if self.parent is cost_group:
                return True
            else:
                return self.parent.is_sub_group_of(cost_group)

    """
    #
    #   MANIPULATE
    #   Fuctions manipulating the cost_group
    #
    """
    @debug.log
    def update(self, id, name, description, budget, parent):
        self.id = id
        self.name = name
        self.description = description
        self.budget = budget
        self.parent = parent
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
        self.restore_parent(project.cost_groups)

    @debug.log
    def restore_after_import(self, project):
        self.restore_parent_by_id(project.cost_groups)

    @debug.log
    def restore_parent(self, cost_groups):
        if self._parent_ref and not(self.parent):
            self.parent = [cost_group for cost_group in cost_groups if cost_group.uid == self._parent_ref["uid"]][0]
            self._parent_ref = None

        elif self._parent_ref and self.parent:
            raise Exception(f"Cannot restore parent: parent_uid ({self._parent_ref['uid']}) stored and the parent (uid: {self.parent.uid}) was already set.")

    @debug.log
    def restore_parent_by_id(self, cost_groups):
        if self._parent_ref and not(self.parent):
            temp_list = [cost_group for cost_group in cost_groups if cost_group.id == self._parent_ref["id"]]
            if len(temp_list)>0:
                self.parent = temp_list[0]
                self._parent_uid = None
            else:
                debug.log_warning(f"Can't restore parent by id, since there was no cost_group with the given id")

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return str(self.id)
