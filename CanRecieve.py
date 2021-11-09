import time
import can

# Function to convert Decimal number
# to Binary number
def decimalToBinary(n):
    return "{0:b}".format(int(n))

class CanRecieve:
    Sensors = [0]*2048
#             ["COPV 1", 1, 0],
#             ["COPV 2", 2, 0],
#             ["Fuel Tank", 3, 0],
#             ["Lox Tank", 4, 0],
#             ["Lox\n Dome", 5, 0],
#             ["Fuel\n Dome", 6, 0],
#             ["MV\n Pneumatic", 7, 0],
#             ["Fuel\n Prop Inlet", 8, 0],
#             ["LOx\n Prop Inlet", 9, 0],
#             # Engine Sensors
#             ["Fuel Inlet", 10, 0],
#             ["Fuel Injector", 11, 0],
#             ["LOX Injector", 12, 0],
#             ["Pc Chamber 1", 13, 0],
#             ["Pc Chamber 2", 14, 0],
#             ["Pc Chamber 3", 15, 0],
#             ["Temp\n ChamberExt", 16, 0],
#             ["LC1: ", 17, 0],
#             ["LC2: ", 18, 0],
#             ["LC3: ", 19, 0]
#         
    # Binary String of bools that hold the current position of the valves
    ValveState = ""
    def __init__(self):
        self.loopshit = True
        
        
    def terminate(self):
        self.loopshit = False
      
    def run(self):
        bustype = 'socketcan'
        channel0 = 'can0'
        channel1 = 'can1'
        n = 1
        print("hi")
        busReceive = can.interface.Bus(channel=channel0, bustype=bustype)
        while self.loopshit == True:
            msgIn = busReceive.recv(timeout=None)
            data = str(msgIn)
            datalist = data.split()
            actualData = datalist[7:-2]
            ID = datalist[3]
            ID = int(ID, 16)
            byte0 = int(actualData[0], 16)
            byte1 = int(actualData[1], 16)
            value = byte0*256+byte1
            print(value)
            CanRecieve.Sensors[ID] = value
#             if datalist:
#                 print(data)

#             datalist = datalist[6:-2]
#             data = ""

#             for num in datalist:
#                 print(num)
#                 print(str(decimalToBinary(int(num))))
#                 data = "".join([data, str(decimalToBinary(int(num)))])  
#                 print(data)

