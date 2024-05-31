
NODEID = 8
VERIFICATIONID = 166
SENSOR_MULTIPLIER = 1

################################################################################
####################### pins_arduino.h / Pin Definitions #######################
################################################################################

PinLUT = {
     "A0":14,  "A1":15,  "A2":16,  "A3":17,  "A4":18, 
     "A5":19,  "A6":20,  "A7":21,  "A8":22,  "A9":23,

    "A10":64, "A11":65, "A12":31, "A13":32, "A14":33,
    "A15":34, "A16":35, "A17":36, "A18":37, "A19":38,
    "A20":39, "A21":66, "A22":67, "A23":49, "A24":50,
    "A25":68, "A26":69,
}

################################################################################
############## HeraclitusRocketController / Config.h Definitions ###############
################################################################################

# Valves & Igniters
NUM_VALVES   = 10
NUM_IGNITERS = 2

# Vehicle Commands
ABORT        = 0
VENT         = 1
FIRE         = 2
TANK_PRESS   = 3
HIGH_PRESS   = 4
STANDBY      = 5
IGNITE       = 6
TEST         = 7

# Valve & Igniter (HPO Commands)
IGN1_OFF     = 8   # Igniter One
IGN1_ON      = 9

IGN2_OFF     = 10  # Igniter Two
IGN2_ON      = 11

HV_CLOSE     = 12  # High Vent valve
HV_OPEN      = 13

HP_CLOSE     = 14  # High Press valve
HP_OPEN      = 15

LDV_CLOSE    = 16  # Lox Dome Vent valve
LDV_OPEN     = 17

FDV_CLOSE    = 18  # Fuel Dome Vent valve
FDV_OPEN     = 19

LDR_CLOSE    = 20  # Lox Dome Reg valve
LDR_OPEN     = 21

FDR_CLOSE    = 22  # Fuel Dome Reg valve
FDR_OPEN     = 23

LV_CLOSE     = 24  # Lox Vent valve
LV_OPEN      = 25

FV_CLOSE     = 26  # Fuel Vent valve
FV_OPEN      = 27

LMV_CLOSE    = 28  # Lox Main valve
LMV_OPEN     = 29

FMV_CLOSE    = 30  # Fuel Main valve
FMV_OPEN     = 31

# Timing
SET_IGNITION  = 32  # Set ignition time for both igniters.
SET_LMV_OPEN  = 33  # Set LMV open time.
SET_FMV_OPEN  = 34  # Set FMV open time. 
SET_LMV_CLOSE = 35  # Set LMV close time.
SET_FMV_CLOSE = 36  # Set FMV close time.

GET_IGNITION  = 37  # Pi Box requests ignition time for both igniters.
GET_LMV_OPEN  = 38  # Pi Box requests LMV open time.
GET_FMV_OPEN  = 39  # Pi Box requests FMV open time.
GET_LMV_CLOSE = 40  # Pi Box requests LMV close time.
GET_FMV_CLOSE = 41  # Pi Box requests FMV close time.

# Ping
PING_PI_ROCKET = 42  # *Important*: Pi Box sends a ping to the rocket. 

# Reserved
MANUAL_OVERRIDE = 43 # TODO: WRITE WHAT THIS DOES

# PT Configuration
ZERO_PTS                = 44  # Zero the pressure transducers.

GET_M_VALUE = 45  # Adjust "m value" of linear approximation for PTs.
SET_M_VALUE = 46
GET_B_VALUE = 47
SET_B_VALUE = 48
DATA_LOGGING = 49 # Sends command to start data logging on SD cards

# State Reports
SR_PROP   = 127
SR_ENGINE = 128

# Sensor Reports
SENS_1_4_PROP     = 129 # Lox High,   Fuel High, Lox Dome,   Fuel Dome
SENS_5_8_PROP     = 130 # Lox Tank1,  Lox Tank2, Fuel Tank1, Fuel Tank2
SENS_9_12_ENGINE  = 131 # Pneumatics, Lox Inlet, Fuel Inlet, Fuel Injector
SENS_13_16_ENGINE = 132 # Chamber1,   Chamber2,  UNUSED,     UNUSED

# Timing Reports
SEND_IGNITION  = 133 # ALARA response to 37. Sends igniter time for confirmation.
SEND_LMV_OPEN  = 134 # ALARA response to 38. Sends LMV open time for confirmation. 
SEND_FMV_OPEN  = 135 # ALARA response to 39. Sends FMV open time for confirmation.
SEND_LMV_CLOSE = 136 # ALARA response to 40. Sends LMV close time for confirmation.
SEND_FMV_CLOSE = 137 # ALARA response to 41. Sends FMV close time for confirmation.

# Ping Response
PING_PROP_PI   = 138 # Prop node ping response to the PI box.
PING_ENGINE_PI = 139
OP_MSG_PROP    = 140 # Prop node message 
OP_MSG_ENGINE  = 141

# PT Calib. Response to "Get" request from GUI
SEND_M_VALUE   = 142 # ALARA response to 45.
SEND_B_VALUE   = 143 # ALARA response to 47.

# Data Direction Inputs 
INPUT  = 0
OUTPUT = 1

# Igniter Digital Pin Designations and IDs | ALARA LOWER 

IGN1_ID      = 10  # Igniter A / ENG-IGNA / ALARA Lower
IGN1_PIN_DIG = 83  #ALARA: DIG5 | Teensy 3.6 MCU Pin: PTC16
IGN1_PIN_PWM = 2 


IGN2_ID      = 11  # Igniter B / ENG-IGNB
IGN2_PIN_DIG = 81  # ALARA: DIG5 | Teensy 3.6 MCU Pin: PTC14
IGN2_PIN_PWM = 10  # In Dan's Code they are both 2?  
      

# Valve Digital Pin Designations and IDs | ALARA LOWER 

HP_ID        = 20  # High Press valve / SV HI PRES  
HP_PIN_DIG   = 87  # ALARA: DIG1 | Teensy 3.6 MCU Pin: PTD10
HP_PIN_PWM   = 5

HV_ID        = 21  # High Vent valve / SV HI PRES V 
HV_PIN_DIG   = 86  # ALARA: DIG2 | Teensy 3.6 MCU Pin: PTC19
HV_PIN_PWM   = 6

FMV_ID       = 22  # Fuel Main valve / SV MV FUEL 
FMV_PIN_DIG  = 85  # ALARA: DIG3 | Teensy 3.6 MCU Pin: PTC18
FMV_PIN_PWM  = 8  

LMV_ID       = 23  # Lox Main valve / SV MV LOX
LMV_PIN_DIG  = 84  # ALARA: DIG4 | Teensy 3.6 MCU Pin: PTC17
LMV_PIN_PWM  = 7

# Valve Digital Pin Designations and IDs | ALARA UPPER 

LV_ID        = 24  # Lox Vent valve / SV LOX V
LV_PIN_DIG   = 87  # ALARA: DIG1 | Teensy 3.6 MCU Pin: PTD10
LV_PIN_PWM   = 5

LDV_ID       = 25  # Lox Dome Vent valve / SV DREG L
LDV_PIN_DIG  = 85  # ALARA: DIG3 | Teensy 3.6 MCU Pin: PTC18
LDV_PIN_PWM  = 8

LDR_ID       = 26  # Lox Dome Reg valve / SV DREG LV
LDR_PIN_DIG  = 84  # ALARA: DIG4 | Teensy 3.6 MCU Pin: PTC17
LDR_PIN_PWM  = 7

FV_ID        = 27  # Fuel Vent valve / SV FUEL V 
FV_PIN_DIG   = 83  # ALARA: DIG5 | Teensy 3.6 MCU Pin: PTC16
FV_PIN_PWM   = 2

FDV_ID       = 28  # Fuel Dome Vent valve / SV DREG F V 
FDV_PIN_DIG  = 81  # ALARA: DIG7 | Teensy 3.6 MCU Pin: PTC14
FDV_PIN_PWM  = 10

FDR_ID       = 29  # Fuel Dome Reg valve /  SV DREG F
FDR_PIN_DIG  = 80  # ALARA: DIG8 | Teensy 3.6 MCU Pin: PTC13
FDR_PIN_PWM  = 9



# Pressure Transducer Sesnor Pin Designations, IDs, and Calibration Values
# (sensors are currently uncalibrated)

#Upper Prop Node:
PT_LOX_HIGH_ID         = 0  #00000000 00000001  Upper A22
PT_LOX_HIGH_PIN        = "A22"
PT_LOX_HIGH_CAL_M      = 1.0
PT_LOX_HIGH_CAL_B      = 0.0

PT_FUEL_HIGH_ID        = 1  #00000000 00000010  Upper A21
PT_FUEL_HIGH_PIN       = "A21"
PT_FUEL_HIGH_CAL_M     = 1.0
PT_FUEL_HIGH_CAL_B     = 0.0

PT_LOX_DOME_ID         = 2  #00000000 00000100  Upper  A3
PT_LOX_DOME_PIN        = "A3"
PT_LOX_DOME_CAL_M      = 1.0
PT_LOX_DOME_CAL_B      = 0.0

PT_FUEL_DOME_ID        = 3  #00000000 00001000  Upper  A2
PT_FUEL_DOME_PIN       = "A2"
PT_FUEL_DOME_CAL_M     = 1.0
PT_FUEL_DOME_CAL_B     = 0.0

PT_LOX_TANK_1_ID       = 4  #00000000 00010000  Upper A14
PT_LOX_TANK_1_PIN      = "A14"
PT_LOX_TANK_1_CAL_M    = 1.0
PT_LOX_TANK_1_CAL_B    = 0.0

PT_LOX_TANK_2_ID       = 5  #00000000 00100000  Upper A11
PT_LOX_TANK_2_PIN      = "A11"
PT_LOX_TANK_2_CAL_M    = 1.0
PT_LOX_TANK_2_CAL_B    = 0.0

PT_FUEL_TANK_1_ID      = 6  #00000000 01000000  Upper A15
PT_FUEL_TANK_1_PIN     = "A15"
PT_FUEL_TANK_1_CAL_M   = 1.0
PT_FUEL_TANK_1_CAL_B   = 0.0

PT_FUEL_TANK_2_ID      = 7  #00000000 10000000  Upper A10
PT_FUEL_TANK_2_PIN     = "A10"
PT_FUEL_TANK_2_CAL_M   = 1.0
PT_FUEL_TANK_2_CAL_B   = 0.0

#Lower Engine Node:
PT_PNUEMATICS_ID       = 8  #00000001 00000000  Lower A15
PT_PNUEMATICS_PIN      = "A15"
PT_PNUEMATICS_CAL_M    = 1.0
PT_PNUEMATICS_CAL_B    = 0.0

PT_LOX_INLET_ID        = 9  #00000010 00000000  Lower A21
PT_LOX_INLET_PIN       = "A21"
PT_LOX_INLET_CAL_M     = 1.0
PT_LOX_INLET_CAL_B     = 0.0

PT_FUEL_INLET_ID       = 10 #00000100 00000000  Lower A22
PT_FUEL_INLET_PIN      = "A22"
PT_FUEL_INLET_CAL_M    = 1.0
PT_FUEL_INLET_CAL_B    = 0.0

PT_FUEL_INJECTOR_ID    = 11 #00001000 00000000  Lower A14
PT_FUEL_INJECTOR_PIN   = "A14"
PT_FUEL_INJECTOR_CAL_M = 1.0
PT_FUEL_INJECTOR_CAL_B = 0.0

PT_CHAMBER_1_ID        = 12 #00010000 00000000  Lower A10
PT_CHAMBER_1_PIN       = "A10"
PT_CHAMBER_1_CAL_M     = 1.0
PT_CHAMBER_1_CAL_B     = 0.0

PT_CHAMBER_2_ID        = 13 #00100000 00000000  Lower A11
PT_CHAMBER_2_PIN       = "A11"
PT_CHAMBER_2_CAL_M     = 1.0
PT_CHAMBER_2_CAL_B     = 0.0

################################################################################
########################### Convenience Dictionaries ###########################
################################################################################

StateLUT = {
         ABORT: "Abort",
          VENT: "Vent",
          FIRE: "Fire",
    TANK_PRESS: "Tank_press",
    HIGH_PRESS: "High_press",
       STANDBY: "Standby",
        IGNITE: "Ignite",
          TEST: "Test",
}

TimingLUT = {
    SEND_IGNITION:  SET_IGNITION,
    SEND_LMV_OPEN:  SET_LMV_OPEN,
    SEND_FMV_OPEN:  SET_FMV_OPEN,
    SEND_LMV_CLOSE: SET_LMV_CLOSE,
    SEND_FMV_CLOSE: SET_FMV_CLOSE,
}

ToggleLUT = {
    IGN1_ID: dict(node=SR_ENGINE, pin=IGN1_PIN_DIG, pwm=IGN1_PIN_PWM, states=[ IGN1_OFF,  IGN1_ON], statestr=[   "Off",   "On"], nick="IGN 1", name="Igniter 1"),
    IGN2_ID: dict(node=SR_ENGINE, pin=IGN2_PIN_DIG, pwm=IGN2_PIN_PWM, states=[ IGN2_OFF,  IGN2_ON], statestr=[   "Off",   "On"], nick="IGN 2", name="Igniter 2"),
      HP_ID: dict(node=SR_ENGINE, pin=  HP_PIN_DIG, pwm=  HP_PIN_PWM, states=[ HP_CLOSE,  HP_OPEN], statestr=["Closed", "Open"], nick="HP",    name="High Press"),
      HV_ID: dict(node=SR_ENGINE, pin=  HV_PIN_DIG, pwm=  HV_PIN_PWM, states=[ HV_CLOSE,  HV_OPEN], statestr=["Closed", "Open"], nick="HV",    name="High Vent"),
     FMV_ID: dict(node=SR_ENGINE, pin= FMV_PIN_DIG, pwm= FMV_PIN_PWM, states=[FMV_CLOSE, FMV_OPEN], statestr=["Closed", "Open"], nick="FMV",   name="Fuel Main Valve"),
     LMV_ID: dict(node=SR_ENGINE, pin= LMV_PIN_DIG, pwm= LMV_PIN_PWM, states=[LMV_CLOSE, LMV_OPEN], statestr=["Closed", "Open"], nick="LMV",   name="Lox Main Valve"),
      LV_ID: dict(node=SR_PROP,   pin=  LV_PIN_DIG, pwm=  LV_PIN_PWM, states=[ LV_CLOSE,  LV_OPEN], statestr=["Closed", "Open"], nick="LV",    name="Lox Vent"),
     LDV_ID: dict(node=SR_PROP,   pin= LDV_PIN_DIG, pwm= LDV_PIN_PWM, states=[LDV_CLOSE, LDV_OPEN], statestr=["Closed", "Open"], nick="LDV",   name="Lox Dome Vent"),
     LDR_ID: dict(node=SR_PROP,   pin= LDR_PIN_DIG, pwm= LDR_PIN_PWM, states=[LDR_CLOSE, LDR_OPEN], statestr=["Closed", "Open"], nick="LDR",   name="Lox Dome Regulator"),
      FV_ID: dict(node=SR_PROP,   pin=  FV_PIN_DIG, pwm=  FV_PIN_PWM, states=[ FV_CLOSE,  FV_OPEN], statestr=["Closed", "Open"], nick="FV",    name="Fuel Vent"),
     FDV_ID: dict(node=SR_PROP,   pin= FDV_PIN_DIG, pwm= FDV_PIN_PWM, states=[FDV_CLOSE, FDV_OPEN], statestr=["Closed", "Open"], nick="FDV",   name="Fuel Dome Vent"),
     FDR_ID: dict(node=SR_PROP,   pin= FDR_PIN_DIG, pwm= FDR_PIN_PWM, states=[FDR_CLOSE, FDR_OPEN], statestr=["Closed", "Open"], nick="FDR",   name="Fuel Dome Regulator"),
}

ToggleKeys = {
    SR_ENGINE:[HP_ID,  HV_ID, FMV_ID, LMV_ID, IGN1_ID, IGN2_ID],
    SR_PROP:  [LV_ID, LDV_ID, LDR_ID,  FV_ID,  FDV_ID,  FDR_ID]
}

SensorLUT = {
         PT_LOX_HIGH_ID: dict(node=SR_PROP,   pin=     PT_LOX_HIGH_PIN, m=     PT_LOX_HIGH_CAL_M, b=     PT_LOX_HIGH_CAL_B, nick="LH",  name="Lox\nHigh Press",  ),
        PT_FUEL_HIGH_ID: dict(node=SR_PROP,   pin=    PT_FUEL_HIGH_PIN, m=    PT_FUEL_HIGH_CAL_M, b=    PT_FUEL_HIGH_CAL_B, nick="FH",  name="Fuel\nHigh Press", ),
         PT_LOX_DOME_ID: dict(node=SR_PROP,   pin=     PT_LOX_DOME_PIN, m=     PT_LOX_DOME_CAL_M, b=     PT_LOX_DOME_CAL_B, nick="LD",  name="Lox\nDome Reg",    ),
        PT_FUEL_DOME_ID: dict(node=SR_PROP,   pin=    PT_FUEL_DOME_PIN, m=    PT_FUEL_DOME_CAL_M, b=    PT_FUEL_DOME_CAL_B, nick="FD",  name="Fuel\nDome Reg",   ),
       PT_LOX_TANK_1_ID: dict(node=SR_PROP,   pin=   PT_LOX_TANK_1_PIN, m=   PT_LOX_TANK_1_CAL_M, b=   PT_LOX_TANK_1_CAL_B, nick="LT1", name="Lox\nTank 1",      ),
       PT_LOX_TANK_2_ID: dict(node=SR_PROP,   pin=   PT_LOX_TANK_2_PIN, m=   PT_LOX_TANK_2_CAL_M, b=   PT_LOX_TANK_2_CAL_B, nick="LT2", name="Lox\nTank 2",      ),
      PT_FUEL_TANK_1_ID: dict(node=SR_PROP,   pin=  PT_FUEL_TANK_1_PIN, m=  PT_FUEL_TANK_1_CAL_M, b=  PT_FUEL_TANK_1_CAL_B, nick="FT1", name="Fuel\nTank 1",     ),
      PT_FUEL_TANK_2_ID: dict(node=SR_PROP,   pin=  PT_FUEL_TANK_2_PIN, m=  PT_FUEL_TANK_2_CAL_M, b=  PT_FUEL_TANK_2_CAL_B, nick="FT2", name="Fuel\nTank 2",     ),
       PT_PNUEMATICS_ID: dict(node=SR_ENGINE, pin=   PT_PNUEMATICS_PIN, m=   PT_PNUEMATICS_CAL_M, b=   PT_PNUEMATICS_CAL_B, nick="MVP", name="MV\nPneumatic",    ),
        PT_LOX_INLET_ID: dict(node=SR_ENGINE, pin=    PT_LOX_INLET_PIN, m=    PT_LOX_INLET_CAL_M, b=    PT_LOX_INLET_CAL_B, nick="LIN", name="Lox\nProp Inlet",  ),
       PT_FUEL_INLET_ID: dict(node=SR_ENGINE, pin=   PT_FUEL_INLET_PIN, m=   PT_FUEL_INLET_CAL_M, b=   PT_FUEL_INLET_CAL_B, nick="FIN", name="Fuel\nProp Inlet", ),
    PT_FUEL_INJECTOR_ID: dict(node=SR_ENGINE, pin=PT_FUEL_INJECTOR_PIN, m=PT_FUEL_INJECTOR_CAL_M, b=PT_FUEL_INJECTOR_CAL_B, nick="FIJ", name="Fuel\nInjector",   ),
        PT_CHAMBER_1_ID: dict(node=SR_ENGINE, pin=    PT_CHAMBER_1_PIN, m=    PT_CHAMBER_1_CAL_M, b=    PT_CHAMBER_1_CAL_B, nick="CH1", name="Chamber 1",        ),
        PT_CHAMBER_2_ID: dict(node=SR_ENGINE, pin=    PT_CHAMBER_2_PIN, m=    PT_CHAMBER_2_CAL_M, b=    PT_CHAMBER_2_CAL_B, nick="CH2", name="Chamber 2",        ),
#                    -1 : dict(pin=-1,                   m=1,                      b=0,                      nick="NIL", name="NULL SENSOR"), # Padding
}

SensorKeys = {
    SENS_1_4_PROP:     [   PT_LOX_HIGH_ID,  PT_FUEL_HIGH_ID,     PT_LOX_DOME_ID,     PT_FUEL_DOME_ID],
    SENS_5_8_PROP:     [ PT_LOX_TANK_1_ID, PT_LOX_TANK_2_ID,  PT_FUEL_TANK_1_ID,   PT_FUEL_TANK_2_ID],
    SENS_9_12_ENGINE:  [ PT_PNUEMATICS_ID,  PT_LOX_INLET_ID,   PT_FUEL_INLET_ID, PT_FUEL_INJECTOR_ID],
    SENS_13_16_ENGINE: [  PT_CHAMBER_1_ID,  PT_CHAMBER_2_ID,                 -1,                  -1]
}
