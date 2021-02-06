import serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtSerialPort, QtCore
import os
import sys
from PyQt5.QtWidgets import QFileDialog
from Cleaner import Cleaner


class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi('lunch.ui', self)
        self.CleanAgent = Cleaner()

        # self.platform = platform.system()
        # print(self.platform)
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "1A86" in p.hwid:
                if p.device:
                    self.port = p.device
                    self.serial = QtSerialPort.QSerialPort(
                        self.port,
                        baudRate=QtSerialPort.QSerialPort.Baud115200,
                        readyRead=self.receive
                    )

        self.lunch.clicked.connect(self.onClicked)
        self.clean_data.clicked.connect(self.openDialog)
        self.send_b.clicked.connect(self.send)
        self.save_file.clicked.connect(self.saveFile)
        self.data_send.setText("Send")

    def onClicked(self, checked):
        self.lunch.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.lunch.setChecked(False)
                    self.serial.write(" ".encode())
        else:
            self.serial.close()

    def openDialog(self):
        self.file = str(QFileDialog.getExistingDirectory(
            self, "Select Directory"))
        # os.system("   echo This directory {}".format(self.file))
        self.CleanAgent.cleanTxtfiles(self.file)
        self.terminal.append('\n')
        self.terminal.append("Files have been cleaned")

    @ QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.terminal.append(text)

    def send(self):
        try:
            self.message_le = self.data_send.text()
            self.terminal.append(self.message_le)
            self.serial.write(self.message_le.encode())
        except Exception:
            ex_type, ex, tb = sys.exc_info()
            print(ex)

    def saveFile(self):
        try:
            self.name = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save file", "", "Text files (*.txt)")[0]
            if not self.name:
                return
            else:
                self.Foldercontent = self.CleanAgent.getFolderContent(
                    self.name)
                with open(self.name, 'w') as file:
                    file = open(self.name, 'w')
                    text = str(self.terminal.toPlainText())
                    file.write(text)
                    file.write('\n')
                    # for item in self.Foldercontent:
                    #     file.write(item)
                    #     file.write('\n')
                    file.close()
        except Exception as er:
            print(er)


app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
