import sys
from main import Application
from ui import mainwindow

app = Application(sys.argv)
app.window.show()
sys.exit(app.exec_())
