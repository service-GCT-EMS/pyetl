# -*- coding: utf-8 -*-

"""
Aauthor: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""
from PyQt5 import QtWidgets as Q
from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit,
#     QInputDialog, QApplication)
import sys

class Example(Q.QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.btn = Q.QPushButton('Dialog', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)

        self.le = Q.QLineEdit(self)
        self.le.move(130, 22)



        self.textEdit = Q.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = Q.QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('chargement script')
        openFile.triggered.connect(self.showFileDialog)

        openMacro = Q.QAction(QIcon('open.png'), 'Open', self)
        openMacro.setStatusTip('chargement macro')
        openFile.triggered.connect(self.Macroselector)

        changeStyle = Q.QAction(QIcon('open.png'), 'change style', self)
        changeStyle.setStatusTip("modifie le style de l application")
        changeStyle.triggered.connect(self.showStyleDialog)


        Test = Q.QAction(QIcon('open.png'), 'test', self)
        Test.setStatusTip("fenetre de test")
        Test.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&select')
        fileMenu.addAction(openFile)
        fileMenu.addAction(openmacro)
        fileMenu.addAction(Test)
        ParamMenu = menubar.addMenu('&parametres')
        ParamMenu.addAction(changeStyle)
        menubar.addAction(script)
        menubar.addAction(macro)
        menubar.addAction(Test)

        layout = QVBoxLayout(self)
        layout.addWidget(defaultPushButton)
        layout.addWidget(togglePushButton)
        layout.addWidget(flatPushButton)
        layout.addWidget(self.progressBar, 3, 0, 1, 2)


        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Mapper')
        self.show()




    def showDialog(self):

        text, ok = Q.QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')

        if ok:
            self.le.setText(str(text))


    def showFileDialog(self):

        fname = Q.QFileDialog.getOpenFileName(self, 'Open file', '/home')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                self.textEdit.setText(data)


    def changeStyle(self, styleName):
        Q.QApplication.setStyle(Q.QStyleFactory.create(styleName))
        # self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            Q.QApplication.setPalette(Q.QApplication.style().standardPalette())
        else:
            Q.QApplication.setPalette(self.originalPalette)

    def showStyleDialog(self):

        styleDialog=Q.QInputDialog(self)
        styleDialog.setComboBoxItems(Q.QStyleFactory.keys())
        # styleComboBox = Q.QComboBox(styleDialog)
        # styleComboBox.addItems(Q.QStyleFactory.keys())
        styleLabel = Q.QLabel("&Style:")
        styleLabel.setBuddy(styleDialog)
        styleDialog.textValueChanged[str].connect(self.changeStyle)
        styleDialog.show()

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)







if __name__ == '__main__':

    app = Q.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
