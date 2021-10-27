import time
import can

# Function to convert Decimal number
# to Binary number
def decimalToBinary(n):
    return "{0:b}".format(int(n))

class CanRecieve:
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
        while self.loopshit == True:
            busReceive = can.interface.Bus(channel=channel0, bustype=bustype)
            msgIn = busReceive.recv(timeout=None)
            data = str(msgIn)
            datalist = data.split()
            if datalist:
                print(data)

            datalist = datalist[6:-2]
            data = ""

#             for num in datalist:
#                 print(num)
#                 print(str(decimalToBinary(int(num))))
#                 data = "".join([data, str(decimalToBinary(int(num)))])  
#                 print(data)

