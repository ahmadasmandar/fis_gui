import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "0403" in p.hwid:
        print(p)
#################### D2xx######################
