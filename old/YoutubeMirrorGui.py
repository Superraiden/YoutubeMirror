#__author__ = 'Tom'
#import sys
#from PyQt5 import QtCore, QtGui
#
from YoutubeMainUi import Ui_MainWindow
#
#
#class MyForm(QtGui.QMainWindow):
#    def __init__(self, parent=None):
#        QtGui.QWidget.__init__(self, parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)
#
#
#if __name__ == "__main__":
#    app = QtGui.QApplication(sys.argv)
#    myapp = MyForm()
#    myapp.show()
#    sys.exit(app.exec_())


2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from YoutubeMainUi import Ui_MainWindow

class MyFirstGuiProgram(Ui_MainWindow):
	def __init__(self, dialog):
		Ui_MainWindow.__init__(self)
		self.setupUi(dialog)

		# Connect "add" button with a custom function (addInputTextToListbox)
		self.addBtn.clicked.connect(self.addInputTextToListbox)

	def addInputTextToListbox(self):
		txt = self.myTextInput.text()
		self.listWidget.addItem(txt)

if __name__ == '__main__':
	app = QtCore.)
	dialog = QtWidgets.QDialog()

	prog = MyFirstGuiProgram(dialog)

	dialog.show()
	sys.exit(app.exec_())