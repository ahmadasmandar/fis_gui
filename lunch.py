import serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtSerialPort
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QComboBox, QInputDialog
import serial

from Cleaner import Cleaner
import traceback
import os
import pandas as pd
from datetime import datetime
import time
import requests
import logging

#############################

class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi("lunch.ui", self)
        self.CleanAgent = Cleaner()
        self.available = False
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")
        self.font.setPointSize(15)
        self.setWindowIcon(QtGui.QIcon("ski1.ico"))
        self.setIconSize(QtCore.QSize(128, 128))

        if not os.path.exists("./logs".format(dir)):
            os.makedirs("./logs".format(dir))

        # self.InfoLogger = self.setup_logger("InfoLogger", "./logs/p_info.log", level=logging.INFO)
        self.DebugLogger = self.setup_logger("DebugLoger", "./logs/p_debug.log", level=logging.DEBUG)

        # *------------ Time --------------------------------------------------
        self.getTime(False)
        self.TimeSourceNet = False
        # *-------------------------------------------------------------------

        self.ParameterMode = False

        self.formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        # self.platform = platform.system()
        # print(self.platform)
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if "0403" in p.hwid:
                    if p.device:
                        self.available = True
                        self.port = p.device

                        self.SerialAgent = QtSerialPort.QSerialPort(
                            self.port,
                            baudRate=115200,
                            readyRead=self.receive,
                            dataBits=QtSerialPort.QSerialPort.Data8,
                            parity=QtSerialPort.QSerialPort.NoParity,
                            stopBits=QtSerialPort.QSerialPort.OneStop,
                        )
                        self.connect_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #FDD835;}")
                    else:
                        self.available = False

            if not self.available:
                self.connect_bu.setStyleSheet("background-color : #ef5350")
                self.terminal.append("Flourine Tracer not detected!! please connect the device and relunch the program")
                self.terminal.setStyleSheet("color: #ef5350 ")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            print(exc_value)

        ######################## Buttons #######################################

        self.connect_bu.clicked.connect(self.connectFunction)
        self.clean_data.clicked.connect(self.cleanFiles)
        self.send_b.clicked.connect(self.send)
        self.save_file.clicked.connect(self.saveFile)

        # press Enter to send data
        self.data_send.setText("send")
        self.data_send.returnPressed.connect(self.send)

        self.exc_com.clicked.connect(self.exportToexcel)
        self.restart_bu.clicked.connect(self.restart)
        self.clear_bu.clicked.connect(self.clear)
        self.set_time_bu.clicked.connect(self.setTime)
        self.starter_bu.clicked.connect(self.starterDialog)
        self.event_bu.clicked.connect(self.eventDialog)
        self.parameter_bu.clicked.connect(self.parameterControl)
        self.parameter_bu.setCheckable(True)
        self.parameter_bu.setEnabled(False)
        self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #c62828;}")

        # ComboBox
        self.comboBox.addItem(" ")
        self.comboBox.addItem("2.5S")
        self.comboBox.addItem("3S")
        self.comboBox.addItem("5S")
    #########################################################################

    def setup_logger(self,name, log_file, level=logging.INFO):
        """To setup as many loggers as you want"""
        self.formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)

        logger_ret = logging.getLogger(name)
        logger_ret.setLevel(level)
        logger_ret.addHandler(handler)

        return logger_ret

    ##########################################################################
    def starterDialog(self):
        try:
            text, ok = QInputDialog.getText(self, "Starter number", "please enter the Starter number")
            if ok:
                self.StarterId = str(text)
                self.terminal.append("Starter ID: {}".format(self.StarterId))
                if self.ParameterMode:
                    self.SerialAgent.write(self.StarterId.encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                    self.SerialAgent.write("a".encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                else:
                    self.terminal.append("Starter ID: {} but you are not in Parameter mode !!".format(self.StarterId))
            self.StarterEndmessage = QMessageBox.question(self, "Parameter is set", "Parameter Mode need to be exit to apply changes!", QMessageBox.Ok)
            self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")

            if self.StarterEndmessage == QMessageBox.Ok:
                self.SerialAgent.write("x".encode())
                self.SerialAgent.waitForBytesWritten(100)
                time.sleep(0.01)
                self.ParameterMode = False
                self.comboBox.setCurrentIndex(0)
                self.parameter_bu.setChecked(False)
                self.buttonControl(True)
            # if self.StarterId:
                # self.InfoLogger("StarterID_LOgger:{}".format(self.StarterId))
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def eventDialog(self):
        try:
            text, ok = QInputDialog.getText(self, "Event", "please enter the Event name:")
            if ok:
                self.EventId = str(text)
                self.terminal.append("EVENT ID: {}".format(self.EventId))
                if self.ParameterMode:
                    self.SerialAgent.write(self.EventId.encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                    self.SerialAgent.write("b".encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                else:
                    self.terminal.append("EVENT ID: {} but you are not in Parameter mode !!".format(self.EventId))
            self.StarterEndmessage = QMessageBox.question(self, "Parameter is set", "Parameter Mode need to be exit to apply changes!", QMessageBox.Ok)
            self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")

            if self.StarterEndmessage == QMessageBox.Ok:
                self.SerialAgent.write("x".encode())
                self.SerialAgent.waitForBytesWritten(100)
                time.sleep(0.01)
                self.ParameterMode = False
                self.comboBox.setCurrentIndex(0)
                self.parameter_bu.setChecked(False)
                self.buttonControl(True)
            # if self.EventId:
                # self.InfoLogger("EventId_LOgger:{}".format(self.EventId))

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def connectFunction(self, checked):
        try:
            if self.available == True:
                self.connect_bu.setText("Disconnect" if checked else "Connect")
            else:
                self.terminal.append("Flourine Tracer not detected!! ")
                return

            if checked:
                self.connect_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")
                self.SerialAgent.open(QtCore.QIODevice.ReadWrite)
                self.terminal.append("device is connected")
                self.terminal.setStyleSheet("color: #64DD17 ")
                self.parameter_bu.setEnabled(True)
                self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")
                # self.InfoLogger("Connected_LOgger: device is connected")
                # self.SerialAgent.flowControl()
                if not self.SerialAgent.isOpen():
                    if not self.SerialAgent.open(QtCore.QIODevice.ReadWrite):
                        # self.InfoLogger("Connected_LOgger: serial agent was not open")
                        self.connect_bu.setChecked(False)

            else:
                ports = list(serial.tools.list_ports.comports())
                for p in ports:
                    if "0403" in p.hwid:
                        if p.device:
                            self.available = True
                if self.available:
                    self.connect_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #FDD835;}")

                self.parameter_bu.setEnabled(False)

                self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #c62828;}")

                self.terminal.append("device is disconnected")
                # self.InfoLogger("Connected_LOgger: device is disconnected")
                if self.ParameterMode:
                    self.terminal.append("End parameter mode")
                    self.SerialAgent.write("x".encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                    # self.receive()
                self.parameter_bu.setEnabled(False)

                if not self.ParameterMode:
                    self.SerialAgent.close()
                    self.parameter_bu.setEnabled(True)

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    #####?######################################## Work with Files #####################################

    def cleanFiles(self):
        try:
            self.FilesDir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            print(self.FilesDir)
            self.CleanAgent.cleanTxtfiles(self.FilesDir)
            # self.InfoLogger("clean_LOgger: {}".format(self.FilesDir))

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def exportToexcel(self):
        try:
            self.ExcelsDir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            # os.system("start cmd /k echo hallo world!!")
            self.DataExcelFlag = self.CleanAgent.exportExcel(self.ExcelsDir)
            if self.DataExcelFlag:
                self.terminal.append("\n")
                self.terminal.append("Files Exported ")
            else:
                self.terminal.append("\n")
                self.terminal.append("there was error generating excel files!!")

            # self.InfoLogger("exportToexcel_LOgger: {}".format(self.ExcelsDir))

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    #####?#################################################################################################
    ####*#################################################################################################

    @QtCore.pyqtSlot()
    def receive(self):
        try:
            while self.SerialAgent.canReadLine():
                text = self.SerialAgent.readLine().data().decode(errors="ignore")
                self.terminal.setStyleSheet("color: black ")
                # print(text)
                if not "StringCommand" in text:
                    text = text.rstrip("\r\n")
                    self.terminal.append(text)

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    @QtCore.pyqtSlot()
    def send(self):
        try:
            if not self.SerialAgent.isOpen():
                self.terminal.setStyleSheet("color: red ")
                self.terminal.append("please connect to the device first")

                return
            else:
                self.terminal.setStyleSheet("color: black ")
                self.SendMessage = self.data_send.text()
                self.CheckComboText = self.comboBox.currentText()
                self.FirstPack = False

                if self.CheckComboText == " ":

                    if "send" in self.SendMessage or not self.SendMessage:
                        self.terminal.append("\n")
                        self.SerialAgent.writeData("1\r".encode())
                        self.SerialAgent.waitForBytesWritten(100)

                        # time.sleep(0.1)
                        # self.SerialAgent.writeData("2\r".encode())
                        # self.SerialAgent.waitForBytesWritten(100)

                    else:
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write(self.SendMessage.encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)
                else:
                    if self.CheckComboText == "2.5S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("a".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)

                    elif self.CheckComboText == "3S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("b".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)

                    elif self.CheckComboText == "5S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("c".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def clear(self):
        try:
            self.ClearMessage = QMessageBox.question(
                self,
                "  clear Confirm",
                "Do you want to clear the output! Data will be lost ?  ",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            # self.ClearMessage.setFont(self, self.font)
            # .setStyleSheet("QPushButton{border-radius: 1px; /* Green */color: white;}")

            if self.ClearMessage == QMessageBox.Yes:
                self.terminal.clear()
                self.data_send.clear()

        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    ######*#################################################################################################

    def parameterControl(self, checked):

        try:
            if self.SerialAgent.isOpen():
                if self.parameter_bu.isChecked():
                    # print("if")
                    # print(self.parameter_bu.isChecked())
                    self.SendMessage = self.data_send.text()
                    if not self.SendMessage or "send" in self.SendMessage:
                        self.ParameterMode = True
                        self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #00B0FF;}")
                        self.SerialAgent.write("p".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)
                    else:
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write(self.SendMessage.encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)

                    if self.ParameterMode:
                        self.terminal.append("we are in parameter mode")
                    else:
                        self.terminal.append("False: Parameter Mode failed to be activated")

                    self.buttonControl(False)
                else:
                    # print("else")
                    # print(self.parameter_bu.isChecked())
                    if self.ParameterMode:
                        self.terminal.append("End parameter mode")
                        self.SerialAgent.write("x".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)
                        self.ParameterMode = False
                        self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")
                        self.buttonControl(True)
                        self.parameter_bu.setChecked(False)
            else:
                self.terminal.append("device is not connected:!!")
                # self.parameter_bu.setChecked(True)
                self.parameter_bu.setChecked(False)

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def buttonControl(self, enable):
        try:
            self.connect_bu.setEnabled(enable)
            self.clean_data.setEnabled(enable)
            self.save_file.setEnabled(enable)
            self.restart_bu.setEnabled(enable)
            self.clear_bu.setEnabled(enable)

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def setTime(self):
        try:
            if not self.ParameterMode:
                self.terminal.append("Parameter Mode is not enabled please enable it first!!")
                return
            else:
                self.TimeMessage = QMessageBox.question(
                    self,
                    "  Time Source",
                    "Do you want to get Time from Internet ?  ",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if self.TimeMessage == QMessageBox.Yes:
                    self.TimeSourceNet = True
                else:
                    self.TimeSourceNet = False

                if self.TimeSourceNet:

                    self.terminal.append("Internet Time: ")
                    self.terminal.append(self.getTime(self.TimeSourceNet))
                    self.SerialAgent.write(self.getTime(self.TimeSourceNet).encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                    # time.sleep(0.1)
                    self.SerialAgent.write("t".encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)

                    self.MoreParamMessage1 = QMessageBox.question(
                        self,
                        "More Parameter",
                        "Do you want to add more Parameters?  ",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )

                    if self.MoreParamMessage1 == QMessageBox.Yes:
                        return
                    else:
                        self.SerialAgent.write("x".encode())
                        self.SerialAgent.waitForBytesWritten(100)
                        time.sleep(0.01)
                        self.ParameterMode = False
                        self.parameter_bu.setStyleSheet("QPushButton {  border-radius: 5px; background-color: #616161; color: #64DD17;}")
                        self.comboBox.setCurrentIndex(0)
                        self.buttonControl(True)

                else:
                    self.terminal.append("Local Time: ")
                    self.terminal.append(self.getTime(self.TimeSourceNet))
                    self.SerialAgent.write(self.getTime(self.TimeSourceNet).encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)
                    # time.sleep(0.1)
                    self.SerialAgent.write("t".encode())
                    self.SerialAgent.waitForBytesWritten(100)
                    time.sleep(0.01)

        except Exception as er:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def exitParameter(self):
        time.sleep(2)
        self.ParameterMode = False
        self.SerialAgent.write("x".encode())

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
                # self.InfoLogger("fileSave_LOgger: {}".format(self.name))

        except Exception as er:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

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
                stream = os.popen("python lunch.cpython-38.pyc")
                sys.exit()

        except Exception as er:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

    def getTime(self, source):
        try:
            if source:
                self.response = requests.get("http://worldtimeapi.org/api/ip")

                # Print the status code of the response.
                self.data = self.response.json()

                self.year, self.month, self.rest = str(self.data["datetime"]).split("-")

                self.day, self.rest2 = self.rest.split("T")
                self.timed, self.rest3 = self.rest2.split(".")
                # print(self.timed, self.rest3)
                self.hour, self.minute, self.second = self.timed.split(":")
                # print(self.hour, self.minute, self.second)
                # print(type(self.hour))
                self.time_tuple = (
                    int(self.year),  # Year
                    int(self.month),  # Month
                    int(self.day),  # Day
                    int(self.hour),  # Hour
                    int(self.minute),  # Minute
                    int(self.second),  # Second
                    0,  # Millisecond
                )
                self.time_string = "{0}.{1}.{2} {3}:{4}:{5}".format(self.day, self.month, self.year[2:], self.hour, self.minute, self.second)
                return self.time_string
            else:
                now = datetime.now()
                current_time = now.strftime("%d.%m.%y %H:%M:%S")

                return current_time

        except Exception as er:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            # self.DebugLogger(str(exc_value))

app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
