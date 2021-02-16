import os
import sys
import sys
import subprocess
import pkg_resources
import time

required = {
    "pyqt5",
    "pandas",
    "requests",
    "serial",
    "pyserial",
}

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
check = 0


def install(package):
    check = os.system("start /wait   cmd  /c pip install {}".format(package))
    print(subprocess.Popen("python lunch.cpython-38.pyc", shell=True, stdout=subprocess.PIPE).stdout.read())
    # subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return check


if missing:
    print("hallo")
    for x in missing:
        check = install(x)
        while check != 0:
            time.sleep(0.1)

check = subprocess.Popen("python lunch.cpython-38.pyc", shell=False)
print(check)
# os.system("cmd /c python lunch.cpython-38.pyc")
# subprocess.run(["python lunch.cpython-38.pyc"])
# subprocess.Popen("python lunch.cpython-38.pyc", shell=True)
# pid = subprocess.Popen([sys.executable, "lunch.cpython-38.pyc"], shell=True)
