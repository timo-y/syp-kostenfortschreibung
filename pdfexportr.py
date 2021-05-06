"""
#
#   PDF Export
#   The class writes a PDF file from a xlsx-Excel template
#
"""
import debug

#   only works on windows !
import win32com.client


class PDFExportr:

    """Shell class for exporting a PDF from an xlsx-Excelfile with simple
    usage.
    """

    def create_pdf(self, input_file_path, output_file_path):
        """Create a PDF.

        Args:
            input_file_path (Path): Path to input *.xlxs-file
            output_file_path (Path): Path to output *.pdf-file
        """
        o = win32com.client.Dispatch("Excel.Application")
        o.Visible = False
        wb = o.Workbooks.Open(input_file_path)
        ws_index_list = [1]  # say you want to print these sheets
        wb.WorkSheets(ws_index_list).Select()
        wb.ActiveSheet.ExportAsFixedFormat(0, output_file_path)
        wb.Close(True)
