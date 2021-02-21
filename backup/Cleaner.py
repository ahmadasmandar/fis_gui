# from Cleaner import Cleaner
import traceback
import os
import re
import pandas as pd
from datetime import datetime
import time
import logging


class Cleaner:
    def __init__(self):
        super(Cleaner, self).__init__()
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
            if not os.path.exists("{}/cleandata".format(dir)):
                os.makedirs("{}/cleandata".format(dir))
                os.makedirs("{}/excels".format(dir))
            self.FolderContent = os.listdir(dir)

            for item in self.FolderContent:
                # delete the text files and the urls files to clean the library
                # print(item)
                if item.find(".txt") > 0 and item != ".git":
                    # print(item)
                    with open("{0}/{1}".format(dir, item), "r") as f:
                        lines = f.readlines()
                        f.close()
                    #     # if (os.path.exists("./cleandata/{}".format(item))):
                    with open("{0}/cleandata/{1}".format(dir, item), "w+") as f:
                        for line in lines:
                            if "10 Messungen" in line.strip("\n"):
                                line = line[line.find("Ch") :]
                                # print(newline)
                            # if (line.strip("\n") != "þStartfischer1 p33-6 hf8 fc6x 0.9km")
                            if "Ch" in line.strip("\n") or "VR" in line.strip("\n"):
                                f.write(line.replace(";", ""))

    def exportExcel(self, dir):
        try:
            path_parent = os.path.dirname(dir)
            if not os.path.exists("{}/cleandata".format(path_parent)):
                import ctypes  # An included library with Python install.

                ctypes.windll.user32.MessageBoxW(0, "No Data to generate ", "NO Data!")
                return False

            else:
                content = os.listdir("{}/cleandata".format(path_parent))

                a = {}
                lst = {}
                result = pd.DataFrame()
                verhaeltnis = pd.DataFrame()
                deltas = pd.DataFrame()
                new_df = pd.DataFrame()
                for x in content:
                    if x.find(".txt") > 0 and x != ".git":
                        # print(x)
                        df = pd.read_csv(
                            "{0}/cleandata/{1}".format(path_parent, x),
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
                            if not os.path.exists("{}/excels".format(path_parent)):
                                # os.makedirs("{}/cleandata".format(dir))
                                os.makedirs("{}/excels".format(path_parent))
                            result = pd.concat([result, dx.append(pd.Series(name="Verh..", dtype="float"))], axis=1)
                            verhaeltnis = pd.concat([verhaeltnis, dv], axis=1)
                            new_df = result.append(verhaeltnis)
                            deltas = pd.concat([deltas, df_new], axis=1)
                            dv.to_excel("{0}/excels/{1}-verhaeltnis.xlsx".format(path_parent, x.strip(".txt")))
                            dx.to_excel("{0}/excels/{1}-result.xlsx".format(path_parent, x.strip(".txt")))
                            df_new.to_excel("{0}/excels/{1}-deltas.xlsx".format(path_parent, x.strip(".txt")))
                return True

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** ErrorDetails:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
