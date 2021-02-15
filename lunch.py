import serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtSerialPort
import os
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QComboBox, QInputDialog
import serial

# from Cleaner import Cleaner
import traceback
import signal

import os
import re
import pandas as pd
from datetime import datetime
import time


import requests


class Cleaner:
    def __init__(self):

        self.names = None

    def getFolderContent(self, dir=None):
        if not dir:
            self.FolderContent = os.listdir()
        else:
            self.FolderContent = os.listdir(os.path.dirname(dir))
        return self.FolderContent

    def cleanTxtfiles(self, dir=None):

        if not dir:
            return
        else:
            if not os.path.exists("./cleandata"):
                os.makedirs("./cleandata")
                os.makedirs("./excels")
            self.FolderContent = os.listdir(dir)

            for item in self.FolderContent:
                # delete the text files and the urls files to clean the library
                # print(item)
                if item.find(".txt") > 0 and item != ".git":
                    # print(item)
                    with open("./{}".format(item), "r") as f:
                        lines = f.readlines()
                        f.close()
                    #     # if (os.path.exists("./cleandata/{}".format(item))):
                    with open("./cleandata/{}".format(item), "w+") as f:
                        for line in lines:
                            if "10 Messungen" in line.strip("\n"):
                                line = line[line.find("Ch") :]
                                # print(newline)
                            # if (line.strip("\n") != "þStartfischer1 p33-6 hf8 fc6x 0.9km")
                            if "Ch" in line.strip("\n") or "V:" in line.strip("\n"):
                                f.write(line.replace(";", ""))

    def exportExcel(self):

        a = {}
        lst = {}
        content = os.listdir("./cleandata")
        result = pd.DataFrame()
        verhaeltnis = pd.DataFrame()
        deltas = pd.DataFrame()
        new_df = pd.DataFrame()
        for x in content:
            if x.find(".txt") > 0 and x != ".git":
                # print(x)
                df = pd.read_csv(
                    "./cleandata/{}".format(x),
                    names=["channal", "min", "max", "x", "y"],
                    sep="\s+",
                    encoding="ISO-8859-1",
                )
                dx = df.drop(["x", "y"], axis=1)
                # .map(lambda x: x.lstrip("+-;").rstrip("aAbBcC;"))
                dx["min"] = dx["min"]
                # .map(lambda x: x.lstrip(";").rstrip(";"))
                dx["channal"] = dx["channal"]
                if 100 in dx.index:
                    dx = dx.drop(100)
                dx["min"] = pd.to_numeric(dx["min"])
                dx["max"] = pd.to_numeric(dx["max"])
                dx["deltas"] = dx["max"] - dx["min"]
                # dx["name"]=x.strip('.txt')
                ########### Extract channals ######

                ch0 = dx[dx.channal == "Ch0:"]
                ch1 = dx[dx.channal == "Ch1:"]
                ch2 = dx[dx.channal == "Ch2:"]
                ch3 = dx[dx.channal == "Ch3:"]
                ch4 = dx[dx.channal == "Ch4:"]
                ch5 = dx[dx.channal == "Ch5:"]
                ch6 = dx[dx.channal == "Ch6:"]
                ch7 = dx[dx.channal == "Ch7:"]
                ch8 = dx[dx.channal == "Ch8:"]
                # print(ch0.head())
                ############ build the deltas #############
                delta0 = ch0["max"] - ch0["min"]
                lst["delta0"] = delta0
                delta1 = ch1["max"] - ch1["min"]
                lst["delta1"] = delta1
                delta2 = ch2["max"] - ch2["min"]
                lst["delta2"] = delta2
                delta3 = ch3["max"] - ch3["min"]
                lst["delta3"] = delta3
                delta4 = ch4["max"] - ch4["min"]
                lst["delta4"] = delta4
                delta5 = ch5["max"] - ch5["min"]
                lst["delta5"] = delta5
                delta6 = ch6["max"] - ch6["min"]
                lst["delta6"] = delta6
                delta7 = ch7["max"] - ch7["min"]
                lst["delta7"] = delta7
                delta8 = ch8["max"] - ch8["min"]
                lst["delta8"] = delta8
                # print(delta0.head())
                # format reset index

                df_new = pd.DataFrame.from_dict(lst)
                df_new = df_new.apply(lambda x: pd.Series(x.dropna().values))
                # print(df_new.head(3))
                dv = dx[dx.channal == "V:"]

                # connect the name of Measurement
                dv.index.name = x.strip(".txt")
                dx.index.name = x.strip(".txt")
                df_new.index.name = x.strip(".txt")

                dx = dx.reset_index()
                dv = dv.reset_index()
                df_new = df_new.reset_index()

                if not (dx.empty):
                    a[x.strip(".txt")] = dx
                dv = dv.replace("V:", "V:{}".format(x.strip(".txt")))
                rows = df_new.shape[0]
                # print(rows)
                for row in range(rows):
                    df_new["name"] = x.strip(".txt")
                # drop empty Dataframes
                if not (dx.empty):
                    if not os.path.exists("./excels"):
                        # os.makedirs("./cleandata")
                        os.makedirs("./excels")
                    result = pd.concat([result, dx.append(pd.Series(name="Verh..", dtype="float"))], axis=1)
                    verhaeltnis = pd.concat([verhaeltnis, dv], axis=1)
                    new_df = result.append(verhaeltnis)
                    deltas = pd.concat([deltas, df_new], axis=1)
                    dv.to_excel("./excels/{}-verhaeltnis.xlsx".format(x.strip(".txt")))
                    dx.to_excel("./excels/{}-result.xlsx".format(x.strip(".txt")))
                    df_new.to_excel("./excels/{}-deltas.xlsx".format(x.strip(".txt")))


class test_lunch(QtWidgets.QMainWindow):
    def __init__(self):
        super(test_lunch, self).__init__()
        uic.loadUi("lunch.ui", self)
        self.CleanAgent = Cleaner()
        self.available = False
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")
        self.font.setPointSize(15)

        # *------------ Time --------------------------------------------------
        self.getTime(False)
        self.TimeSourceNet = False
        # *-------------------------------------------------------------------

        self.ParameterMode = False

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
                        self.connect_bu.setStyleSheet("background-color : #fdd835")
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

        self.connect_bu.clicked.connect(self.onClicked)
        self.clean_data.clicked.connect(self.openDialog)
        self.send_b.clicked.connect(self.send)
        self.save_file.clicked.connect(self.saveFile)

        # press Enter to send data
        self.data_send.setText("send")
        self.data_send.returnPressed.connect(self.send)

        self.exc_com.clicked.connect(self.excute)
        self.restart_bu.clicked.connect(self.restart)
        self.clear_bu.clicked.connect(self.clear)
        self.set_time_bu.clicked.connect(self.setTime)
        self.starter_bu.clicked.connect(self.showDialog)

        # ComboBox
        self.comboBox.addItem(" ")
        self.comboBox.addItem("2.5S")
        self.comboBox.addItem("3S")
        self.comboBox.addItem("5S")
        self.comboBox.addItem("P")

    ##########################################################################
    def showDialog(self):
        text, ok = QInputDialog.getText(self, "Starter number", "please enter the Starter number")
        if ok:
            self.terminal.append(str(text))

    def excute(self):
        # os.system("start cmd /k echo hallo world!!")
        self.CleanAgent.exportExcel()
        self.terminal.append("Files Exported ")

    def onClicked(self, checked):
        try:
            if self.available == True:
                self.connect_bu.setText("Disconnect" if checked else "Connect")
            else:
                self.terminal.append("Flourine Tracer not detected!! ")
                return

            if checked:
                self.connect_bu.setStyleSheet("background-color : #66bb6a")
                self.SerialAgent.open(QtCore.QIODevice.ReadWrite)
                self.terminal.append("device is connected")
                self.terminal.setStyleSheet("color: green ")
                if not self.SerialAgent.isOpen():
                    if not self.SerialAgent.open(QtCore.QIODevice.ReadWrite):
                        self.connect_bu.setChecked(False)

            else:
                self.connect_bu.setStyleSheet("background-color : #ffa726")

                self.terminal.append("device is disconnected")
                if self.ParameterMode:
                    self.terminal.append("End parameter mode")
                    self.SerialAgent.write("x".encode("utf-8"))
                    self.receive()

                if not self.ParameterMode:
                    time.sleep(1)
                    self.SerialAgent.close()

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

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
            while self.SerialAgent.canReadLine():
                text = self.SerialAgent.readLine().data().decode()
                text = text.rstrip("\r\n")
                self.terminal.setStyleSheet("color: black ")
                self.terminal.append(text)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

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

                if self.CheckComboText == " ":

                    if "send" in self.SendMessage:
                        self.terminal.append("\n")
                        ValueRet = self.SerialAgent.write("1".encode("utf-8"))
                        while not self.SerialAgent.waitForBytesWritten(100):
                            delay_while = delay_while + 1

                    time.sleep(1)
                    if ValueRet >= 1:
                        ValueRet = self.SerialAgent.write("2".encode("utf-8"))

                    else:
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write(self.SendMessage.encode("utf-8"))
                        # self.SerialAgent.write("\r".encode("utf-8"))
                        # self.SerialAgent.write("\n".encode("utf-8"))
                else:
                    if self.CheckComboText == "2.5S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("a".encode("utf-8"))
                        # self.SerialAgent.write("\r".encode("utf-8"))
                        # self.SerialAgent.write("\n".encode("utf-8"))

                    elif self.CheckComboText == "3S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("b".encode("utf-8"))
                        # self.SerialAgent.write("\r".encode("utf-8"))
                        # self.SerialAgent.write("\n".encode("utf-8"))

                    elif self.CheckComboText == "5S":
                        self.terminal.append(self.SendMessage)
                        self.SerialAgent.write("c".encode("utf-8"))
                        # self.SerialAgent.write("\r".encode("utf-8"))
                        # self.SerialAgent.write("\n".encode("utf-8"))

                    elif self.CheckComboText == "P":
                        if not self.SendMessage or "send" in self.SendMessage:
                            self.ParameterMode = True
                            self.SerialAgent.write("p".encode("utf-8"))
                            # self.SerialAgent.clear()
                        else:
                            self.terminal.append(self.SendMessage)
                            self.SerialAgent.write(self.SendMessage.encode("utf-8"))

                        if self.ParameterMode:
                            self.terminal.append("we are in parameter mode")
                        else:
                            self.terminal.append("False: Parameter Mode failed to be activated")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

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
                    self.SerialAgent.write(self.getTime(self.TimeSourceNet).encode("utf-8"))
                    # time.sleep(0.1)
                    self.SerialAgent.write("t".encode("utf-8"))

                else:
                    self.terminal.append("Local Time: ")
                    self.terminal.append(self.getTime(self.TimeSourceNet))
                    self.SerialAgent.write(self.getTime(self.TimeSourceNet).encode("utf-8"))
                    # time.sleep(0.1)
                    self.SerialAgent.write("t".encode("utf-8"))

        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

        def exitParameter(self):
            time.sleep(2)
            self.ParameterMode = False
            self.SerialAgent.write("x".encode("utf-8"))

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

        except Exception as er:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

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


app = QtWidgets.QApplication([])
win = test_lunch()
win.show()
sys.exit(app.exec())
