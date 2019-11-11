#!/usr/bin/env python3

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QCalendarWidget)


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)

        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Calendar Widget")

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Preview")
        layout = QVBoxLayout()
        layout.addWidget(QCalendarWidget())
        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("General Options")
        locale = QComboBox()
        locale.addItems(['English/Germany', 'American', 'Asia'])

        weekstart = QComboBox()
        weekstart.addItems(['Sunday', 'Monday'])

        selecmode = QComboBox()
        selecmode.addItems(['Single selection'])

        # Grid + Navigation Bar
        grid = QCheckBox("Grid")
        grid.setChecked(True)
        navigationbar = QCheckBox("Navigation bar")
        navigationbar.setChecked(True)

        hboxoption = QHBoxLayout()
        hboxoption.addWidget(grid)
        hboxoption.addStretch()
        hboxoption.addWidget(navigationbar)

        hheader = QComboBox()
        hheader.addItems(['Short day names'])

        vheader = QComboBox()
        vheader.addItems(['ISO week numbers'])

        layout = QGridLayout()
        layout.addWidget(QLabel("Locale"), 0, 0)
        layout.addWidget(locale, 0, 1)
        layout.addWidget(QLabel("Week starts on"), 1, 0)
        layout.addWidget(weekstart, 1, 1)
        layout.addWidget(QLabel("Selection mode"), 2, 0)
        layout.addWidget(selecmode, 2, 1)
        layout.addLayout(hboxoption, 3, 0, 1, 2)
        layout.addWidget(QLabel("Horizontal header"), 4, 0)
        layout.addWidget(hheader, 4, 1)
        layout.addWidget(QLabel("Vertical header"), 5, 0)
        layout.addWidget(vheader, 5, 1)

        # layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1) # Only column 1 can stretch, column 0 fixed size

        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftGroupBox = QGroupBox("Dates")

        layout = QVBoxLayout()
        self.bottomLeftGroupBox.setLayout(layout)

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Text Format")

        layout = QVBoxLayout()
        self.bottomRightGroupBox.setLayout(layout)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())