from importsreop import np
from importsreop import sports

ports = list(sports.comports())
for p in ports:
    if "0403" in p.hwid:
        print(p)
#################### D2xx######################
