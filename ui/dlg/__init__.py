""" dialog package """
from ui.dlg.project_dlg import ProjectDialog
from ui.dlg.person_dlg import PersonDialog
from ui.dlg.address_dlg import AddressDialog
from ui.dlg.invoice_dlg import InvoiceDialog
from ui.dlg.job_dlg import JobDialog
from ui.dlg.company_dlg import CompanyDialog
from ui.dlg.trade_dlg import TradeDialog
from ui.dlg.cost_group_dlg import CostGroupDialog
from ui.dlg.config_dlg import ConfigDialog
from ui.dlg.pay_safety_deposit_dlg import PaySafetyDepositDialog

from ui.dlg.open_dialogs import open_project_dialog
from ui.dlg.open_dialogs import open_person_dialog
from ui.dlg.open_dialogs import open_address_dialog
from ui.dlg.open_dialogs import open_invoice_dialog
from ui.dlg.open_dialogs import open_job_dialog
from ui.dlg.open_dialogs import open_company_dialog
from ui.dlg.open_dialogs import open_trade_dialog
from ui.dlg.open_dialogs import open_cost_group_dialog
from ui.dlg.open_dialogs import open_config_dialog
from ui.dlg.open_dialogs import open_pay_safety_deposit_dialog
from ui.dlg.open_dialogs import open_delete_prompt
from ui.dlg.open_dialogs import open_save_curr_project_prompt

del project_dlg
del person_dlg
del address_dlg
del invoice_dlg
del job_dlg
del company_dlg
del pay_safety_deposit_dlg

del open_dialogs
