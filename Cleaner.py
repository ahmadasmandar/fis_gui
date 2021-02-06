import os
import re
import pandas as pd


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
                                line = line[line.find("Ch"):]
                                # print(newline)
                            # if (line.strip("\n") != "þStartfischer1 p33-6 hf8 fc6x 0.9km")
                            if "Ch" in line.strip("\n") or "V:" in line.strip("\n"):
                                f.write(line.replace(";", ""))
