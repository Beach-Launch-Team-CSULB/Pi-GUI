import can


# Function to convert Decimal number
# to Binary number
def decimalToBinary(n):
    return "{0:b}".format(int(n))


class ValveDevice:
    valve_id: int = 0
    valve_state: int = 0

    def __init__(self, vid, state):
        self.valve_id = vid
        self.valve_state = state


class ValveNodeState:
    id: int = 0
    state = "Default State"
    autosequence: bool = False
    valve_enable = []
    valves = []
    valve_state_arr = ["Closed", "Open", "Fire Sent", "Open Sent", "Close Sent", "Open Process",
                       "Closed Process", "Valve State Size"]

    def __init__(self, id_value=None, can_message=None):
        self.id = id_value
        # state = int(can_message[0][0], 16)
        if id_value is None and can_message is None:
            self.id = 0
            self.state = "Default State"
            self.autosequence = False
        else:
            can_bit_array = CanMessageToBitArray(can_message)
            state_num = BitArrayToDec(can_bit_array[0:4])
            if state_num > 7:
                self.state = str(state_num)
            else:
                self.state = self.valve_state_arr[BitArrayToDec(can_bit_array[0:4])]
            self.valve_enable = can_bit_array[4:7]
            self.autosequence = can_bit_array[7]
            for i in range(8, len(can_bit_array), 8):
                valve_id = BitArrayToDec(can_bit_array[i:i + 5])
                valve_state = BitArrayToDec(can_bit_array[i + 5:i + 8])
                valve = ValveDevice(valve_id, valve_state)
                self.valves.append(valve)


def CanMessageToBitArray(can_msg):
    bin_translator = [
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 0, 0],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
        [1, 1, 1, 1]
    ]
    out_arr = []
    for i in can_msg:
        for j in i:
            bin_nums = bin_translator[int(j, base=16)]
            for k in bin_nums:
                out_arr.append(k == 1)
    return out_arr


def BitArrayToDec(inp_array):
    out_num = 0
    pow_val = 0
    for i in reversed(inp_array):
        if i:
            out_num += 2 ** pow_val
        pow_val += 1
    return out_num


class CanRecieve:
    update_values = True
    Sensors = [0] * 2048
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
    prop_node_dict = {"id": "0", "state": "Default State"}
    upper_prop_node_dict = {"id": "0", "state": "Default State"}

    def __init__(self):
        self.loop = True

    def update_value_false(self):
        self.update_values = False

    def run(self):
        self.update_values = True
        bustype = 'socketcan'
        channel0 = 'can0'
        print("hi")
        busReceive = can.interface.Bus(channel=channel0, bustype=bustype)
        while self.loop:
            msgIn = busReceive.recv(timeout=None)
            data = str(msgIn)
            datalist = data.split()
            actualData = datalist[7:14]
            ID = int(datalist[3], base=16)
            value = int(actualData[0] + actualData[1], base=16)
            print(value)
            CanRecieve.Sensors[ID] = value
            if ID == 2:  # Prop Node state report logic
                print("Prop Node")
                node_data = ValveNodeState(ID, actualData)
                self.prop_node_dict["id"] = str(node_data.id)
                self.prop_node_dict["state"] = node_data.state
            if ID == 3:  # Upper Prop state report logic
                print("Upper Prop Node")
                node_data = ValveNodeState(ID, actualData)
                self.upper_prop_node_dict["id"] = str(node_data.id)
                self.upper_prop_node_dict["state"] = node_data.state
#             if datalist:
#                 print(data)

#             datalist = datalist[6:-2]
#             data = ""

#             for num in datalist:
#                 print(num)
#                 print(str(decimalToBinary(int(num))))
#                 data = "".join([data, str(decimalToBinary(int(num)))])  
#                 print(data)
