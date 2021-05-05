import sys
from main import Application

app = Application(sys.argv)
app.window.show()
sys.exit(app.exec_())
