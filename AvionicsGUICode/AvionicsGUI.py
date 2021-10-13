import tkinter as tk # Import tkinter GUI library
from tkinter import font as tkFont  # for font size
# from typing import runtime_checkable
import serial # Import serial library for python connect with arduino (do pip install pyserial on consolepip)
import can # Import CAN library (do python pip install python-can)

# Root for application //////////////////////////////////////////////////////////////////////////////////////
root = tk.Tk()

# Functions /////////////////////////////////////////////////////////////////////////////////////////////////
# TOP FRAME FUNCTIONS-----------------------------
def telemetryNodeReset():
    pass

def upperPropSystemNodeReset():
    pass

def EngineNodeReset():
    pass

def PadGroundNodeReset():
    pass

# LEFT FRAME FUNCTIONS----------------------------
def testFunction():
    pass

def purgeFunction():
    pass

def hiPressPressArmFunction():
    pass

def hiPressPressurizeFunction():
    pass

def takePressArmFunction():
    pass

def tankPressurizeFunction():
    pass

def fireArmFunction():
    pass

def FIREFunction():
    pass

# CENTER FRAME FUNCTIONS--------------------------
def HPFunction():
    pass

def HVFunction():
    pass

def LDRFunction():
    pass

def FDRFunction():
    pass

def LDVFunction():
    pass

def FDVFunction():
    pass

def LVFunction():
    pass

def FVFunction():
    pass

def LMVFunction():
    pass

def FMVFunction():
    pass

# BOTTOM FRAME FUNCTIONS---------------------------
def ventFunction():
    pass

def abortFunction():
    pass

# Create size for GUI window ////////////////////////////////////////////////////////////////////////////////
# Window size presets
HEIGHT = 1080 
WIDTH = 1920

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Group 1 Mode Display //////////////////////////////////////////////////////////////////////////////////////
# Create group 1 frame
group1ModeFrame = tk.Frame(root, bg="Black", bd=5)
group1ModeFrame.place(relx=0, rely=0, relwidth=3/4, relheight=1)

# CREATE TOP FRAME (Nodes)------------------------------------------------
topFrame = tk.Frame(group1ModeFrame, bg="black", bd=5)
topFrame.place(relx=0.5, rely=0, relwidth=19/20, relheight=0.2, anchor="n")

# Number of top nodes needed
nodes = 4

# nodeFrames[0]: Prop System Node Frame
# nodeFrames[1]: Engine Node Frame
# nodeFrames[2]: Pad Group Node Frame
nodeFrames = [0] * nodes
for i in range(nodes):
    nodeFrames[i] = tk.Frame(topFrame, bg="white", bd=5)
    nodeFrames[i].place(relx=((1/nodes) + 0.0015)*i, rely=0, relwidth=(1/(nodes + 0.1)), relheight=1)

# Telemetry node labels----------------------------------------
# telemetryLabels[0]: Node Name (Upper Prop System Node)
# telemtryLabels[1]: Upper Prop System Activity
# telemetryLabels[2]: Uppoer Prop System Temperature
# telemetryLabels[3]: Sampling / Bus Info
telemetryLabels = [0] * 4
for i in range(4):
    telemetryLabels[i] = tk.Label(nodeFrames[0], text="", bg="blue", anchor="w")
    telemetryLabels[i].place(relx=0, rely=(1/4)*i, relwidth=2/3, relheight=1/4)

telemetryLabels[0]["text"] = "Telemetry Node"
telemetryLabels[1]["text"] = "Activity: "
telemetryLabels[2]["text"] = "Temp: "
telemetryLabels[3]["text"] = "Sampling / Bus Info"

# Upper Prop System node labels-------------------------------
# upperPropSystemLabels[0]: Node Name (Upper Prop System Node)
# upperPropSystemLabels[1]: Upper Prop System Activity
# upperPropSystemLabels[2]: Uppoer Prop System Temperature
# upperPropSystemLabels[3]: Sampling / Bus Info
upperPropSystemLabels = [0] * 4
for i in range(4):
    upperPropSystemLabels[i] = tk.Label(nodeFrames[1], text="", bg="blue", anchor="w")
    upperPropSystemLabels[i].place(relx=0, rely=(1/4)*i, relwidth=2/3, relheight=1/4)

upperPropSystemLabels[0]["text"] = "Upper Prop System Node"
upperPropSystemLabels[1]["text"] = "Activity: "
upperPropSystemLabels[2]["text"] = "Temp: "
upperPropSystemLabels[3]["text"] = "Sampling / Bus Info"

# Engine node labels-----------------------------------------
# engineLabels[0]: Node Name (Engine Node)
# engineLabels[1]: Engine Activity
# engineLabels[2]: Engine Temperature
# engineLabels[3]: Sampling / Bus Info
engineLabels = [0] * 4
for i in range(4):
    engineLabels[i] = tk.Label(nodeFrames[2], text="", bg="blue", anchor="w")
    engineLabels[i].place(relx=0, rely=(1/4)*i, relwidth=2/3, relheight=1/4)

engineLabels[0]["text"] = "Engine Node"
engineLabels[1]["text"] = "Activity: "
engineLabels[2]["text"] = "Temp: "
engineLabels[3]["text"] = "Sampling / Bus Info"

# Pad Ground node labels--------------------------------------
# padGroundLabels[0]: Node Name (Pad Ground Node)
# padGroundLabels[1]: Pad Ground Activity
# padGroundLabels[2]: Pad Ground Temperature
# padGroundLabels[3]: Sampling / Bus Info
padGroundLabels = [0] * 4
for i in range(4):
    padGroundLabels[i] = tk.Label(nodeFrames[3], text="", bg="blue", anchor="w")
    padGroundLabels[i].place(relx=0, rely=(1/4)*i, relwidth=2/3, relheight=1/4)

padGroundLabels[0]["text"] = "Pad Ground Node"
padGroundLabels[1]["text"] = "Activity: "
padGroundLabels[2]["text"] = "Temp: "
padGroundLabels[3]["text"] = "Sampling / Bus Info"

# nodeFrameStateLabels[0]: Prop System Node State Label
# nodeFrameStateLabels[1]: Engine Node State Label
# nodeFrameStateLabels[2]: Pad Group Node State Label
nodeFrameStateLabels = [0] * nodes
for i in range(nodes):
    nodeFrameStateLabels[i] = tk.Label(nodeFrames[i], text="", bg="aqua")
    nodeFrameStateLabels[i].place(relx=2/3, rely=2/3, relwidth=(1/3), relheight=1/3)

# Reset Buttons
# resetButtonList[0]: Telemetry Node Reset Button
# resetButtonList[1]: Upper Prop System Node Reset Button
# resetButtonList[2]: Engine Node Reset Button
# resetButtonList[3]: Pad Ground Node Reset Button
resetButtonList = [0] * 4
for i in range(4):
    resetButtonList[i] = tk.Button(nodeFrames[i], text="Reset")
    resetButtonList[i].place(relx=3/4, rely=0, relwidth=1/4, relheight=1/3)

resetButtonList[0]["command"] = lambda: telemetryNodeReset() # Add button functionality to telemetry node reset
resetButtonList[1]["command"] = lambda: upperPropSystemNodeReset() # Add button functionality to upper prop system node reset
resetButtonList[2]["command"] = lambda: EngineNodeReset() # Add button functionality to engine node reset
resetButtonList[3]["command"] = lambda: PadGroundNodeReset() # Add button functionality to pad ground node reset

# CREATE LEFT FRAME (Buttons)-----------------------------------------------------
leftFrame = tk.Frame(group1ModeFrame, bg="Red", bd=5)
leftFrame.place(relx=0.0255, rely=1/5, relwidth=1/10, relheight=0.8)

# List to store buttons for g1RowFrame1
leftButtonRowList = [0]*12

# Create first row of buttons
# leftButtonRowList[0]: Test
# leftButtonRowList[1]: Purge
# leftButtonRowList[2]: Hi-Press Press Arm
# leftButtonRowList[3]: Hi-Press Pressurize
# leftButtonRowList[4]: Tank Press Arm
# leftButtonRowList[5]: Tank Pressurize
# leftButtonRowList[6]: Fire Arm
# leftButtonRowList[7]: FIRE
for i in range(8): # Create buttons for g1ForFrame1
    leftButtonRowList[i] = tk.Button(leftFrame, text="G1 Button " + str(i + 1))
    leftButtonRowList[i].place(relx=0, rely=((1/8) * i), relwidth=1, relheight=1/8)

# Add text and functionality to left frame buttons
leftButtonRowList[0]["text"] = "Test"
leftButtonRowList[0]["command"] = lambda: testFunction()
leftButtonRowList[1]["text"] = "Purge"
leftButtonRowList[1]["command"] = lambda: purgeFunction()
leftButtonRowList[2]["text"] = "Hi-Press\nPress Arm"
leftButtonRowList[2]["command"] = lambda: hiPressPressArmFunction()
leftButtonRowList[3]["text"] = "Hi-Press\nPressurize"
leftButtonRowList[3]["command"] = lambda: hiPressPressurizeFunction()
leftButtonRowList[4]["text"] = "Tank Press Arm"
leftButtonRowList[4]["command"] = lambda: takePressArmFunction()
leftButtonRowList[5]["text"] = "Tank Pressurize"
leftButtonRowList[5]["command"] = lambda: tankPressurizeFunction()
leftButtonRowList[6]["text"] = "Fire Arm"
leftButtonRowList[6]["command"] = lambda: fireArmFunction()
leftButtonRowList[7]["text"] = "FIRE"
leftButtonRowList[7]["command"] = lambda: FIREFunction()

# CREATE CENTER FRAME (System Map)---------------------------------------------------
centerFrame = tk.Frame(group1ModeFrame, bg="Black")
centerFrame.place(relx=0.16, rely=0.2, relwidth=0.8, relheight=0.65)

# Put schematic draft for layout
schematicImage = tk.PhotoImage(file="Images\SchematicImage2.png")
schematicLabel = tk.Label(centerFrame, image=schematicImage)
schematicLabel.place(relx=0, rely=0)

# Buttons
HP = tk.Button(centerFrame, text="HP", command=lambda: HPFunction()) # HP Button
HP.place(relx=0.02,rely=0.5, relwidth=0.06, relheight=0.12)
HV = tk.Button(centerFrame, text="HV", command=lambda: HVFunction()) #HV Button
HV.place(relx=0.1,rely=0.65, relwidth=0.06, relheight=0.12)
LDR = tk.Button(centerFrame, text="LDR", command=lambda: LDRFunction()) # LDR Button
LDR.place(relx=0.22,rely=0.15, relwidth=0.06, relheight=0.12)
FDR = tk.Button(centerFrame, text="FDR", command=lambda: FDRFunction()) # FDR Button
FDR.place(relx=0.22,rely=0.65, relwidth=0.06, relheight=0.12)
LDV = tk.Button(centerFrame, text="LDV", command=lambda: LDVFunction()) # LDV Button
LDV.place(relx=0.285,rely=0.03, relwidth=0.06, relheight=0.12)
FDV = tk.Button(centerFrame, text="FDV", command=lambda: FDVFunction()) # FDV Button
FDV.place(relx=0.285,rely=0.77, relwidth=0.06, relheight=0.12)
LV = tk.Button(centerFrame, text="LV", command=lambda: LVFunction()) # LV Button
LV.place(relx=0.375,rely=0.03, relwidth=0.06, relheight=0.12)
FV = tk.Button(centerFrame, text="FV", command=lambda: FVFunction()) # FV Button
FV.place(relx=0.375,rely=0.77, relwidth=0.06, relheight=0.12)
LMV = tk.Button(centerFrame, text="LDV", command=lambda: LMVFunction()) # LDV Button
LMV.place(relx=0.775,rely=0.3, relwidth=0.06, relheight=0.12)
FMV = tk.Button(centerFrame, text="FDV", command=lambda: FMVFunction()) # FDV Button
FMV.place(relx=0.67,rely=0.3, relwidth=0.06, relheight=0.12)

# CREATE BOTTOM FRAME (Buttons)-----------------------------------------------------
bottomFrame = tk.Frame(group1ModeFrame, bg="Green", bd=5)
bottomFrame.place(relx=0.16, rely=0.85, relwidth=0.8, relheight=0.15)

# Preset font size
fontSize = tkFont.Font(size=30)

# Vent Button
ventButton = tk.Button(bottomFrame, text="Vent", font=fontSize, command=lambda: ventFunction())
ventButton.place(relx=0, rely=0, relwidth=1/4, relheight=1)

# Abort Button
abortButton = tk.Button(bottomFrame, text="Abort", font=fontSize, command=lambda: abortFunction())
abortButton.place(relx=3/4, rely=0, relwidth=1/4, relheight=1)

#Group 2 Mode Display--------------------------------------------------------------------------------------
#Create group 2 frame
group2ModeFrame = tk.Frame(root, bg="Blue", bd=5)
group2ModeFrame.place(relx=3/4, rely=0, relwidth=1/4, relheight=1)

# Realtime stuff
# root.after(1, randomNumber)

# Start window--------------------------------------------------------------------------------------------
root.state('zoomed') # Maximize window
root.mainloop()