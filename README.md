# SYP-Kostenfortschreibung
Accounting application developed for Scharmer-Yu + Partner.

## Structure

    Application
    ├── core                - API and object models
    │   └── obj             - object models, e.g. invoices, jobs, ...
    ├── images              - images
    ├── lang                - language files
    ├── logs                - application logs
    ├── projects            - project saves
    ├── qss                 - stylesheets for QtPy
    ├── resources           - default lists of companies, trades and cost groups
    ├── templates           - excel-templates for generating overviews
    ├── ui                  - mainwindow PyQt configuration files 
    │   └── dlg             - dialog PyQt configuration files
    ├── debug.py            - debugging functions
    ├── decoder.py          - json decoder for the models
    ├── encoder.py          - json encoder for the models
    ├── importr.py          - import SYP-kf-excel files 
    ├── pdfexportr.py       - convert excel to pdf
    ├── templatr.py         - fill the templates with content 
    ├── zipr.py             - create/load zipped save files
    └── main.py             - main program

## Dependencies
- pyqt5     (gui)
- openpyxl  (use xlsx-templates for documentation)
- uuid      (for internal structure: pointers)
- appdirs   (for app data directory)
- pywin32   (ONLY windows! export pdf from xlsx)

### optional:
- ujson / simplejson    (for more performance for loading/saving data)
- pillow                (image support in the xlsx-templates)


## To Do
- Documentation
- Templates and Outputs of Overviews
- Features:
-- graphical representations of project
-- add scans (images) to objects
