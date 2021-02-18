#####################################################
__author__ = "Ahmad Asmandar"
__copyright__ = "Copyright 2021, FIS Project"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.16"
__maintainer__ = "Ahmad Asmandar"
__email__ = "a.asmandar@kompass-sensor.com"
__status__ = "Production"
#####################################################

import os
import sys
import subprocess
import pkg_resources
import time
import logging
import traceback

## Create the Loggers
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
############################### Init Parameters

InfoLogger = setup_logger("InfoLogger", "open_info.log", level=logging.INFO)
DebugLogger = setup_logger("DebugLoger", "open_debug.log", level=logging.DEBUG)

### Start Flag check if the script was ran and don't try to install the package again
FirstRunFlag=True

## CMD execute Flag
CheckExecFlag = 0

###########################


############### list the Dir Contentes and search for Logs

content=os.listdir()
if "open_info.log" in content:
    with open("open_info.log" ,"r") as f:
        for l in f.readlines():
            #print(l)
            if "first run" in l:

                FirstRunFlag=False
                InfoLogger.info("file was found and Flag was set to False")

############## the Requiered Packages to run the Programm
required = {
    "pyqt5",
    "pandas",
    "requests",
    "serial",
    "pyserial",
    "xlwt",
    "XlsxWriter"
}

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

############# install Package Function
### TODO : need to be updated to install from Local Repos

def install(package):

    CheckExecFlag = subprocess.check_call(["pip", "install", package])
    return CheckExecFlag

if len(missing) >0 and FirstRunFlag :
    #print("hallo")
    ##!first check if python and the oteher dips are installed
    # CheckPython=subprocess.Popen("python --version",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True, stdin=subprocess.PIPE)
    # print(CheckPython.communicate()[0])
    # print(CheckPython.communicate()[1])
    # if CheckPython.communicate()[1]:
    #     CheckInstall=subprocess.Popen("./dips/python-3.8.0-amd64.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True, stdin=subprocess.PIPE)
    #     subprocess.Popen.wait()
    # if not CheckInstall.communicate()[1]:
    #     subprocess.Popen("./dips/runtime-3.1.11-win-x64.exe",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True, stdin=subprocess.PIPE)
    #     subprocess.Popen.wait()
    InfoLogger.info("first run ")
    for x in missing:
        CheckExecFlag = install(x)
        while CheckExecFlag != 0:
            time.sleep(0.1)

###################### Ececute the Programm
try:
    result = subprocess.Popen("python lunch.cpython-38.pyc",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True, stdin=subprocess.PIPE)

except  Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("*** ErrorDetails:")
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    DebugLogger.debug(str(exc_type))
    DebugLogger.debug(str(exc_value))
    DebugLogger.debug(str(exc_traceback))
