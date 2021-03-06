import can
import bitstring
from bitarray.util import ba2int
from bitarray import bitarray
import time


class ValveDevice:  # Represents a valve logically
    valve_id: int = 0
    valve_state: int = 0

    def __init__(self, vid, state):
        self.valve_id = vid
        self.valve_state = state


class ValveNodeState:  # Represents a valve node logically, parses data
    id: int = 0  # ID of the nodeHV Does not exist
    state = "Default State"  # String to represent current state node is in, looked up from node_state_arr
    autosequence: bool = False  # Autosequence bool
    valve_enable = []  # List of 3 valve enable bools
    valves = []  # List of ValveDevice objects to represent the valve states of each node

    node_state_arr = ("Setup",
                      "Debug Mode",
                      "Passivated State",
                      "Test State",
                      "Abort State",
                      "Vent State",
                      "Manual Override",
                      "Hi-Press Press Arm State",
                      "Hi-Press Pressurize State",
                      "Tank Press Arm State",
                      "Tank Press State",
                      "Fire Arm State",
                      "Fire State")

    def __init__(self, id_value=None, can_message=None):
        self.id = id_value
        # state = int(can_message[0][0], 16)
        if id_value is None and can_message is None:
            self.id = 0
            self.state = "Default State"
        else:
            state_num = ba2int(bitarray(can_message[4:8]))
            if state_num > len(self.node_state_arr):
                self.state = str(state_num)
            else:
                self.state = self.node_state_arr[state_num]
            self.valve_enable = can_message[0:4]
            for i in range(8, len(can_message), 8):
                valve_id = ba2int(bitarray(can_message[i + 3:i + 8]))
                valve_state = ba2int(bitarray(can_message[i:i + 3]))
                valve = ValveDevice(valve_id, valve_state)
                self.valves.append(valve)


class CanReceive:
    startTime = 0
    currRefTime = startTime
    firstNodeTime = 0
    Sensors = [0] * 2048
    sensorTimestamps = [0] * 2048
    valve_state_arr = ((), (), ("HP", "HPV", "LMV", "FMV"),
                       ("LV", "LDR", "LDV", "FV", "FDR", "FDV"))
    autosequence_state_arr = ("Standby", "RunCommanded", "Running", "Hold")
    node_name_arr = ("PadGroundNode", "UpperPropNode", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Pasafire", 0, 0, 0, 0, 0, 0)
    seconds_timer = 0
    millis_timer = 0
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
    node_dict_list = {node_name_arr[0]: {"id": "0", "state": "Default State"},
                      node_name_arr[1]: {"id": "0", "state": "Default State"},
                      node_name_arr[13]: {"id": "0", "state": "Default State"}}
    prop_node_dict = {"id": "0", "state": "Default State"}
    upper_prop_node_dict = {"id": "0", "state": "Default State"}
    node_state = {}
    autosequence = {"state": "0", "time": "0"}

    def __init__(self):
        self.loop = True

    def run(self):
        bus_type = 'socketcan'
        channel0 = 'can0'
        # noinspection PyTypeChecker
        bus_receive = can.interface.Bus(channel=channel0, bustype=bus_type)
        while self.loop:
            msg_in = bus_receive.recv(timeout=None)
            # msg_in_1 = bus_receive_1.recv(timeout=None)
            if CanReceive.startTime == 0:
                CanReceive.startTime = time.time()
                # CanReceive.firstNodeTime = 9
            # currRefTime = time.time()-CanReceive.startTime + CanReceive.firstNodeTime
            data_list_hex = msg_in.data.hex()
            # data_list_hex_1 = msg_in_1.data.hex()
            if data_list_hex[0:4] == '':
                continue
            data_bin = bitstring.BitArray(hex=data_list_hex).bin
            msg_id = int(msg_in.arbitration_id)
            #             data_bin_1 = bitstring.BitArray(hex=data_list_hex_1).bin
            #             msg_id_1 = extended_id_1
            #             print(msg_id_1, bin_id_1[0:11])
            seconds = 0
            millis = 0
            if len(data_list_hex) >= 4:
                CanReceive.Sensors[msg_id] = int(data_list_hex[0:2], base=16) + int(data_list_hex[2:4], base=16) * 255
            if len(msg_in.data) >= 2:
                seconds = msg_in.data[2]
            if len(data_list_hex) >= 9:
                millis = int(data_list_hex[6:8], base=16) + int(data_list_hex[8:10], base=16)
            CanReceive.sensorTimestamps[msg_id] = seconds + (millis * 0.001)
            if msg_id == 2 or msg_id == 3 or msg_id == 15 or msg_id == 31:  # Prop Node state report logic
                node_data = ValveNodeState(msg_id, data_bin)
                try:
                    self.node_dict_list[self.node_name_arr[msg_id - 2]]["id"] = node_data.id
                except:
                    continue
                self.node_dict_list[self.node_name_arr[msg_id - 2]]["state"] = node_data.state
                for i in node_data.valves:
                    self.node_state[i.valve_id] = i.valve_state
                # print()
            elif msg_id == 34 or msg_id == 47:
                # print("Autosequence!")
                state_byte = int(msg_in.data[0])
                self.autosequence['state'] = str(state_byte)
                if str(state_byte < len(self.autosequence_state_arr)):
                    self.autosequence['state'] = self.autosequence_state_arr[state_byte]
                self.autosequence['time'] = \
                    str(float(int.from_bytes(msg_in.data[1:8], byteorder='little', signed=True)) / 1000000.0)
            # print(self.autosequence['state'])
            # print(self.autosequence['time'])
#             if datalist:
#                 print(data)

#             ssdatalist = datalist[6:-2]
#             data = ""

#             for num in datalist:
#                 print(num)
#                 print(str(decimalToBinary(int(num))))
#                 data = "".join([data, str(decimalToBinary(int(num)))])  
#                 print(data)
