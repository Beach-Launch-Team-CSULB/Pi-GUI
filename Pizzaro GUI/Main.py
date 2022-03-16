# Import the library tkinter
from tkinter import *
from tkinter import font as tkFont  # for font size

from PIL import Image, ImageTk

import datetime

import can  # /////////////////////////////////////////////////////////////////////////
# from CanSend import CanSend
from CanReceive import CanReceive

### This code is initializing the bus variable with the channel and bustype.
# noinspection PyTypeChecker
bus = can.interface.Bus(channel='can1', bustype='socketcan')  # ///////////////

# Create a GUI app
app = Tk()
app.configure(background='black')

# Font Size used for some of the labels
fontSize = tkFont.Font(size=26)
fontSize2 = tkFont.Font(size=17)


# Top most Frame holds all the Nodes and there status's
class NodeFrame:
    # Number of Nodes that will be displayed. Used to size the each individual frame
    numberOfSubframes = 3

    def __init__(self, parent):
        # Create over arching frame for all the Nodes will be placed in
        nodeFrame = Canvas(parent, bg="black", highlightbackground="black", bd=5)
        nodeFrame.place(relx=0.405, rely=0, relwidth=.81, relheight=0.2, anchor="n")

        # Instantiates the Individual Nodes
        telemetryFrame = self.Node(nodeFrame)
        # Array with the labels
        telemetryFrame.labelarray = ["Telemetry Node", "Activity: ", "Temp: ", "Bus Info"]
        # Adds in the labels into the frame
        telemetryFrame.makeNodeLabels()

        upperPropSystemFrame = self.Node(nodeFrame)
        upperPropSystemFrame.labelarray = ["Upper Prop System Node", "Activity: ", "Temp: ", "Bus Info"]
        upperPropSystemFrame.makeNodeLabels()

        engineFrame = self.Node(nodeFrame)
        engineFrame.labelarray = ["Engine Node", "Activity: ", "MCU Temp: ", "Bus Info"]
        engineFrame.makeNodeLabels()

    class Node:
        # Keeps track of number of instantiated Nodes. Used for Frame placement
        numberOfNodes = 0

        def __init__(self, parent):
            # Makes
            self.nodeFrame = Canvas(parent, bg="grey", highlightbackground="black", bd=5)
            self.nodeFrame.place(relx=(1 / NodeFrame.numberOfSubframes + 0.0015) * NodeFrame.Node.numberOfNodes, rely=0,
                                 relwidth=(1 / (NodeFrame.numberOfSubframes)), relheight=1)

            # Updates the amount of instantiated nodes
            NodeFrame.Node.numberOfNodes += 1
            # Holds the labels/text that will be put in the frame
            self.labelarray = []

            # Shows the current state of the node
            nodeState = Label(self.nodeFrame, text="State", bg="black", fg="white")
            nodeState.place(relx=2 / 3 - .025, rely=2 / 3 - .025, relwidth=(1 / 3), relheight=1 / 3)
            # Reset button
            resetButton = Button(self.nodeFrame, text="Reset", command=lambda: self.Reset(), font=("Verdana", 10),
                                 fg='black', bg='white')
            resetButton.place(relx=3 / 4 - .025, rely=.025, relwidth=1 / 4, relheight=1 / 3)

        # Still needs work to be done
        def Reset(self):
            pass

        # Makes the labels for the node and adds it to the frame
        def makeNodeLabels(self):
            numberOfLabels = len(self.labelarray)
            nodeLabels = [0] * numberOfLabels
            for i in range(numberOfLabels):
                nodeLabels[i] = Label(self.nodeFrame, text=self.labelarray[i], bg="grey", anchor="w")
                nodeLabels[i].place(relx=0.01, rely=(1 / numberOfLabels) * i + .01, relwidth=1 / 2,
                                    relheight=1 / (numberOfLabels + 1))


# Creates the Frame that the System States are going to be in
class StatesFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = (
        ("Test", 2, 1, 4, 5, False),
        ("Hi-Press\nPress Arm", 3, 1, 10, 11, True),
        ("Hi-Press\nPressurize", 4, 1, 12, 13, False),
        ("Tank Press \nArm", 5, 1, 14, 15, True),
        ("Tank \nPressurize", 6, 1, 16, 17, False),
        ("Fire Arm", 7, 1, 18, 19, True),
        ("FIRE", 8, 1, 20, 21, False)
    )

    def __init__(self, parent):
        stateFrame = Canvas(parent, bg="grey", highlightbackground="black", bd=5)
        stateFrame.place(relx=0.0001, rely=1 / 5, relwidth=.1, relheight=0.8)

        # Creates label for Passive/Standby State
        self.passiveState = Label(stateFrame, text="Passive", bg="grey", fg="Red", font=fontSize)
        self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)

        # Store previosly instantiated State. Arm States may be able to access the state before it
        prevState = None

        # Every state in State Array gets instantiated and a Button is made for it
        for i in range(len(StatesFrame.States)):
            button = StateButtons(stateFrame, StatesFrame.States[i], prevState=prevState)
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
        # Goes to logic function when button is pressed
        button = Button(self.parent, text=self.args[0], fg='red', bg='black', bd=5, command=lambda: self.Logic(),
                        font=self.fontSize)
        button.place(relx=self.relxcor, rely=self.relycor, relwidth=self.relwitdth, relheight=self.relheight)

    # The Vent and abort buttons are made here
    def VentAbortInstantiation(self):
        self.relxcor = self.args[1]
        self.relycor = 0
        self.relheight = 1
        self.relwitdth = 1 / 4
        self.bgcolor = "grey"
        self.fontSize = ("Verdana", 26)
        button = Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(), fg='red', bg='grey',
                        font=self.fontSize)
        button.place(relx=self.relxcor, rely=self.relycor, relheight=self.relheight, relwidth=self.relwitdth)

    # Holds the logic for the state commands and the transition between the states
    # If in Test mode System leaves passive state and cant go into the other states until user has left Test mode
    # The transition between each state can only be done sequentially but Arm states can go back to its previous state
    # If user input follows the specified logic the State Actuaction function is called and it updated the UI buttons

    # Logic for Vent and Abort currently not done
    def Logic(self):
        if self.stateName == "Test":
            if StateButtons.CurrState == "Passive":
                self.passiveState = Label(self.parent, text="Active", bg="grey", fg="Green", font=fontSize)
                self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
                StateButtons.CurrState = "Test"
                self.StateActuaction()
            else:
                self.passiveState = Label(self.parent, text="Passive", bg="grey", fg="red", font=fontSize)
                self.passiveState.place(relx=.1, rely=0.0125, relwidth=.8, relheight=1 / 30)
                StateButtons.CurrState = "Passive"
                self.StateActuaction()
        elif StateButtons.CurrState != "Test":
            if self.prevState.stateName == StateButtons.CurrState or self.prevState.stateName == "Test":
                self.passiveState = Label(self.parent, text="Active", bg="grey", fg="Green", font=fontSize)
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
            button = Button(self.parent, text=self.args[0], fg='red', bg=self.bgcolor, bd=5,
                            command=lambda: self.Logic(), font=self.fontSize)
            self.state = False
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # ////
        ##            bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        ##            #
        else:
            button = Button(self.parent, text=self.args[0], fg='green', bg=self.bgcolor, bd=5,
                            command=lambda: self.Logic(), font=self.fontSize)
            self.state = True
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # ////
        ##            bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        ##            #
        button.place(relx=self.relxcor, rely=self.relycor, relheight=self.relheight, relwidth=self.relwitdth)


# Creates the rightmost frame that will hold incomming data in a graphical form
# Only a black frame is currently displayed. Graph code is currently missing
class GraphFrame:
    # The amount of graphs that will be used
    numberOfGraphsSubFrames = 3

    def __init__(self, parent):
        graphFrame = Canvas(parent, bg="grey", highlightbackground="black")
        graphFrame.place(relx=.815, rely=.07, relwidth=.1875, relheight=.95)

        # Instantiates the subframe where each individual graph will be held in
        graph1 = self.Graph(graphFrame)
        graph2 = self.Graph(graphFrame)
        graph3 = self.Graph(graphFrame)

    class Graph:
        def __init__(self, parent):
            graph_frame = Frame(parent, bg="grey", bd=5)
            graph_frame.place(relx=0.15, rely=0.1, relwidth=.8, relheight=(1 / 3.1))


# Bottom most frame that holds the Vent and Abort buttons, the Renegade Logo and will also have the Countdown for Autosequence
class VentAbortFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = [
        ["Vent", 0, 1, 20, 21, False],
        ["Abort", 3 / 4, 1, 22, 23, False]
    ]

    def __init__(self, parent):
        self.parent = parent
        # Makes the Frame
        ventAbortFrame = Canvas(parent, bg="black", highlightbackground="black")
        ventAbortFrame.place(relx=0.14, rely=0.85, relwidth=0.65, relheight=0.2)

        # Adds in Renegade Logo
        RenegadeLOGO = Image.open("GUI Images/RenegadeLogoSmall.png")
        render = ImageTk.PhotoImage(RenegadeLOGO)
        img = Button(ventAbortFrame, image=render, bg="black")
        img.image = render
        img.place(relx=.415, rely=0)
        img.bind('<Triple-1>', self.LogoPress)  # bind double left clicks

        # Instantiated the buttons for the Vent and Abort State
        for stateData in VentAbortFrame.States:
            button = StateButtons(ventAbortFrame, stateData)
            button.VentAbortInstantiation()

    def LogoPress(self, event):
        BrandonLabel = Label(self.parent, text="BRANDON IS AMAZING", bg="black", fg="white", font=("Verdana", 50))
        BrandonLabel.place(relx=0, rely=0, relwidth=1, relheight=1)


class PropulsionFrame:
    killSwitchState = False
    # Displays all the sensor readings and what the current valve actuation state is
    # Also allows user to actuate valves individually if test mode is enabled

    # Data needed to set up the button
    # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
    valves = (
        ('HP', 0, .65, 16, 2, 32, 33),
        ('HV', .075, .825, 17, 2, 34, 35),
        ('LV', .375, .025, 18, 3, 36, 37),
        ('LDR', .15, .15, 19, 3, 38, 39),
        ('LDV', .225, .025, 20, 3, 40, 41),
        ('FV', .375, .8, 21, 3, 42, 43),
        ('FDR', .15, .65, 22, 3, 44, 45),
        ('FDV', .225, .8, 17, 23, 3, 46, 47),
        ('LMV', .815, 0.15, 24, 2, 48, 49),
        ('FMV', .685, .15, 25, 2, 50, 51),
    )

    # Data needed to set up the button
    # [ Sensor Name, relx ,rely , Reading Xcor Offest , Reading Xcor Offest,  Sensor ID]
    sensors = [
        ["COPV LOx", 0.06, 0.0125, 0.075, 0.00, 84],
        ["COPV Fuel", 0.06, 0.055, 0.075, 0.00, 83],
        ["Fuel Tank", 0.505, 0.575, 0.06, 0.04, 81],
        ["Lox Tank", 0.505, 0.125, 0.06, 0.04, 82],
        ["Lox\n Dome", 0.305, 0.05, 0.02, 0.08, 80],
        ["Fuel\n Dome", 0.305, 0.7, 0.02, 0.08, 79],
        ["MV\n Pneumatic", 0.715, 0.005, 0.03, 0.08, 78],
        ["Fuel\n Prop Inlet", .65, 0.25, 0.025, 0.08, 57],
        ["LOx\n Prop Inlet", .8125, 0.25, 0.025, 0.08, 59],
        ["---: ", .55, 0.225, 0.03, 0.00, 0],
        ["---: ", .55, 0.34, 0.03, 0.00, 0],
        ["---: ", .55, 0.455, 0.03, 0.00, 0],
        # Engine Sensors
        ["Fuel Inlet", .86, .38, 0.05, 0.04, 10],
        ["Fuel Injector", .86, .46, 0.05, 0.04, 58],
        ["LOX Injector", .86, .54, 0.05, 0.04, 12],
        ["Pc Chamber 1", .7, .38, 0.05, 0.04, 56],
        ["Pc Chamber 2", .7, .46, 0.05, 0.04, 55],
        ["Pc Chamber 3", .7, .54, 0.05, 0.04, 15],
        ["Temp\n ChamberExt", .86, .86, 0.05, 0.08, 16],
        ["LC1: ", .725, .86, 0.065, 0, 17],
        ["LC2: ", .725, .90, 0.065, 0, 18],
        ["LC3: ", .725, .94, 0.065, 0, 19]
    ]

    def __init__(self, parent):
        self.parent = parent
        # Creates the Center Frame where all the propulsion valves and sensors will be displayed
        self.propFrame = Canvas(parent, bg="black", highlightbackground="black")
        self.propFrame.place(relx=0.11, rely=0.2, relwidth=0.7, relheight=0.65)

        # Holds the instantiated Sensors
        self.sensorList = []

        # A bunch of images that are in the UI
        engineart = Image.open("GUI Images/Engine Clipart smol.png")
        render = ImageTk.PhotoImage(engineart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.735, rely=.40)

        LOXTankart = Image.open("GUI Images/TankPlainClipart.png")
        render = ImageTk.PhotoImage(LOXTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.475, rely=.25)

        FuelTankart = Image.open("GUI Images/TankPlainClipart.png")
        render = ImageTk.PhotoImage(FuelTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.475, rely=.615)

        COPVTankart = Image.open("GUI Images/TankPlainClipartCOPV.png")
        render = ImageTk.PhotoImage(COPVTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.0, rely=.0)

        DomeRegart = Image.open("GUI Images/AquaDomeReg Clipart.png")
        render = ImageTk.PhotoImage(DomeRegart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.23, rely=.185)

        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.23, rely=.5)

        # Lines showing the fluid flow routing in the fluid system
        self.propFrame.create_line(25, 100, 25, 1000, fill="khaki", width=5)
        self.propFrame.create_line(25, 600, 100, 600, fill="white", width=5)
        self.propFrame.create_line(25, 325, 225, 325, fill="sienna", width=5)
        self.propFrame.create_line(225, 82, 225, 525, fill="deep pink", width=5)
        self.propFrame.create_line(225, 82, 325, 82, fill="grey", width=5)
        self.propFrame.create_line(225, 525, 325, 525, fill="cyan", width=5)
        self.propFrame.create_line(325, 60, 325, 150, fill="bisque", width=5)
        self.propFrame.create_line(325, 400, 325, 600, fill="blue", width=5)
        self.propFrame.create_line(325, 150, 665, 150, fill="red", width=5)
        self.propFrame.create_line(525, 150, 525, 50, fill="ivory4", width=5)
        self.propFrame.create_line(525, 150, 525, 50, fill="dark slate gray", width=5)
        self.propFrame.create_line(665, 150, 665, 350, fill="green", width=5)
        self.propFrame.create_line(665, 350, 850, 350, fill="yellow", width=5)
        self.propFrame.create_line(850, 350, 850, 50, fill="green", width=5)
        self.propFrame.create_line(850, 50, 1115, 50, fill="orange", width=5)
        self.propFrame.create_line(1115, 50, 1115, 120, fill="snow4", width=5)
        self.propFrame.create_line(1115, 120, 1035, 120, fill="aquamarine4", width=5)
        self.propFrame.create_line(1035, 120, 1035, 300, fill="dark violet", width=5)
        self.propFrame.create_line(325, 400, 665, 400, fill="lime green", width=5)
        self.propFrame.create_line(525, 400, 525, 600, fill="green", width=5)
        self.propFrame.create_line(665, 400, 665, 600, fill="navy", width=5)
        self.propFrame.create_line(665, 600, 900, 600, fill="indian red", width=5)
        self.propFrame.create_line(900, 600, 900, 120, fill="lightpink1", width=5)
        self.propFrame.create_line(900, 120, 1000, 120, fill="yellow4", width=5)
        self.propFrame.create_line(1000, 120, 1000, 300, fill="salmon", width=5)

        # Instantiates Every Valve
        for valve in PropulsionFrame.valves:
            button = Valves(self.propFrame, valve)

        self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
        self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
        self.Button.place(relx=.705, rely=0.205)
        self.Button.bind('<Double-1>', self.KillSwitch)  # bind double left clicks

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

        self.sensorList[1].ReadingLabel.after(250, self.RefreshLabel)

    def KillSwitch(self, event):
        if PropulsionFrame.killSwitchState:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
            self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
            PropulsionFrame.killSwitchState = False
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
        ##            bus.send(msg)
        else:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideEnabledButton.png")
            self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            PropulsionFrame.killSwitchState = True
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
        ##            bus.send(msg)
        self.Button.place(relx=.705, rely=.2050)
        self.Button.bind('<Double-1>', self.KillSwitch)  # bind double left clicks

        # On double press, Call KillSwitch function


class Sensors:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        self.stateID = args[5]

        self.label = Label(parent, text=args[0], font=("Verdana", 10), fg='white', bg='black')
        self.label.place(relx=args[1], rely=args[2], anchor="nw")
        # Makes label with the reading for its corresponding sensor
        self.ReadingLabel = Label(parent, text="N/A", font=("Verdana", 10), fg='orange', bg='grey')
        self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")

    # Updates the reading
    # Gets called by the PropulsionFrame class
    def RefreshLabel(self):
        value = randint(1, 100)
        self.ReadingLabel.config(text=value)  # Updates the label with the updated value


class Valves:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        self.state = False

        self.photo_name = args[0]
        self.x_pos = args[1]
        self.y_pos = args[2]

        self.commandID = args[4]
        self.commandOFF = args[5]
        self.commandON = args[6]

        self.photo = PhotoImage(file="Valve Buttons/" + self.photo_name + "-Closed-EnableOn.png").subsample(2)
        self.Button = Button(parent, image=self.photo, font=("Verdana", 10), fg='red', bg='black')
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        self.Button.bind('<Double-1>', self.valve_actuation)

    def valve_actuation(self, event):
        # User is only allowed to actuate valves if in Test mode
        if StateButtons.CurrState != "Test":
            return 0
        if self.state:
            self.photo = PhotoImage(file="Valve Buttons/" + self.photo_name + "-Closed-EnableOn.png").subsample(2)
            self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
            self.state = False
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
        ##            bus.send(msg)
        else:
            self.photo = PhotoImage(file="Valve Buttons/" + self.photo_name + "-Open-EnableOn.png").subsample(2)
            self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            self.state = True
        ##            msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
        ##            bus.send(msg)
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        # On double press, Call valve_actuation function
        self.Button.bind('<Double-1>', self.valve_actuation)


# Time Frame  ------------------------------------------------------------------------------------------------------
# Displays current time in top right corner
class TimeFrame:
    def refresh_label(self):
        time_label = Label(self.time_frame, fg="Orange", bg='grey',
                           text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), font=("Verdana", 17))
        time_label.place(relx=0.1, rely=0.1)
        self.time_frame.after(1000, self.refresh_label)

    def __init__(self, parent):
        self.time_frame = Frame(parent, bg="gray", bd=5)
        self.time_frame.place(relx=.815, rely=.008, relwidth=.185, relheight=0.05)
        self.time_frame.after(1000, self.refresh_label)


# Instantiates every Frame
center = PropulsionFrame(app)
nodeframe = NodeFrame(app)
leftframe = StatesFrame(app)
bottomframe = VentAbortFrame(app)
rightframe = GraphFrame(app)
timeframe = TimeFrame(app)

app.attributes("-fullscreen",
               True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen
app.bind("<Escape>", lambda event: app.destroy())  # binds escape key to killing the window
app.bind("<F11>", lambda event: app.attributes("-fullscreen", True))  # switches from zoomed to fullscreen
app.bind("<F12>", lambda event: app.attributes("-fullscreen", False))  # switches from fullscreen to zoomed

app.mainloop()
