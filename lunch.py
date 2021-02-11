import serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtSerialPort, QtCore, QtGui
import os
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from Cleaner import Cleaner
import traceback
import signal


class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi("lunch.ui", self)
        self.CleanAgent = Cleaner()
        self.available = False
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")
        self.font.setPointSize(15)
        # self.platform = platform.system()
        # print(self.platform)
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "0403" in p.hwid:
                    if p.device:
                        self.available = True
                        self.port = p.device
                        self.serial = QtSerialPort.QSerialPort(
                            self.port, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead=self.receive
                        )
                        self.lunch.setStyleSheet("background-color : #fdd835")
                    else:
                        self.available = False

            if not self.available:
                self.lunch.setStyleSheet("background-color : #ef5350")
                self.terminal.append("Flourine Tracer not detected!! please connect the device and relunch the program")
                self.terminal.setStyleSheet("color: #ef5350 ")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** Exception:", exc_type)
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)

        ######################## Buttons #######################################

        self.lunch.clicked.connect(self.onClicked)
        self.clean_data.clicked.connect(self.openDialog)
        self.send_b.clicked.connect(self.send)
        self.save_file.clicked.connect(self.saveFile)

        ### press Enter to send data
        self.data_send.setText("send")
        self.data_send.returnPressed.connect(self.send)

        self.exc_com.clicked.connect(self.excute)
        self.restart_bu.clicked.connect(self.restart)
        self.clear_bu.clicked.connect(self.clear)

    ##########################################################################
    def excute(self):
        # os.system("start cmd /k echo hallo world!!")
        self.CleanAgent.exportExcel()
        self.terminal.append("Files Exported ")

    def onClicked(self, checked):
        try:
            if self.available == True:
                self.lunch.setText("Disconnect" if checked else "Connect")
            else:
                self.terminal.append("Flourine Tracer not detected!! ")
                return

            if checked:
                self.lunch.setStyleSheet("background-color : #66bb6a")
                self.serial.open(QtCore.QIODevice.ReadWrite)
                self.terminal.append("device is connected")
                self.terminal.setStyleSheet("color: green ")
                if not self.serial.isOpen():
                    if not self.serial.open(QtCore.QIODevice.ReadWrite):
                        self.lunch.setChecked(False)

            else:
                self.serial.close()
                self.lunch.setStyleSheet("background-color : #ffa726")

                self.terminal.append("device is disconnected")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print(exc_value)

    def openDialog(self):
        try:
            self.file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            # os.system("   echo This directory {}".format(self.file))
            self.CleanAgent.cleanTxtfiles(self.file)
            self.terminal.append("\n")
            self.terminal.append("Files have been cleaned")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    @QtCore.pyqtSlot()
    def receive(self):
        try:
            while self.serial.canReadLine():
                text = self.serial.readLine().data().decode()
                text = text.rstrip("\r\n")
                self.terminal.setStyleSheet("color: black ")
                self.terminal.append(text)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    def send(self):
        try:
            if not self.serial.isOpen():
                self.terminal.setStyleSheet("color: red ")
                self.terminal.append("please connect to the device first")

                return
            else:
                self.terminal.setStyleSheet("color: black ")
                self.message_le = self.data_send.text()
                if "Send" in self.message_le:
                    self.terminal.append("\n")
                    self.serial.write("\n".encode())
                else:
                    self.terminal.append(self.message_le)
                    self.serial.write(self.message_le.encode())

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    def saveFile(self):
        try:
            self.name = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "Text files (*.txt)")[0]
            if not self.name:
                return
            else:
                self.Foldercontent = self.CleanAgent.getFolderContent(self.name)
                with open(self.name, "w") as file:
                    file = open(self.name, "w")
                    text = str(self.terminal.toPlainText())
                    file.write(text)
                    file.write("\n")
                    # for item in self.Foldercontent:
                    #     file.write(item)
                    #     file.write('\n')
                    file.close()
        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    def restart(self):
        try:
            self.message_6 = QMessageBox.question(
                self,
                "  RESTART Confirm",
                "Do you want to Restart ?  ",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if self.message_6 == QMessageBox.Yes:
                stream = os.popen("python lunch.py")
                sys.exit()

        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    def clear(self):
        try:
            self.message_7 = QMessageBox.question(
                self,
                "  clear Confirm",
                "Do you want to clear the output! Data will be lost ?  ",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            
            #self.message_7.setFont(self, self.font)
            # .setStyleSheet("QPushButton{border-radius: 1px; /* Green */color: white;}")

            if self.message_7 == QMessageBox.Yes:
                self.terminal.clear()

        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)


app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
