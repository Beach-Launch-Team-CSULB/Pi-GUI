import can
import bitstring
from bitarray.util import ba2int
from bitarray import bitarray


class ValveDevice:  # Represents a valve logically
    valve_id: int = 0
    valve_state: int = 0

    def __init__(self, vid, state):
        self.valve_id = vid
        self.valve_state = state


class ValveNodeState:  # Represents a valve node logically, parses data
    id: int = 0  # ID of the node
    state = "Default State"  # String to represent current state node is in, looked up from node_state_arr
    autosequence: bool = False  # Autosequence bool
    valve_enable = []  # List of 3 valve enable bools
    valves = []  # List of ValveDevice objects to represent the valve states of each node

    node_state_arr = ("Debug Mode",
                      "Passivated State",
                      "Test State",
                      "Abort State",
                      "Vent State",
                      "Hi-Press Press Arm State",
                      "Hi-Press Pressurize State",
                      "Tank Press Arm State",
                      "Tank Press State",
                      "Fire Arm State",
                      "Fire State")

    valve_state_arr = ((), (), ("HP", "HPV", "LMV", "FMV"),
                       ("LV", "LDR", "LDV", "FV", "FDR", "FDV"))

    def __init__(self, id_value=None, can_message=None):
        self.id = id_value
        # state = int(can_message[0][0], 16)
        if id_value is None and can_message is None:
            self.id = 0
            self.state = "Default State"
            self.autosequence = False
        else:
            state_num = ba2int(bitarray(can_message[0:4]))
            if state_num > 7:
                self.state = str(state_num)
            else:
                self.state = self.node_state_arr[ba2int(bitarray(can_message[0:4]))]
            self.valve_enable = can_message[4:7]
            self.autosequence = can_message[7]
            for i in range(8, len(can_message), 8):
                valve_id = ba2int(bitarray(can_message[i:i + 5]))
                valve_state = ba2int(bitarray(can_message[i + 5:i + 8]))
                valve = ValveDevice(valve_id, valve_state)
                self.valves.append(valve)


class CanReceive:
    Sensors = [0] * 2048
    valve_state_arr = ((), (), ("HP", "HPV", "LMV", "FMV"),
                       ("LV", "LDR", "LDV", "FV", "FDR", "FDV"))
    node_name_arr = ("PadGroundNode", "UpperPropNode")
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
    node_dict_list = {node_name_arr[0]:  {"id": "0", "state": "Default State"},
                      node_name_arr[1]: {"id": "0", "state": "Default State"}}
    prop_node_dict = {"id": "0", "state": "Default State"}
    upper_prop_node_dict = {"id": "0", "state": "Default State"}
    node_state = {}

    def __init__(self):
        self.loop = True

    def run(self):
        bus_type = 'socketcan'
        channel0 = 'can0'
        # noinspection PyTypeChecker
        bus_receive = can.interface.Bus(channel=channel0, bustype=bus_type)
        while self.loop:
            msg_in = bus_receive.recv(timeout=None)
            data_list_hex = msg_in.data.hex()
            data_bin = bitstring.BitArray(hex=data_list_hex).bin
            msg_id = msg_in.arbitration_id
            value = int(data_list_hex[0:4], base=16)
            print(value)
            CanReceive.Sensors[msg_id] = value
            if msg_id == 2 or msg_id == 3:  # Prop Node state report logic
                node_data = ValveNodeState(msg_id, data_bin)
                self.node_dict_list[self.node_name_arr[msg_id-2]]["id"] = node_data.id
                self.node_dict_list[self.node_name_arr[msg_id-2]]["state"] = node_data.state
                for i in node_data.valves:
                    if i.valve_id > len(self.valve_state_arr[msg_id]):
                        node_name = int(str(msg_id) + str(i.valve_id))
                    else:
                        node_name = self.valve_state_arr[msg_id][i.valve_id]
                    self.node_state[node_name] = i.valve_state
#             if datalist:
#                 print(data)

#             ssdatalist = datalist[6:-2]
#             data = ""

#             for num in datalist:
#                 print(num)
#                 print(str(decimalToBinary(int(num))))
#                 data = "".join([data, str(decimalToBinary(int(num)))])  
#                 print(data)
