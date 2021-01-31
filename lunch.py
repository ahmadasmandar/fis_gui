#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic, QtSerialPort, QtCore
import os
import platform
import sys
from PyQt5.QtWidgets import QFileDialog


import requests


class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi('lunch.ui', self)
        self.platform = platform.system()
        print(self.platform)
        self.serial = QtSerialPort.QSerialPort(
            'COM5',
            baudRate=QtSerialPort.QSerialPort.Baud115200,
            readyRead=self.receive
        )

        self.lunch.clicked.connect(self.onClicked)
        self.folder.clicked.connect(self.openDialog)

    def onClicked(self, checked):
        self.lunch.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.lunch.setChecked(False)
        else:
            self.serial.close()

    def openDialog(self):
        self.file = str(QFileDialog.getExistingDirectory(
            self, "Select Directory"))
        os.system("   echo This directory {}".format(self.file))

    @ QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.terminal.append(text)


app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
