# Import the library tkinter
from tkinter import *
from tkinter import font as tkFont  # for font size

from threading import Thread
import signal

from PIL import Image, ImageTk
from os.path import exists

import datetime



import can  # /////////////////////////////////////////////////////////////////////////
from CanReceive import CanReceive

# This code is initializing the bus variable with the channel and bustype.
# noinspection PyTypeChecker
bus = can.interface.Bus(channel='can0', bustype='socketcan')  # ///////////////

DANGERZONE = 3000

yellow = "yellow3"
blue = "dodgerblue"
red = "red"
green = "green"
purple = "purple4"
darkgrey = "grey3"
orange = 'orange'
# Top most Frame holds all the Nodes and there status's
class NodeFrame:
    # Number of Nodes that will be displayed. Used to size the each individual frame
    numberOfSubframes = 3
    
    sensorSettingList =[
        ("OFF", 126),
        ("SLOW", 127),
        ("MEDIUM", 128),
        ("FAST", 129),
        ("CALIBRATION", 130)
    ]

    def __init__(self, parent):
        # Create over arching frame for all the Nodes will be placed in
        self.nodeFrame = Canvas(parent, bg="black", highlightbackground="black", bd=5)
        self.nodeFrame.place(relx=0.405, rely=0, relwidth=.81, relheight=0.2, anchor="n")

        # Instantiates the Individual Nodes
        self.telemetryFrame = self.Node(self.nodeFrame,commandRESET=244, name = "PasafireNode",  canID=700)
        # Array with the labels
        self.telemetryFrame.labelarray = ["Pasafire Node", "Activity: ", "Temp: ", "Bus Info"]
        # Adds in the labels into the frame
        self.telemetryFrame.makeNodeLabels()

        self.upperPropSystemFrame = self.Node(self.nodeFrame, commandRESET = 240, name = "UpperPropNode", canID=300)
        self.upperPropSystemFrame.labelarray = ["Upper Prop System Node", "Activity: ", "Temp: ", "Bus Info"]
        self.upperPropSystemFrame.makeNodeLabels()

        self.engineFrame = self.Node(self.nodeFrame, commandRESET = 239, name = "PadGroundNode", canID=200)
        self.engineFrame.labelarray = ["Engine Node", "Activity: ", "MCU Temp: ", "Bus Info"]
        self.engineFrame.makeNodeLabels()

        globalResetButton = Button(self.nodeFrame, text="Reset", command=lambda: self.Reset(), font=("Verdana", 10),
                                   fg='black', bg='orange', bd=5)
        globalResetButton.place(
            relx=(1 / (NodeFrame.numberOfSubframes + 1 / 2) + 0.0015) * (NodeFrame.numberOfSubframes), rely=0,
            relwidth=1 - (1 / (NodeFrame.numberOfSubframes + 1 / 2) + 0.0015) * (NodeFrame.numberOfSubframes),
            relheight=1 / 2)
        self.refresh_label()
        
#         self.sampleSettingDefault = "SLOW"
#         self.sampleSettingButton = Button(self.nodeFrame, text=self.sampleSettingDefault, command=lambda: self.SampleSettingChange(), font=("Verdana", 10),
#                                    fg='orange', bg='grey15', bd=5)
#         self.sampleSettingButton.place(
#             relx=(1/ (NodeFrame.numberOfSubframes + 1 / 2) + 0.0015) * (NodeFrame.numberOfSubframes)+0.025, rely=9/16,
#             relwidth=(1 - (1 / (NodeFrame.numberOfSubframes + 1 / 2) + 0.0015) * (NodeFrame.numberOfSubframes))/1.5,
#             relheight=1 / 3)
#         
#     def SampleSettingChange(self):
#         if StateButtons.CurrState == "Test":
#             for i in range(len(NodeFrame.sensorSettingList)):
#                 if NodeFrame.sensorSettingList[i][0] == self.sampleSettingDefault:
#                     if len(NodeFrame.sensorSettingList) <= i+1:
#                         self.sampleSettingButton.config(text=NodeFrame.sensorSettingList[0][0])
#                         self.sampleSettingDefault = NodeFrame.sensorSettingList[0][0]
#                         msg = can.Message(arbitration_id=1, data=[NodeFrame.sensorSettingList[0][1]], is_extended_id=False)  # ////
#                         bus.send(msg)
#                     else:
#                         self.sampleSettingButton.config(text=NodeFrame.sensorSettingList[i+1][0])
#                         self.sampleSettingDefault = NodeFrame.sensorSettingList[i+1][0]
#                         msg = can.Message(arbitration_id=1, data=[NodeFrame.sensorSettingList[i+1][1]], is_extended_id=False)  # ////
#                         bus.send(msg)
#                     break

    def refresh_label(self):
        self.upperPropSystemFrame.refresh_label()
        self.engineFrame.refresh_label()
        self.nodeFrame.after(100, self.refresh_label)

    class Node:
        # Keeps track of number of instantiated Nodes. Used for Frame placement
        numberOfNodes = 0

        def __init__(self, parent, commandRESET = None,  name=None, canID=None):
            # Makes
            self.nodeLabels = []
            self.nodeFrame = Canvas(parent, bg=darkgrey, highlightbackground=orange)
            self.nodeFrame.place(
                relx=(1 / (NodeFrame.numberOfSubframes + 1 / 2) + 0.0015) * NodeFrame.Node.numberOfNodes, rely=0,
                relwidth=(1 / (NodeFrame.numberOfSubframes + 1 / 2)), relheight=1)
            self.name = name
            self.commandRESET = commandRESET
            # Updates the amount of instantiated nodes
            NodeFrame.Node.numberOfNodes += 1
            # Holds the labels/text that will be put in the frame
            self.labelarray = []
            self.canID = canID
            # Shows the current state of the node
            self.nodeState = Label(self.nodeFrame, text="State", bg="grey20", fg=orange)
            self.nodeState.place(relx=2 / 3 - .025, rely=2 / 3 - .025, relwidth=(1 / 3), relheight=1 / 3)
            # Reset button
#             resetButton = Button(self.nodeFrame, text="Reset", command=lambda: self.Reset(), font=("Verdana", 10),
#                                  fg='black', bg='white')
#             resetButton.place(relx=3 / 4 - .025, rely=.025, relwidth=1 / 4, relheight=1 / 3)
            canResetButton = Button(self.nodeFrame, text="Can Reset", command=lambda: self.Reset(),
                                    font=("Verdana", 10),
                                    fg=orange, bg=darkgrey, bd=5)
            canResetButton.place(relx=3 / 4 - .025, rely=.025, relwidth=1 / 4, relheight=1 / 3)

        def refresh_label(self):
            self.nodeState.config(text=str(can_receive.node_dict_list[self.name]["state"]))
            self.nodeLabels[2].config(text="MCU Temp: " + str(CanReceive.Sensors[self.canID]))

        # Still needs work to be done
        def Reset(self):
            msg = can.Message(arbitration_id=self.commandID, data=[self.commandRESET], is_extended_id=False)  # ////
            bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////

            

        # Makes the labels for the node and adds it to the frame
        def makeNodeLabels(self):
            numberOfLabels = len(self.labelarray)
            for i in range(numberOfLabels):
                node_label = Label(self.nodeFrame, text=self.labelarray[i], bg=darkgrey, anchor="w", fg=orange)
                node_label.place(relx=0.01, rely=(1 / numberOfLabels) * i + .01, relwidth=1 / 3,
                                 relheight=1 / (numberOfLabels + 1))
                self.nodeLabels.append(node_label)


    def Reset(self):
        msg = can.Message(arbitration_id=self.commandID, data=[254], is_extended_id=False)  # ////
        bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////



# Creates the Frame that the System States are going to be in
class StatesFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = (
        ("Test", 2, 1, 3, 5, False),
        ("Hi-Press\nPress Arm", 3, 1, 10, 11, True),
        ("Hi-Press\nPressurize", 4, 1, 12, 13, False),
        ("Tank Press \nArm", 5, 1, 14, 15, True),
        ("Tank \nPressurize", 6, 1, 16, 17, False),
        ("Fire Arm", 7, 1, 18, 19, True),
        ("FIRE", 8, 1, 20, 21, False)
    )

    def __init__(self, parent):
        self.stateFrame = Canvas(parent, bg=darkgrey, highlightbackground=orange, bd=5)
        self.stateFrame.place(relx=0.0001, rely=1 / 5, relwidth=.1, relheight=0.8)

        self.StateReset()

    def StateReset(self):
        # Creates label for Passive/Standby State
        self.passiveState = Label(self.stateFrame, text="Passive", bg=darkgrey, fg="Red")  # , font=fontSize)
        self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
        StateButtons.CurrState = "Passive"
        # Store previosly instantiated State. Arm States may be able to access the state before it
        prevState = None
        # Every state in State Array gets instantiated and a Button is made for it
        for i in range(len(StatesFrame.States)):
            button = StateButtons(self.stateFrame, StatesFrame.States[i], prevState=prevState)
            # Creates the button and places it into the Frame. May change name later since it really inst instantiating 
            button.MainStateInstantiation()
            # Updates the prevState so that the next state may be able to access it. Its pretty much a Linked List
            prevState = button


# Creates the Buttons and holds all the logic for the states
class StateButtons:
    # System starts off in a passive state
    CurrState = "Passive"

    # Parent is the Parent Frame
    # args is the data in the States array. 
    def __init__(self, parent, args, prevState=None):
        self.parent = parent
        self.args = args
        self.state = False
        self.prevState = prevState
        self.stateName = args[0]
        self.isArmState = args[5]
        self.commandID = args[2]
        self.commandOFF = args[3]
        self.commandON = args[4]
        # Info needed to make the labels and buttons. May get updated in MainStateInstantiation or VentAbortInstantiation
        self.relxcor = 0
        self.relycor = 0
        self.relheight = 1
        self.relwitdth = 1
        self.bgcolor = "black"
        self.fontSize = ("Verdana", 10)

    # The Main state buttons get made here
    def MainStateInstantiation(self):
        self.relxcor = 0.125 / 2
        self.relycor = (1 / (len(StatesFrame.States) + 1) * (self.args[1] - 1)) - 1 / 18
        self.relheight = 1 / (len(StatesFrame.States) + 1)
        self.relwitdth = 0.85
        self.bgcolor = "black"
        self.isVentAbort = False
        # Goes to logic function when button is pressed
        self.button = Button(self.parent, text=self.args[0], fg='red', bg='black', bd=5,
                        command=lambda: self.Logic())  # , font = self.fontSize)
        self.button.place(relx=self.relxcor, rely=self.relycor, relwidth=self.relwitdth, relheight=self.relheight)

    # The Vent and abort buttons are made here
    def VentAbortInstantiation(self):
        self.relxcor = self.args[1]
        self.relycor = 0
        self.relheight = .9
        self.relwitdth = 1 / 4
        self.bgcolor = darkgrey
        self.fontSize = ("Verdana", 26)
        self.isVentAbort = True
        self.button = Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(), fg='red',
                        bg=darkgrey, font=self.fontSize, bd=5)  # , font=self.fontSize)
        self.button.place(relx=self.relxcor, rely=self.relycor, relheight=self.relheight, relwidth=self.relwitdth)
        
    # Holds the logic for the state commands and the transition between the states
    # If in Test mode System leaves passive state and cant go into the other states until user has left Test mode
    # The transition between each state can only be done sequentially but Arm states can go back to its previous state
    # If user input follows the specified logic the State Actuaction function is called and it updated the UI buttons

    # Logic for Vent and Abort currently not done
    def Logic(self):
        if self.stateName == "Test":
            if StateButtons.CurrState == "Passive":
                self.passiveState = Label(self.parent, text="Active", bg=darkgrey, fg="Green")  # , font=fontSize)
                self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
                StateButtons.CurrState = "Test"
                self.StateActuaction()
            elif StateButtons.CurrState == "Test":
                self.passiveState = Label(self.parent, text="Passive", bg=darkgrey, fg="red")  # , font=fontSize)
                self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
                StateButtons.CurrState = "Passive"
                self.StateActuaction()
            else:
                return 0
        elif StateButtons.CurrState != "Test":
            if self.prevState.stateName == StateButtons.CurrState or (
                    StateButtons.CurrState == "Passive" and self.prevState.stateName == "Test"):
                self.passiveState = Label(self.parent, text="Active", bg=darkgrey, fg="Green")  # , font=fontSize)
                self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
                self.StateActuaction()
                if self.prevState.stateName != "Test":
                    self.prevState.StateActuaction()
                StateButtons.CurrState = self.stateName
            elif StateButtons.CurrState == self.stateName and self.isArmState:
                self.prevState.StateActuaction()
                self.StateActuaction()
                StateButtons.CurrState = self.prevState.stateName

    # Updates the visuals in the UI to specify whether a state is on or off
    # red if OFF and green if ON
    def StateActuaction(self):
        if self.state:
            #button = Button(self.parent, text=self.args[0], command=lambda: self.Logic())  # , font = self.fontSize)
            self.button.config(fg= 'red')
            self.state = False
            msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)  # ////
            bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        ##            #
        else:
            #button = Button(self.parent, text=self.args[0],command=lambda: self.Logic())  # , font = self.fontSize)
            self.button.config(fg= 'green')
            self.state = True
            if self.isVentAbort:
                print("hi")
                Main.leftframe.StateReset()
            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # ////
            bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        #button.place(relx=self.relxcor, rely=self.relycor, relheight=self.relheight, relwidth=self.relwitdth)

# Creates the rightmost frame that will hold incomming data in a graphical form
# Only a black frame is currently displayed. Graph code is currently missing
class GraphFrame:
    # The amount of graphs that will be used
    numberOfGraphsSubFrames = 3

    def __init__(self, parent):
        graphFrame = Canvas(parent, bg=darkgrey, highlightbackground="black")
        graphFrame.place(relx=.815, rely=.07, relwidth=.1875, relheight=.95)

        # Instantiates the subframe where each individual graph will be held in
        graph1 = self.Graph(graphFrame)
        graph2 = self.Graph(graphFrame)
        graph3 = self.Graph(graphFrame)

    class Graph:
        def __init__(self, parent):
            graph_frame = Frame(parent, bg=darkgrey, bd=5)
            graph_frame.place(relx=0.15, rely=0.1, relwidth=.8, relheight=(1 / 3.1))


# Bottom most frame that holds the Vent and Abort buttons, the Renegade Logo and will also have the Countdown for Autosequence
class VentAbortFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = [
        ["Vent", 0, 1, 3, 9, False],
        ["Abort", 3 / 4, 1, 3, 7, False]
    ]

    def __init__(self, parent):
        self.parent = parent
        # Makes the Frame
        ventAbortFrame = Canvas(parent, bg="black", highlightbackground="black")
        ventAbortFrame.place(relx=0.14, rely=0.85, relwidth=0.65, relheight=0.15)

        self.autoseqence = Label(ventAbortFrame, text="Boom Boom \n wont go boom boom", bg="black", fg="Green",
                                 font=("Verdana", 25))
        self.autoseqence.place(relx=.45, rely=0.2)
        self.autoseqence.after(1000, self.refresh_label)
        self.autosequence_str = ""

        # Adds in Renegade Logo
        RenegadeLOGO = Image.open("GUI Images/RenegadeLogoSmall.png")
        render = ImageTk.PhotoImage(RenegadeLOGO)
        img = Button(ventAbortFrame, image=render, bg="black")
        img.image = render
        img.place(relx=.315, rely=0)
        img.bind('<Triple-1>', self.LogoPress)  # bind double left clicks

        # Instantiated the buttons for the Vent and Abort State
        for stateData in VentAbortFrame.States:
            button = StateButtons(ventAbortFrame, stateData)
            button.VentAbortInstantiation()

    def LogoPress(self, event):
        BrandonLabel = Label(self.parent, text="BRANDON IS AMAZING", bg="black", fg="white", font=("Verdana", 50))
        BrandonLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

    def refresh_label(self):
        self.autosequence_str = "State: " + can_receive.autosequence['state'] + "\n" + \
                                "T  " + can_receive.autosequence['time'] + " s"
        self.autoseqence.config(text=self.autosequence_str)
        self.autoseqence.after(100, self.refresh_label)


class PropulsionFrame:
    killSwitchState = False
    # Displays all the sensor readings and what the current valve actuation state is
    # Also allows user to actuate valves individually if test mode is enabled

    # Data needed to set up the button
    # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
    valves = (
        ('HP', 0, .65, 16, 1, 32, 33),
        ('HV', 0.05, .825, 17, 1, 34, 35),
        ('LV', .45, .01, 18, 1, 36, 37),
        ('LDR', .165, .275, 19, 1, 38, 39),
        ('LDV', .265, .275, 20, 1, 40, 41),
        ('FV', .45, .85, 21, 1, 42, 43),
        ('FDR', .165, .55, 22, 1, 44, 45),
        ('FDV', .265, .55, 23, 1, 46, 47),
        ('LMV', .565, 0.25, 24, 1, 48, 49),
        ('FMV', .565, .6, 25, 1, 50, 51),
        ('IGN1', .8, .25, 26, 1, 52, 53),
        ('IGN2', .9, .25, 27, 1, 54, 55)
    )

    # Data needed to set up the button
    # [ Sensor Name, relx ,rely , Reading Xcor Offest , Reading Ycor Offest,  Sensor ID]
    sensors = [
        ["COPV LOx", 0.06, 0.0225, 0.075, 0.00, 84, yellow],
        ["COPV Fuel", 0.06, 0.065, 0.075, 0.00, 83, yellow],
        ["Fuel\nTank", 0.315, 0.855, 0.01, 0.06, 81, red],
        ["Fuel\nDome", 0.24, 0.855, 0.01, 0.06, 79, yellow],
        ["Lox\nTank", 0.315, 0.025, 0.01, 0.06, 82, blue],
        ["Lox\nDome", 0.24, 0.025, 0.01, 0.06, 80, yellow],
        ["MV\nPneumatic", 0.51, 0.4, 0.02, 0.08, 78, yellow],
        ["Fuel\nProp Inlet", .665, 0.55, 0.025, 0.08, 57, red],
        ["LOx\nProp Inlet", .665, 0.3, 0.025, 0.08, 59, blue],
        ["Fuel\nInjector", .76, .55, 0.015, 0.08, 58, red],

        #["---: ", .55, 0.225, 0.03, 0.00, 0],
        #["---: ", .55, 0.34, 0.03, 0.00, 0],
        #["---: ", .55, 0.455, 0.03, 0.00, 0],
        # Engine Sensors
        #["Fuel Inlet", .86, .38, 0.05, 0.04, 10],
        #["LOX Injector", .86, .54, 0.05, 0.04, 12],
        ["Pc\nChamber 1", .75, .75, 0.075, 0.01, 56, green],
        ["Pc\nChamber 2", .75, .85, 0.075, 0.01, 55, green],
        #["Pc Chamber 3", .7, .54, 0.05, 0.04, 15],
        #["Temp\n ChamberExt", .86, .86, 0.05, 0.08, 16],
        ["LC1: ", .65, .76, 0.035, 0, 17, green],
        ["LC2: ", .65, .80, 0.035, 0, 18, green],
        ["LC3: ", .65, .84, 0.035, 0, 19, green]
    ]

    def __init__(self, parent):
        self.parent = parent
        # Creates the Center Frame where all the propulsion valves and sensors will be displayed
        self.propFrame = Canvas(parent, bg="black", highlightbackground="black")
        self.propFrame.place(relx=0.11, rely=0.2, relwidth=0.7, relheight=0.65)

        # Holds the instantiated Sensors
        self.sensorList = []
        self.valve_list = []

        # A bunch of images that are in the UI
        engineart = Image.open("GUI Images/Engine_Clipart.png")
        render = ImageTk.PhotoImage(engineart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.835, rely=.435)

        LOXTankart = Image.open("GUI Images/LOxTankClipart.png")
        render = ImageTk.PhotoImage(LOXTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.425, rely=.15)

        FuelTankart = Image.open("GUI Images/FuelTankClipart.png")
        render = ImageTk.PhotoImage(FuelTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.425, rely=.7475)

        COPVTankart = Image.open("GUI Images/PressurantTankClipart.png")
        render = ImageTk.PhotoImage(COPVTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.0, rely=.0)

        DomeRegart = Image.open("GUI Images/AquaDomeReg_Clipart.png")
        render = ImageTk.PhotoImage(DomeRegart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.175, rely=.115)

        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.175, rely=.725)
        
        self.propFrame.create_rectangle(60,10,250,100,outline = yellow, fill="black")
        self.propFrame.create_rectangle(300,10,500,100,outline = blue,fill="black")
        self.propFrame.create_rectangle(300,575,500,675,outline = red,fill="black")
        self.propFrame.create_rectangle(675,260,775,360,outline = purple,fill="black")
        self.propFrame.create_rectangle(850,500,1200,650,outline = green,fill="black")
        self.propFrame.create_rectangle(875,375,1111,475,outline = red,fill="black")
        self.propFrame.create_rectangle(875,200,1000,300,outline = blue,fill="black")

        # Lines showing the fluid flow routing in the fluid system
        self.propFrame.create_line(25, 100, 25, 1100, fill=yellow, width=5)  #
        self.propFrame.create_line(25, 625, 200, 625, fill=yellow, width=5)  #
        self.propFrame.create_line(25, 337, 180, 337, fill=yellow, width=5)  #
        self.propFrame.create_line(180, 130, 180, 550, fill=yellow, width=5)  #
        self.propFrame.create_line(180, 550, 600, 550, fill=yellow, width=5)  #
        self.propFrame.create_line(180, 130, 600, 130, fill=yellow, width=5)  #
        
        self.propFrame.create_line(260, 100, 260, 550, fill="purple", width=5)  #
        self.propFrame.create_line(180, 337, 660, 337, fill="purple", width=5)  #
        self.propFrame.create_line(260, 425, 460, 425, fill="purple", width=5)  #
        self.propFrame.create_line(260, 235, 460, 235, fill="purple", width=5)  #
        self.propFrame.create_line(660, 215, 660, 450, fill="purple", width=5)  #
        self.propFrame.create_line(660, 215, 800, 215, fill="purple", width=5)  #
        self.propFrame.create_line(660, 450, 800, 450, fill="purple", width=5)  #

        #self.propFrame.create_line(180, 325, 260, 325, fill="purple", width=5)  #

        self.propFrame.create_line(475, 130, 800, 130, fill=blue, width=5)  #
        self.propFrame.create_line(800, 130, 800, 325, fill=blue, width=5)  #
        self.propFrame.create_line(800, 325, 1150, 325, fill=blue, width=5)  #
        self.propFrame.create_line(540, 130, 540, 50, fill=blue, width=5)  #
        self.propFrame.create_line(540, 50, 740, 50, fill=blue, width=5)  #

        self.propFrame.create_line(475, 550, 800, 550, fill=red, width=5)  #
        self.propFrame.create_line(800, 550, 800, 350, fill=red, width=5)  #
        self.propFrame.create_line(800, 350, 1150, 350, fill=red, width=5)  #
        self.propFrame.create_line(540, 550, 540, 650, fill=red, width=5)  #
        self.propFrame.create_line(540, 650, 740, 650, fill=red, width=5)  #

        # Instantiates Every Valve
        for valve in PropulsionFrame.valves:
            self.valve_list.append(Valves(self.propFrame, valve))

        self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
        self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
        self.Button.place(relx=.7, rely=0.2)
        self.Button.bind('<Double-1>', self.KillSwitch)  # bind double left clicks
        self.overrideCommandID = 1
        self.overrideCommandOFF = 22
        self.overrideCommandON = 23

        # Instantiates Every Valve
        for sensor in PropulsionFrame.sensors:
            self.sensorList.append(Sensors(self.propFrame, sensor))

        # Refreshlabel() Refreshes the Readings
        self.RefreshLabel()

    # Readings Refresher, Recursive Function
    def RefreshLabel(self):
        # for each sensor in the sensor list. refresh the label
        for sensor in self.sensorList:
            sensor.RefreshLabel()
        for valve in self.valve_list:
            valve.refresh_valve()
        self.sensorList[1].ReadingLabel.after(250, self.RefreshLabel)

    def KillSwitch(self, event):
        if StateButtons.CurrState != "Override":
            self.savedCurrState = StateButtons.CurrState
            for i in range(len(StatesFrame.States)):
                if StatesFrame.States[i][0] == StateButtons.CurrState:
                    self.reminderButtonOfCurrState = Button(Main.leftframe.stateFrame, text=StateButtons.CurrState,
                                                            fg='orange', bg='black', bd=5)
                    # Goes to logic function when button is pressed
                    self.reminderButtonOfCurrState.place(relx=0.125 / 2, rely=(1 / (len(StatesFrame.States) + 1) * (
                                StatesFrame.States[i][1] - 1)) - 1 / 18, relheight=1 / (len(StatesFrame.States) + 1),
                                                         relwidth=0.85)
        if PropulsionFrame.killSwitchState:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
            self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
            PropulsionFrame.killSwitchState = False
            self.reminderButtonOfCurrState.destroy()
            StateButtons.CurrState = self.savedCurrState
            msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandOFF], is_extended_id=False)
            bus.send(msg)
        else:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideEnabledButton.png")
            self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            PropulsionFrame.killSwitchState = True
            StateButtons.CurrState = "Override"
            msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandON], is_extended_id=False)
            bus.send(msg)
        self.Button.place(relx=.7, rely=0.2)
        self.Button.bind('<Double-1>', self.KillSwitch)  # bind double left clicks

        # On double press, Call KillSwitch function


class Sensors:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        self.stateID = args[5]
        self.color = args[6]
        self.datalist  = []
        self.datapoint = 0
        aFont = tkFont.Font(family="Verdana",size=10,weight="bold")

        self.label = Label(parent, text=args[0], font=aFont, fg=self.color, bg='black')
        self.label.place(relx=args[1], rely=args[2], anchor="nw")
        # Makes label with the reading for its corresponding sensor
        self.ReadingLabel = Label(parent, text="N/A", font=("Verdana", 12), fg='orange', bg='black')
        self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")

    # Updates the reading
    # Gets called by the PropulsionFrame class
    def RefreshLabel(self):
        # value = randint(1,100)
        if self.stateID == 0:
            value = 0
        else:
            #self.datapoint = self.datapoint % 10 + 1
            #self.datalist[]
            value = CanReceive.Sensors[self.stateID]
            
        if value >= DANGERZONE:
            self.ReadingLabel.config(fg=red, text=str(value) +" psi")  # Updates the label with the updated value
        else:
            self.ReadingLabel.config(fg=orange, text=str(value) +" psi")  # Updates the label with the updated value

class Valves:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        self.state = False
        self.photo_name = args[0]
        self.status = 0  # Keeps track of valve actuation state

        self.name = args[0]
        self.x_pos = args[1]
        self.y_pos = args[2]
        self.id = args[3]
        self.commandID = args[4]
        self.commandOFF = args[5]
        self.commandON = args[6]

        self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Stale-EnableStale.png")  # .subsample(2)
        self.Button = Button(parent, image=self.photo, font=("Verdana", 10), fg='red', bg='black')
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        self.Button.bind('<Double-1>', self.ValveActuaction)

    def ValveActuaction(self, event):
        # User is only allowed to actuate valves if in Test mode
        if StateButtons.CurrState != "Test" and StateButtons.CurrState != "Override":
            return 0
        if self.state:
            #self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Closed-EnableOn.png")  # .subsample(2)
            #self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
            #self.state = False
            #print(self.commandOFF)
            msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
            bus.send(msg)
        else:
            #self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Open-EnableOn.png")  # .subsample(2)
            #self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            #if self.name != "IGN1" and self.name != "IGN2":
            #self.state = True
            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
            bus.send(msg)
        #self.Button.place(relx=self.x_pos, rely=self.y_pos)
        # On double press, Call ValveActuaction function
        #self.Button.bind('<Double-1>', self.ValveActuaction)

    def refresh_valve(self):
        #print(can_receive.node_state)
        if self.id in can_receive.node_state and self.status is not can_receive.node_state[self.id]:
            self.status = can_receive.node_state[self.id]
            if self.status == 0:  # Closed
                self.photo_name = "Valve Buttons/" + self.name + "-Closed-EnableStale.png"
                self.state = False
            elif self.status == 1:  # Open
                self.photo_name = "Valve Buttons/" + self.name + "-Open-EnableStale.png"
                self.state = True
            elif self.status == 2:
                self.photo_name = "Valve Buttons/" + self.name + "-FireCommanded-EnableStale.png"
#             elif can_receive.currRefTime - can_receive.node_state_time[self.id] >= can_receive.staleTimeThreshold:
#                 self.photo_name = "Valve Buttons/" + self.name + "-Stale-EnableStale.png"
            if not exists(self.photo_name):
                print(self.photo_name + " Does not exist. Status is " + str(self.status))
            else:
                #print(self.photo_name, self.status)
                self.photo = PhotoImage(file=self.photo_name)
                self.Button.config(image=self.photo)


# Time Frame  ------------------------------------------------------------------------------------------------------
# Displays current time in top right corner
class TimeFrame:
    def refresh_label(self):
        time_label = Label(self.time_frame, fg="Orange", bg=darkgrey,
                           text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), font=("Verdana", 17))
        time_label.place(relx=0, rely=0.1)
        self.time_frame.after(1000, self.refresh_label)

    def __init__(self, parent):
        self.time_frame = Frame(parent, bg=darkgrey, bd=5)
        self.time_frame.place(relx=.815, rely=.008, relwidth=.185, relheight=0.05)
        self.time_frame.after(1000, self.refresh_label)


def mainGUIloop():
    # Create a GUI app
    app = Tk()
    app.configure(background='black')

    # Font Size used for some of the labels
    fontSize = tkFont.Font(size=26)
    fontSize2 = tkFont.Font(size=17)

    # Instantiates every Frame
    Main.leftframe = StatesFrame(app)
    center = PropulsionFrame(app)
    nodeframe = NodeFrame(app)
    bottomframe = VentAbortFrame(app)
    rightframe = GraphFrame(app)
    timeframe = TimeFrame(app)
    # Uncomment line for X forwarding
    app.attributes("-fullscreen", True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no
    # taskbars true fullscreen
    app.bind("<Escape>", lambda event: app.destroy())  # binds escape key to killing the window
    app.bind("<F11>", lambda event: app.attributes("-fullscreen", True))  # switches from zoomed to fullscreen
    app.bind("<F12>", lambda event: app.attributes("-fullscreen", False))  # switches from fullscreen to zoomed

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    #print(screen_width)
    #print(screen_height)

    app.mainloop()


class Main:
    def __init__(self):
        leftframe = None

    def run(self):
        mainGUIloop()


if __name__ == '__main__':
    # subprocess.call(['sh', './cansetup.sh'])
    GUI = Main()
    GUIThread = Thread(target=GUI.run)
    GUIThread.daemon = True

    #     cansend = CanSend()
    #     cansendThread = Thread(target=cansend.run)
    #     cansendThread.daemon = True
    can_receive = CanReceive()
    can_receive_thread = Thread(target=can_receive.run)
    can_receive_thread.daemon = True

    GUIThread.start()
    #     cansendThread.start()
    can_receive_thread.start()
    signal.pause()
