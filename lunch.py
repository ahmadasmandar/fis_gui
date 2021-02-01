#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic, QtSerialPort, QtCore
import os
import platform
import sys
from PyQt5.QtWidgets import QFileDialog

import serial.tools.list_ports


import requests


class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi('lunch.ui', self)
        self.platform = platform.system()
        print(self.platform)
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if p.device != "COM1":
                self.port = p.device

        self.serial = QtSerialPort.QSerialPort(
            self.port,
            baudRate=QtSerialPort.QSerialPort.Baud115200,
            readyRead=self.receive
        )

        self.lunch.clicked.connect(self.onClicked)
        self.folder.clicked.connect(self.openDialog)
        self.send_b.clicked.connect(self.send)

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

    def send(self):
        self.message_le = self.message.text()
        self.serial.write(self.message_le.text().encode())


app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
