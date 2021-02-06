import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
  if "1A86" in p.hwid:
    print("ping")
    print(p.hwid)
#################### D2xx######################
