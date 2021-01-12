import sys
from main import Application
from ui import mainwindow

app = Application(sys.argv)
window = mainwindow.MainWindow(app.app_data)
window.show()
sys.exit(app.exec_())
