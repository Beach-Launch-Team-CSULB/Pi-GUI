import can
import bitstring
from bitarray.util import ba2int
from bitarray import bitarray
import time
import struct

class CanReceive:
    Sensors = [0] * 1028
    sensorTimestamps = [0] * 1028
    Valves = [0] * 64
    ValvesRenegadeEngine = [0] * 64
    ValvesRenegadeProp = [0] * 64
    Controllers = [[0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50, [0] * 50]
    VehicleStates = [
        "Setup",
        "Passive",
        "Standby",
        "Test",
        "Abort",
        "Vent",
        "OFF Nominal",
        "Hi Press Arm",
        "Hi Press Pressurized",
        "Tank Press Arm",
        "Tank Press Pressurized",
        "Fire Arm",
        "Fire"
        ]
    NodeStatusBang = VehicleStates[0]
    NodeStatusRenegadeEngine = VehicleStates[0]
    NodeStatusRenegadeProp = VehicleStates[0]

    AutosequenceTime = 0
    AutosequenceTimeDupes = 0
    ThrottlePoints = {}
    def __init__(self, channel='can0', bustype='socketcan'):
        print("HI")
        self.loop = True
        self.busargs = {'channel':channel, 'bustype':bustype}

    def run(self):
        # starts Canbus
        #bus_type = 'virtual'#'socketcan'
        #channel0 = 'vcan0'
        bus_receive = can.interface.Bus(**self.busargs)#channel=channel0, bustype=bus_type)

        while self.loop:
            msg_in = bus_receive.recv(timeout=None)

            # Grabs Message ID
            msg_id = int(msg_in.arbitration_id)
            try:
                msg_id_bin = str(bitstring.BitArray(int=msg_id, length=32).bin)
            except Exception as e:
                print(e)
                continue
            ID_A_bin = msg_id_bin[-11:]
            ID_A = ba2int(bitarray(ID_A_bin))
            # Grabs the data in the msg
            data_list_hex = msg_in.data.hex()
            data_bin = bitstring.BitArray(hex=data_list_hex).bin

            # if data is empty
#             if data_list_hex[0:16] == '':
#                 continue
            
            self.translateMessage(ID_A, msg_id_bin, data_bin, data_list_hex)
            
    def translateMessage(self, ID_A, msg_id_bin, data_bin, data_list_hex):

        if ID_A == 546:
            self.ID_546(ID_A, msg_id_bin, data_bin, data_list_hex)
        if ID_A == 552:
            self.ID_552(ID_A, msg_id_bin, data_bin, data_list_hex)
        if ID_A == 547:
            self.ID_547(ID_A, msg_id_bin, data_bin, data_list_hex)
        elif 510 < ID_A < 530:
            self.ID_Between_510_530(ID_A, msg_id_bin, data_bin, data_list_hex)
        elif 50 < ID_A < 427:
            self.ID_Between_050_427(ID_A, msg_id_bin, data_bin, data_list_hex)
            

        elif ID_A > 1000:
            self.translateControllerMessage(ID_A, msg_id_bin, data_bin, data_list_hex)

    def translateControllerMessage(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        " CONTROLLERS"
        #print(ID_A)

        if ID_A == 1100:
            self.ID_1100_Controller(ID_A, msg_id_bin, data_bin, data_list_hex)
        elif ID_A == 1506:
            self.ID_1506_Controller(ID_A, msg_id_bin, data_bin, data_list_hex)
        elif data_list_hex:
            self.ID_Misc_Controller(ID_A, msg_id_bin, data_bin, data_list_hex)

    def ID_546(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        """
        Valves
        
        """
        #print(msg_id_bin, data_bin)
        HP1_bin = int(msg_id_bin[12:20])
        HP1_bin = str(HP1_bin)[::-1]
        if HP1_bin:
            HP1 = ba2int(bitarray(HP1_bin))
            #print(HP1)
            #print(msg_id_bin)
            CanReceive.ValvesRenegadeEngine[1] = HP1

        HP2_bin = int(msg_id_bin[4:12])
        HP2_bin = str(HP2_bin)[::-1]
        HP2 = ba2int(bitarray(HP2_bin))

        CanReceive.ValvesRenegadeEngine[2] = HP2
        for i in range(3, 11):
            HPi_bin = data_bin[(i - 3) * 8:(i - 2) * 8]
            HPi = ba2int(bitarray(HPi_bin))
            CanReceive.ValvesRenegadeEngine[i] = HPi
    
    def ID_552(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        """
        Valves
        
        """
        #print(msg_id_bin, data_bin)
        HP1_bin = int(msg_id_bin[12:20])
        HP1_bin = str(HP1_bin)[::-1]
        if HP1_bin:
            HP1 = ba2int(bitarray(HP1_bin))
            #print(HP1)
            #print(msg_id_bin)
            CanReceive.Valves[1] = HP1

        HP2_bin = int(msg_id_bin[4:12])
        HP2_bin = str(HP2_bin)[::-1]
        HP2 = ba2int(bitarray(HP2_bin))

        CanReceive.Valves[2] = HP2
        for i in range(3, 11):
            HPi_bin = data_bin[(i - 3) * 8:(i - 2) * 8]
            HPi = ba2int(bitarray(HPi_bin))
            CanReceive.Valves[i] = HPi

    def ID_547(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        """
        Valves
        
        """
        #print(msg_id_bin, data_bin)
        HP1_bin = int(msg_id_bin[12:20])
        HP1_bin = str(HP1_bin)[::-1]
        if HP1_bin:
            HP1 = ba2int(bitarray(HP1_bin))
            #print(HP1)
            #print(msg_id_bin)
            CanReceive.ValvesRenegadeProp[1] = HP1

        HP2_bin = int(msg_id_bin[4:12])
        HP2_bin = str(HP2_bin)[::-1]
        HP2 = ba2int(bitarray(HP2_bin))

        CanReceive.ValvesRenegadeProp[2] = HP2
        for i in range(3, 11):
            HPi_bin = data_bin[(i - 3) * 8:(i - 2) * 8]
            HPi = ba2int(bitarray(HPi_bin))
            CanReceive.ValvesRenegadeProp[i] = HPi
    
    def ID_Between_510_530(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        "NODE STATES"
        "Engine Node 2"
        "Prop Node 3"
        try:
            if ID_A == 514: 
                CanReceive.NodeStatusRenegadeEngine = CanReceive.VehicleStates[int(data_list_hex[0:2], 16)]
            if ID_A == 515: 
                CanReceive.NodeStatusRenegadeProp = CanReceive.VehicleStates[int(data_list_hex[0:2], 16)]
            if ID_A == 520: 
                CanReceive.NodeStatusBang = CanReceive.VehicleStates[int(data_list_hex[0:2], 16)]
            self.translateMessage(ID_A, msg_id_bin, data_bin, data_list_hex)
        except:
            return
        
    def ID_Between_050_427(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        """
        Sensors
        """
        #print(ID_A, "NADA")
        if data_list_hex:
            TimeStamp_bin = msg_id_bin[0:18]
            TimeStamp = ba2int(bitarray(TimeStamp_bin))
            msg_id = ID_A
            value = ba2int(bitarray(data_bin[0:16]), signed = False)
            CanReceive.Sensors[msg_id] = value/10
            CanReceive.sensorTimestamps[msg_id] = TimeStamp
            #print(msg_id, value/10, data_list_hex,data_bin[0:16])
            if len(data_list_hex) > 6:
                msg_id_2 = int(data_list_hex[4:6], base=16)
                value_2 =  ba2int(bitarray(data_bin[24:40]), signed = False)
                CanReceive.Sensors[msg_id_2] = value_2/10
                CanReceive.sensorTimestamps[msg_id_2] = TimeStamp
                #print(msg_id_2, value_2/10, data_list_hex,data_bin[24:40])

            if len(data_list_hex) > 12:

                msg_id_3 = int(data_list_hex[10:12], base=16)
                value_3 = ba2int(bitarray(data_bin[48:64]), signed = False)
                CanReceive.Sensors[msg_id_3] = value_3/10
                CanReceive.sensorTimestamps[msg_id_3] = TimeStamp
                #print(msg_id_3, value_3/10, data_list_hex,data_bin[48:64])

    def ID_1100_Controller(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        "AUTOSEQUENCE"
        CanReceive.PrevAutosequenceTime = CanReceive.AutosequenceTime
        CanReceive.AutosequenceTime = ba2int(bitarray(data_bin), signed = True)/1000000

        if CanReceive.PrevAutosequenceTime == CanReceive.AutosequenceTime:
            CanReceive.AutosequenceTimeDupes += 1
        else:
            print(CanReceive.AutosequenceTimeDupes, "Dupes parsed.")
            print("Autosequence Time:", CanReceive.AutosequenceTime)
            CanReceive.AutosequenceTimeDupes = 0

    def ID_1506_Controller(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        Time = int(data_list_hex[0:4], base=16)
        ThrottlePoint = int(data_list_hex[4:8], base=16)
        if Time == 0:
            CanReceive.ThrottlePoints = []
        #print(Time, ThrottlePoint)
        CanReceive.ThrottlePoints.append([Time, ThrottlePoint])
        try:
            Time = int(data_list_hex[8:12], base=16)
            ThrottlePoint = int(data_list_hex[12:16], base=16)
            CanReceive.ThrottlePoints.append([Time, ThrottlePoint])
        except:
            return

    def ID_Misc_Controller(self, ID_A, msg_id_bin, data_bin, data_list_hex):
        ControllerID = (round(ID_A, -2)-1000)//100
        ControllerIndex = ID_A % 100
        if len(data_list_hex) == 16:
            
            if ID_A == 1502 or ID_A == 1504:
                value_1 = ba2int(bitarray(data_bin[0:32]), signed = True)
                CanReceive.Controllers[ControllerID][ControllerIndex] = value_1
                value_2 = ba2int(bitarray(data_bin[32:64]), signed = True)
                CanReceive.Controllers[ControllerID][ControllerIndex + 1] = value_2
            elif ControllerIndex == 14 or ControllerIndex == 15:
                value_1 = int(data_bin[0:32],2)
                CanReceive.Controllers[ControllerID][ControllerIndex] = value_1
                value_2 = int(data_bin[32:64],2)
                CanReceive.Controllers[ControllerID][ControllerIndex + 1] = value_2
            else:
                value_1 = int(data_bin[0:32],2)
                value_1 = struct.unpack('f', struct.pack('I', value_1))[0]
                CanReceive.Controllers[ControllerID][ControllerIndex] = value_1
                value_2 = int(data_bin[32:64],2)
                value_2 = struct.unpack('f', struct.pack('I', value_2))[0]
                CanReceive.Controllers[ControllerID][ControllerIndex + 1] = value_2
        else:
            
            value_1 = int(data_bin[0:32],2)
            value_1 = struct.unpack('f', struct.pack('I', value_1))[0]
            CanReceive.Controllers[ControllerID][ControllerIndex] = value_1



