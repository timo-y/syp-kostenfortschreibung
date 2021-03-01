"""
#
#   ARCH
#   This modules is for the architecture/construction related classes.
#
"""
import debug

from core.obj import corp
from core.obj import IdObject
from core.obj import restore

class ArchJob(corp.Job):
    """docstring for ArchJob"""

    def __init__(self,  id, *, uid=None, deleted=False,  company=None, trade=None, cost_group=None, job_sum=None, comment="",
                    company_ref=None, trade_ref=None, cost_group_ref=None, job_additions=None,
                    paid_safety_deposits=None):
        super(ArchJob, self).__init__(id, uid=uid, deleted=deleted, company=company, job_sum=job_sum, comment=comment, company_ref=company_ref)
        self.trade = trade
        self.cost_group = cost_group

        """
        #   job_additions
        #       List containing dicts d with d.keys() = ["date", "amount", "comment"], where d["date"]  = "date of addition" and  d["amount"] = "amount added".
        #       These are to extend the job_sum. The final job_sum then, is the initial job_sum plus sum of the amounts in this dict.
        #
        """
        self._job_additions = job_additions if job_additions else list()

        """
        #   payed_safety_deposits
        #       List containing dicts d with d.keys() = ["date", "amount", "comment"], where d["date"]  = "date of payment" and  d["amount"] = "payment amount".
        #       Then, the sum of these should eventually equal the sum of safety deposits of the invoices of the
        #       ArchJob. This would indicate, that the safety deposit is fully payed.
        #
        """
        self._paid_safety_deposits = paid_safety_deposits if paid_safety_deposits else list()

        """ for restoration only """
        self._trade_ref = trade_ref
        self._cost_group_ref = cost_group_ref

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
    #       Fuctions manipulating the job
    #
    """
    @debug.log
    def update(self, *,id, company, job_sum, trade, cost_group, paid_safety_deposits):
        super(ArchJob, self).update(id=id, company=company, job_sum=job_sum)
        self.trade = trade
        self.cost_group = cost_group
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
        self.trade = restore.restore_by(self.trade, self._trade_ref, project.trades)
        self.cost_group = restore.restore_by(self.cost_group, self._cost_group_ref, project.cost_groups)

    @debug.log
    def restore_after_import(self, project):
        super(ArchJob, self).restore_after_import(project)
        self.trade = restore.restore_by(self.trade, self._trade_ref, project.trades, by=["name"])
        self.cost_group = restore.restore_by(self.cost_group, self._cost_group_ref, project.cost_groups, by=["id"])



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
    #       Fuctions manipulating the trade
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
        self.cost_group = restore.restore_by(self.cost_group, self._cost_group_ref, project.cost_groups)

    @debug.log
    def restore_after_import(self, project):
        self.cost_group = restore.restore_by(self.cost_group, self._cost_group_ref, project.cost_groups, by=["id"])

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
        self._parent = parent

        """ for restoration only """
        self._parent_ref = parent_ref

    """
    #
    #   PROPERTIES
    #
    #
    """
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, cost_group):
        if self.parent_allowed(cost_group):
            self._parent = cost_group
        else:
            self._parent = None
            debug.warning_msg(f"Setting parent of {self.id} / {self.name} to {cost_group.id} / {cost_group.name} failed, due to recursion! Setting parent to None.")

    def is_main_group(self):
        if self.parent is None:
            return True
        else:
            return False

    def is_sub_group(self):
        return not(self.is_main_group())

    """
    #    is_sub_group_of
    #       Check whether a cost_group is subgroup of another one.
    #       Every cost_group is a subgroup of itself.
    """
    def is_sub_group_of(self, cost_group):
        """if self is cost_group:
            return True"""
        if self.parent is None:
            return False
        elif self.parent is cost_group:
            return True
        else:
            return self.parent.is_sub_group_of(cost_group)
    """
    #
    #   GETTER
    #
    #
    """
    def get_main_cost_group(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_main_cost_group()

    """
    #
    #   get_tree_level
    #       In order to render the CostGroups in a TreeWidget
    #       we need to know the layer they are at in the CostGroup-tree.
    #       Then, we can go render them layer by layer.
    """
    def get_tree_level(self):
        if self.parent is None:
            return 0
        else:
            return 1+self.parent.get_tree_level()


    """
    #
    #   UNTILITY
    #
    #
    """
    #   Check, if setting the parent to an existing
    #   cost_group is allowed (i.e. there is no recursion)
    @debug.log
    def parent_allowed(self, parent):
        if parent and parent is not self and parent.parent:
            if parent.parent is self:
                return False
            else:
                self.parent_allowed(parent.parent)
        return True
    """
    #
    #   MANIPULATE
    #       Fuctions manipulating the cost_group
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
        self.parent = restore.restore_by(self.parent, self._parent_ref, project.cost_groups)

    @debug.log
    def restore_after_import(self, project):
        self.parent = restore.restore_by(self.parent, self._parent_ref, project.cost_groups, by=["id"])

    """
    #
    #   __FUNCTIONS__
    #
    #
    """
    def __str__(self):
        return str(self.id)
