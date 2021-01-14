"""
#
#   TEMPLATE
#   The Template-class writes the info to the proper excel-template.
#
"""
import debug

import openpyxl
from openpyxl.styles.borders import Border, Side

from datetime import datetime
import os
from os.path import expanduser

class Template():
    """docstring for Template"""
    def __init__(self, template_dir, template_filename, save_path):
        self.template_dir_path = os.path.join(os.getcwd(), template_dir)
        self.template_file_path = os.path.join(self.template_dir_path, template_filename)

        self.wb = openpyxl.load_workbook(self.template_file_path)
        self.ws = self.wb["TEMPLATE"]

        self.date_format = "DD.MM.YYYY"
        self.amount_format = "#,##0.00 € ;-#,##0.00 € ; - € "

    @debug.log
    def add_rows(self, before_row, number_of_rows):
        self.ws.move_range(f"A{before_row}:AA{99+before_row}", rows=number_of_rows, cols=0)
        #   the actuall insertion is not needed, we can just move the bottom part down!
        # self.ws.insert_rows(before_row, number_of_rows)
        # self.ws.move_range(f"AA1:BA{100}", rows=+(number_of_rows+before_row-1), cols=-26)

    @debug.log
    def write_data(self, excel_data):
        for write_cell in excel_data:
            # Data can be assigned directly to cells
            self.ws[write_cell["cell"]] = write_cell["data"]

    @debug.log
    def save_file(self):
        # create directory if non-existing
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))
        # Save the file
        self.wb.save(self.save_path)

class InvoiceCheckExcelTemplate(Template):
    """docstring for InvoiceCheckExcelTemplate"""
    def __init__(self, project_identifier, app_data_config, invoice, save_dir=None, filename=None):
        self.template_dir = app_data_config["template_subdir"]
        self.template_filename = "invoice_check.xlsx"

        self.filename = filename if filename else "invoice_check"
        default_save_dir = save_dir if save_dir else os.path.join(os.getcwd(), app_data_config["save_dir"], project_identifier, app_data_config["invoice_check_subdir"])
        self.save_path = os.path.join(default_save_dir, f"{self.filename}.xlsx")

        super(InvoiceCheckExcelTemplate, self).__init__(template_dir=self.template_dir,
                                                        template_filename=self.template_filename,
                                                        save_path=self.save_path)
        """
        #   I
        #   If we have more than 10 previous invoices,
        #   we need to add rows and hence have to move
        #   the cells underneath the listing by the number
        #   of lines added
        """
        self.new_rows = 0
        if len(invoice.prev_invoices)>10:
            self.new_rows = len(invoice.prev_invoices)-10

        """
        #
        #   EXCEL DATA
        #   Gather the data for the invoice check and connect
        #   it to the cells.
        #
        """
        self.excel_data = [
            {"cell": "D7", "data": invoice.company.name},
            {"cell": "H8", "data": invoice.invoice_date.toPyDate()},
            {"cell": "C8", "data": project_identifier},
            {"cell": "C10", "data": " ".join(["Auftrag:", str(invoice.job.id)])},
            {"cell": "E11", "data": invoice.id},
            {"cell": "H11", "data": invoice.amount},
            {"cell": "H12", "data": invoice.verified_amount},
            {"cell": f"G{25+self.new_rows}", "data": invoice.reduction_total},
            {"cell": f"H{25+self.new_rows}", "data": invoice.reduction_total_amount},
            {"cell": f"H{26+self.new_rows}", "data": invoice.amount_a_reductions_amount},
            {"cell": f"C{27+self.new_rows}", "data": invoice.VAT},
            {"cell": f"H{27+self.new_rows}", "data": invoice.amount_a_reductions_amount_VAT_amount},
            {"cell": f"H{28+self.new_rows}", "data": invoice.amount_a_reductions_amount_w_VAT},
            {"cell": f"E{31+self.new_rows}", "data": invoice.safety_deposit},
            {"cell": f"H{31+self.new_rows}", "data": invoice.safety_deposit_amount},
            {"cell": f"H{32+self.new_rows}", "data": invoice.job.paid_safety_deposits_sum},
            {"cell": f"H{34+self.new_rows}", "data": invoice.approved_amount},
            {"cell": f"E{35+self.new_rows}", "data": invoice.discount},
            {"cell": f"H{35+self.new_rows}", "data": invoice.discount_amount},
            {"cell": f"H{36+self.new_rows}", "data": invoice.approved_amount_a_discount_amount},
            {"cell": f"D{39+self.new_rows}", "data": invoice.checked_date.toPyDate() if invoice.checked_date else invoice.invoice_date.toPyDate()},
            {"cell": f"F{34+self.new_rows}", "data": invoice.due_date.toPyDate()},
            {"cell": f"F{36+self.new_rows}", "data": invoice.due_date_discount.toPyDate() if invoice.due_date_discount else "-"}
        ]
        """
        #
        #   PREVIOUS INVOICES
        #   Add one line per previous invoice.
        #
        """
        j = 0
        for prev_invoice in invoice.prev_invoices:
            invoice_line = [
                {"cell": f"D{15+j}", "data": prev_invoice.invoice_date.toPyDate()},
                {"cell": f"F{15+j}", "data": prev_invoice.id},
                {"cell": f"H{15+j}", "data": prev_invoice.verified_amount}
            ]
            self.excel_data.extend(invoice_line)
            j += 1

    @debug.log
    def make_file(self):
        #   format previous invoices tab
        for i in range(10):
            #   date column format
            self.ws[f"D{15+i}"].number_format = self.date_format
            #   amount column format
            self.ws[f"H{15+i}"].number_format = self.amount_format
        self.add_rows(15, self.new_rows)
        #   Add borders to the newly added rows
        for j in range(self.new_rows):
            self.ws[f"C{15+j}"].border = Border(left=Side(style='thin'))
            self.ws[f"H{15+j}"].border = Border(right=Side(style='thin'))
            #   date column format
            self.ws[f"D{15+j}"].number_format = self.date_format
            #   amount column format
            self.ws[f"H{15+j}"].number_format = self.amount_format

        self.write_data(self.excel_data)
        self.save_file()


