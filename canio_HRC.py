import can
import bitstring
from bitarray.util import ba2int
from bitarray import bitarray
import time
import struct
from lint import docstring
import config_HRC as HRC

################################################################################
################################### Can Send ###################################
################################################################################

def isfloat(x):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b

def intTypeCheck(var, type, label, size):
    num = var.get()

    buffer = {
        int:   ( isint,   lambda val: dict(int=val),  "Integer Number" ),
        float: ( isfloat, lambda val: dict(float=val), "Decimal Value" )
    }

    if type not in buffer:
        return False
    
    check, bitarrArg, errString = buffer[type]
    
    try:
        if not check(num):
            label.config(text="Invalid Type.\n%s is required as Input"%errString, fg="red")
            return False
        
        binstr = bitstring.BitArray(length=size, **bitarrArg(type(num))).bin
        label.config(text="Command Sent!", fg="green")
        return True
    except bitstring.CreationError as e:
        label.config(text=e, fg="red")
        return False

class CanSend:
    def __init__(self, canReceive, **busargs):
        print("Hericlitus Rocket Controller CanSend instance created")
        self.bus = can.interface.Bus(**busargs)
        self.canReceive = canReceive
        # DEBUG
        # self._test = True

    def send(self, ID, DATA, prefix=""):
        self.canReceive.outgoing_message_ids[ID] = True
        print(">>", prefix, ID, DATA)
        msg = can.Message(arbitration_id=ID, data=DATA, is_extended_id=False)
        self.bus.send(msg)

    def __call__(self, ID, DATA):
        self.send(ID, DATA)

    # def TEST_send_state_reports(self, canRecieve):
    #     
    #     if not self._test:
    #         return 
    #     self._test = False
    #     
    #     def split(hexes):
    #         hexes = hexes.replace(' ','')
    #         return [int('0'+hexes[h:h+2], base=16) for h in range(0, len(hexes), 2)]
    #     
    #     # State reports
    #     self.send(HRC.SR_ENGINE, split("00 01 8B CD 07 25"), "sent STATE REPORT engine:")
    #     self.send(HRC.SR_PROP,   split("00 01 8B CD 07 38"), "sent STATE REPORT prop:")
    #     
    #     # Sensor readings for all four groups
    #     self.send(HRC.SENS_1_4_PROP,     split("1A 2C 19 C8 06 A4 06 40"), "sent SENSOR READING 01 - 04:")
    #     self.send(HRC.SENS_5_8_PROP,     split("0C E4 19 64 0D AC 19 00"), "sent SENSOR READING 05 - 08:")
    #     self.send(HRC.SENS_9_12_ENGINE,  split("0D 48 19 C8 1A 2C 0C E4"), "sent SENSOR READING 09 - 12:")
    #     self.send(HRC.SENS_13_16_ENGINE, split("19 00 19 64 00 00 00 00"), "sent SENSOR READING 12 - 16:")
    #     
    #     print(canRecieve._stdio)

    ##############################
    ########## Generics ##########
    ##############################
    #     These functions are    #
    # commonly used throughout   #
    # the rest of CanSend. All   #
    # other functions are for    #
    # your convinience, and      #
    # derive from these.         #
    
    @docstring("""
    # Sets the timing for the target id.
    # 
    # Arguments:
    # id: Message id -- Setters in range [32, 36].
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_timing(self, ID, time_micros):
        binstr = bitstring.BitArray(int=time_micros, length=32).bin
        data = [int('0'+binstr[i:i+8],base=2) for i in range(0, len(binstr), 8)]
        self.send(ID, data, "Sent Timer Message:")

        # DEBUG
        # Echoes the timing to CanRecieve for testing.
        # rev = {v:k for k,v in HRC.TimingLUT.items()}
        # self.send(rev[ID], data, "Echo Timer Message:")

    @docstring("""
    # Sends a unary message.
    # 
    # Arguments:
    # id: Command id -- Defined in Config.h
    """)
    def send_unary_message(self, ID):
        self.send(ID, [], "Sent Unary Message:")
        

    ##############################
    ###### Vehicle Commands ######
    ##############################
        
    @docstring("""
    # Sends the abort command.
    """)
    def abort(self):
        self.send_unary_message(HRC.ABORT)

    @docstring("""
    # Sends the vent command.
    """)
    def vent(self):
        self.send_unary_message(HRC.VENT)

    @docstring("""
    # Sends the fire command.
    """)
    def fire(self):
        self.send_unary_message(HRC.FIRE)

    @docstring("""
    # Sends the tank pressurize command.
    """)
    def tank_press(self):
        self.send_unary_message(HRC.TANK_PRESS)

    @docstring("""
    # Sends the high press pressurize command.
    """)
    def high_press(self):
        self.send_unary_message(HRC.HIGH_PRESS)

    @docstring("""
    # Sends the standby command.
    """)
    def standby(self):
        self.send_unary_message(HRC.STANDBY)

    @docstring("""
    # Sends the ignite command.
    """)
    def ignite(self):
        self.send_unary_message(HRC.IGNITE)

    @docstring("""
    # Sends the test command.
    """)
    def test(self):
        self.send_unary_message(HRC.TEST)

    ##############################
    ##### Valves & Igniters ######
    ##############################
        
    @docstring("""
    # Sets Igniter 1 to off.
    """)
    def ign1_off(self):
        self.send_unary_message(HRC.IGN1_OFF)


    @docstring("""
    # Sets Igniter 1 to on.
    """)
    def ign1_on(self):
        self.send_unary_message(HRC.IGN1_ON)


    @docstring("""
    # Sets Igniter 2 to off.
    """)
    def ign2_off(self):
        self.send_unary_message(HRC.IGN2_OFF)


    @docstring("""
    # Sets Igniter 2 to on.
    """)
    def ign2_on(self):
        self.send_unary_message(HRC.IGN2_ON)


    @docstring("""
    # Sets High Pressure Vent to close.
    """)
    def hv_close(self):
        self.send_unary_message(HRC.HV_CLOSE)


    @docstring("""
    # Sets High Pressure Vent open.
    """)
    def hv_open(self):
        self.send_unary_message(HRC.HV_OPEN)


    @docstring("""
    # Sets High Pressure to close.
    """)
    def hp_close(self):
        self.send_unary_message(HRC.HP_CLOSE)


    @docstring("""
    # Sets High Pressure to open.
    """)
    def hp_open(self):
        self.send_unary_message(HRC.HP_OPEN)


    @docstring("""
    # Sets Liquid Oxygen Dome Vent to close.
    """)
    def ldv_close(self):
        self.send_unary_message(HRC.LDV_CLOSE)


    @docstring("""
    # Sets Liquid Oxygen Dome Vent to open.
    """)
    def ldv_open(self):
        self.send_unary_message(HRC.LDV_OPEN)


    @docstring("""
    # Sets Fuel Dome Vent to close.
    """)
    def fdv_close(self):
        self.send_unary_message(HRC.FDV_CLOSE)


    @docstring("""
    # Sets Fuel Dome Vent to open.
    """)
    def fdv_open(self):
        self.send_unary_message(HRC.FDV_OPEN)


    @docstring("""
    # Sets Liquid Oxygen Dome Regulator to close.
    """)
    def ldr_close(self):
        self.send_unary_message(HRC.LDR_CLOSE)


    @docstring("""
    # Sets Liquid Oxygen Dome Regulator to open.
    """)
    def ldr_open(self):
        self.send_unary_message(HRC.LDR_OPEN)


    @docstring("""
    # Sets Fuel Dome Regulator to close.
    """)
    def fdr_close(self):
        self.send_unary_message(HRC.FDR_CLOSE)


    @docstring("""
    # Sets Fuel Dome Regulator to open.
    """)
    def fdr_open(self):
        self.send_unary_message(HRC.FDR_OPEN)


    @docstring("""
    # Sets Liquid Oxygen Vent to close.
    """)
    def lv_close(self):
        self.send_unary_message(HRC.LV_CLOSE)


    @docstring("""
    # Sets Liquid Oxygen Vent to open.
    """)
    def lv_open(self):
        self.send_unary_message(HRC.LV_OPEN)


    @docstring("""
    # Sets Fuel Vent to close.
    """)
    def fv_close(self):
        self.send_unary_message(HRC.FV_CLOSE)


    @docstring("""
    # Sets Fuel Vent to open.
    """)
    def fv_open(self):
        self.send_unary_message(HRC.FV_OPEN)


    @docstring("""
    # Sets Liquid Oxygen Main Valve to close.
    """)
    def lmv_close(self):
        self.send_unary_message(HRC.LMV_CLOSE)


    @docstring("""
    # Sets Liquid Oxygen Main Valve to open.
    """)
    def lmv_open(self):
        self.send_unary_message(HRC.LMV_OPEN)


    @docstring("""
    # Sets Fuel Main Valve to close.
    """)
    def fmv_close(self):
        self.send_unary_message(HRC.FMV_CLOSE)


    @docstring("""
    # Sets Fuel Main Valve to open.
    """)
    def fmv_open(self):
        self.send_unary_message(HRC.FMV_OPEN)

    ##############################
    ########### Timing ###########
    ##############################

    @docstring("""
    # Sets the ignition time for both igniters.
    # 
    # Arguments:
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_ignition(self, time_micros):
        self.set_timing(HRC.SET_IGNITION, time_micros)

    @docstring("""
    # Sets the opening time for the liquid oxygen main valve.
    # 
    # Arguments:
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_lmv_open(self, time_micros):
        self.set_timing(HRC.SET_LMV_OPEN, time_micros)

    @docstring("""
    # Sets the opening time for the fuel main valve.
    # 
    # Arguments:
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_fmv_open(self, time_micros):
        self.set_timing(HRC.SET_FMV_OPEN, time_micros)

    @docstring("""
    # Sets the closing time for the liquid oxygen main valve.
    # 
    # Arguments:
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_lmv_close(self, time_micros):
        self.set_timing(HRC.SET_LMV_CLOSE, time_micros)

    @docstring("""
    # Sets the closing time for the fuel main valve.
    # 
    # Arguments:
    # time_micros: unsigned 32 bit integer -- microsecond delay from fire command.
    """)
    def set_fmv_close(self, time_micros):
        self.set_timing(HRC.SET_FMV_CLOSE, time_micros)

    ##############################
    ####### Miscellaneous ########
    ##############################
        
    @docstring("""
    # Pings the rocket.
    """)
    def ping(self):
        self.send_unary_message(HRC.PING_PI_ROCKET)

    @docstring("""
    # Zeros the pressure transducers.
    """)
    def zero_pts(self):
        self.send_unary_message(HRC.ZERO_PTS)

    def manual_override_toggle(self):
        self.send_unary_message(HRC.MANUAL_OVERRIDE)

    def getDefaultTiming(self):
        self.send_unary_message(HRC.GET_IGNITION)
        self.send_unary_message(HRC.GET_LMV_OPEN)
        self.send_unary_message(HRC.GET_FMV_OPEN)
        self.send_unary_message(HRC.GET_LMV_CLOSE)
        self.send_unary_message(HRC.GET_FMV_CLOSE)
    
    def get_calibration_values(self, SENSOR_ID, var):
        ID = [HRC.GET_M_VALUE, HRC.GET_B_VALUE][var]
        binstr = bitstring.BitArray(int=SENSOR_ID, length=8 ).bin
        data = [int('0'+binstr[i:i+8],base=2) for i in range(0, len(binstr), 8)]
        self.send(ID, data, "Get Calibration Values:")

    def set_calibration_values(self, SENSOR_ID, var, val):
        ID = [HRC.SET_M_VALUE, HRC.SET_B_VALUE][var]
        binstr_s = bitstring.BitArray(int=SENSOR_ID, length=8 ).bin
        binstr_v = bitstring.BitArray(float=val,     length=32).bin
        binstr = binstr_s + binstr_v
        data = [int('0'+binstr[i:i+8],base=2) for i in range(0, len(binstr), 8)]
        self.send(ID, data, "Set Calibration Values:")

    def start_data_logging(self):
        self.send_unary_message(HRC.DATA_LOGGING)

################################################################################
################################# Can Receive ##################################
################################################################################

class CanReceive:

    def __init__(self, **busargs):
        print("Hericlitus Rocket Controller CanReceive instance created")
        self.bus = can.interface.Bus(**busargs)

        self.States = {k:v['states'][0] for k,v in HRC.ToggleLUT.items()}
        self.Sensor_Raw = {k:0 for k,v in HRC.SensorLUT.items()}
        self.Sensor_Val = {k:v['b'] for k,v in HRC.SensorLUT.items()}

        self.rocketState = {k:HRC.STANDBY for k in HRC.ToggleKeys.keys()}
        self.time_micros = {k:-1 for k in HRC.ToggleKeys.keys()}

        self.timingLUT_micros = {k:-1 for k in HRC.TimingLUT.keys()}

        t0 = time.time_ns() / 1000
        self.timeLastRecievedPing_micros = {k:t0 for k in HRC.ToggleKeys.keys()}

        self.outgoing_message_ids = {}

        self.emaBeta = 0.9
        
        # DEBUG
        # self._stdio = ""

    # def Print(self, s):
    #     self._stdio += s + '\n'

    @docstring("""
    Runs the CanReceive thread.
    """)
    def run(self):
        self.loop = True

        import numpy as np

        timeout = None
        while self.loop:
            # DEBUG
            # timeout = 0.1

            self.cycle(timeout=timeout)

            # DEBUG
            # for key in HRC.SensorLUT:
            #     v = int(np.random.random()*100)
            #     self.Sensor_Raw[key] = v
            #     self.Sensor_Val[key] = HRC.SensorLUT[key]['b'] + HRC.SensorLUT[key]['m'] * v
            # for key, val in HRC.ToggleLUT.items():
            #     self.States[key] = np.random.choice(val['states'])
            # #time.sleep(0.1)

    @docstring("""
    Runs a single message loop cycle.
    """)
    def cycle(self, timeout=None):
        msg_in = self.bus.recv(timeout=timeout)
        
        if msg_in is None:
            return
        
        try:
            self.translateMessage(*self.parseMessage(msg_in))
        except Exception as e:
            print(e)
            

    @docstring("""
    # Parses a message recieved by the Can Bus.
    # Returns message id as an integer, and the data in hex and binary formats.
    # 
    # Arguments:
    # msg_in: Can message
    """)
    def parseMessage(self, msg_in):
        # Grabs Message ID
        msg_id = int(msg_in.arbitration_id)
        
        # Grabs the data in the msg
        data_list_hex = msg_in.data.hex()
        data_list_hex = [data_list_hex[h:h+2] for h in range(0, len(data_list_hex), 2)]
        #data_list_hex = list(reversed(data_list_hex))
        data_bin = bitstring.BitArray(hex=''.join(data_list_hex)).bin
        
        return msg_id, data_list_hex, data_bin
    
    @docstring("""
    # Passes the parsed message to the appropriate decoder.
    """)
    def translateMessage(self, msg_id, data_list_hex, data_bin):

        # self.Print("\nMessage Recieved with id: %d"%msg_id)

        if msg_id in HRC.ToggleKeys:
            return self.recvStateReport(msg_id, data_list_hex, data_bin)
        
        if msg_id in HRC.SensorKeys:
            return self.recvSensorData(msg_id, data_list_hex, data_bin)
        
        if msg_id in self.timingLUT_micros:
            return self.recvTiming(msg_id, data_list_hex, data_bin)
        
        if msg_id in [HRC.PING_PROP_PI, HRC.PING_ENGINE_PI]:
            return self.recvPing(msg_id, data_list_hex, data_bin)
        
        if msg_id in [HRC.SEND_M_VALUE, HRC.SEND_B_VALUE]:
            return self.recvCalibrationValues(msg_id, data_list_hex, data_bin)

        if msg_id in self.outgoing_message_ids:
            return

        # DEBUG
        # for state_id, lut in HRC.ToggleLUT.items():
        #     if msg_id in lut['states']:
        #         time.sleep(1)
        #         s = self.States[state_id]
        #         self.States[state_id] = msg_id
        #         raise KeyError("Recieved msg with id: %s, altering %s"%(msg_id, s))
        #         return 

        raise KeyError("Unknown message recieved with id: %d, and data [%s]"%(msg_id, str(data_list_hex)))

    @docstring("""
    # State report
    """)
    def recvStateReport(self, msg_id, data_list_hex, data_bin):
        # self.Print(f"{data_list_hex = }")

        self.time_micros[msg_id] = int('0'+data_bin[:32], base=2)
        self.rocketState[msg_id] = int('0'+data_list_hex[4], base=16)
        # self.Print(f"{self.rocketState[msg_id] = }")

        state_bits = '{0:06b}'.format(int('0'+data_list_hex[5], base=16))
        states = list(map(lambda b: int('0'+b, base=2), state_bits))

        # self.Print(f"{data_list_hex[5] = }")
        # self.Print(f"{(state_bits, states) = }")

        for key, state in zip(HRC.ToggleKeys[msg_id], states):
            self.States[key] = HRC.ToggleLUT[key]['states'][state]

    @docstring("""
    # Sensor data
    """)
    def recvSensorData(self, msg_id, data_list_hex, data_bin):

        vals = [int('0'+data_bin[i:i+16], base=2) for i in range(0, 64, 16)]

        for key, val in zip(HRC.SensorKeys[msg_id], vals):
            if key not in HRC.SensorLUT:
                continue
            
            v = val / HRC.SENSOR_MULTIPLIER

            v = self.Sensor_Raw[key]*self.emaBeta + (1.0-self.emaBeta)*v

            self.Sensor_Raw[key] = v
            self.Sensor_Val[key] = HRC.SensorLUT[key]['b'] + HRC.SensorLUT[key]['m'] * v

    @docstring("""
    # Timing replies.
    # 
    # 32 bit unix epoch nanosecond timestamp.
    """)
    def recvTiming(self, msg_id, data_list_hex, data_bin):

        timestamp = int('0'+''.join(data_bin), base=2)
        self.timingLUT_micros[msg_id] = timestamp/1000

    @docstring("""
    # Ping reply.
    """)
    def recvPing(self, msg_id, data_list_hex, data_bin):
        lut = {
            HRC.PING_PROP_PI:   HRC.SR_PROP,
            HRC.PING_ENGINE_PI: HRC.SR_ENGINE,
        }
        self.timeLastRecievedPing_micros[lut[msg_id]] = time.time_ns() / 1000

    def recvCalibrationValues(self, msg_id, data_list_hex, data_bin):
        sensor_id = int('0'+data_bin[:8], base=2)
        val = bitstring.BitArray(bin='0'+data_bin[8:][:32], length=32).float
        key = {HRC.SEND_M_VALUE:'m', HRC.SEND_B_VALUE:'b'}[msg_id]
        HRC.SensorLUT[sensor_id][key] = val
        