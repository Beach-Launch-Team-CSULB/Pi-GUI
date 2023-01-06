# Import the library tkinter
from tkinter import *
from tkinter import font as tkFont  # for font size

from threading import Thread
import signal

from PIL import Image, ImageTk
from os.path import exists

import datetime



#import can  # /////////////////////////////////////////////////////////////////////////
#from CanReceive import CanReceive

# This code is initializing the bus variable with the channel and bustype.
# noinspection PyTypeChecker
#bus = can.interface.Bus(channel='can0', bustype='socketcan')  # ///////////////

DANGERZONE = 300
sensorSettingList =[
        ("OFF", 126),
        ("SLOW", 127),
        ("MEDIUM", 128),
        ("FAST", 129),
        ("CALIBRATION", 130)
    ]
yellow = "yellow3"
blue = "dodgerblue"
red = "red"
green = "green"
purple = "purple4"
darkgrey = "grey3"
orange = 'orange'

# Creates the Frame that the System States are going to be in
class StatesFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = (
        ("Test", 2, 1, 3, 5, False, 1),
        ("Tank Press \nArm", 5, 1, 14, 15, True, 2),
        ("Tank \nPressurize", 6, 1, 16, 17, False, 3),
        ("Fire Arm", 7, 1, 18, 19, True, 4),
        ("FIRE", 8, 1, 20, 21, False, 5)
    )

    def __init__(self, parent):
        self.stateFrame = Canvas(parent, bg=darkgrey, highlightbackground=orange, bd=5)
        self.stateFrame.place(relx=0.0001, rely=0, relwidth=.15, relheight=1)

        self.StateReset()
        
        self.nodeState = Label(self.stateFrame, text="State", fg=orange, bg=darkgrey, font=("Arial", 25))
        self.nodeState.place(relx=.0625, rely=0.02, relwidth=7/8, relheight=1 / 30)
        self.Activity = Label(self.stateFrame, text="Activity:", fg=orange, bg=darkgrey)
        self.Activity.place(relx=.0625, rely=0.065, relwidth=1/3, relheight=1 / 30)
        self.BusInfo = Label(self.stateFrame, text="Bus Info:", fg=orange, bg=darkgrey)
        self.BusInfo.place(relx=.0625, rely=0.125, relwidth=1/3, relheight=1 / 30)
        self.Kp = Label(self.stateFrame, text="PID STUFF", fg=orange, bg=darkgrey)
        self.Kp.place(relx=.0625, rely=0.2, relwidth=1/3, relheight=1 / 30)
        self.Ki = Label(self.stateFrame, text="PID STUFF", fg=orange, bg=darkgrey)
        self.Ki.place(relx=.0625, rely=0.3, relwidth=1/3, relheight=1 / 30)
        self.Kd = Label(self.stateFrame, text="PID STUFF", fg=orange, bg=darkgrey)
        self.Kd.place(relx=.0625, rely=0.4, relwidth=1/3, relheight=1 / 30)
        
    def StateReset(self):
        # Creates label for Passive/Standby State
        #self.passiveState = Label(self.stateFrame, text="Passive", bg=darkgrey, fg="Red")  # , font=fontSize)
        #self.passiveState.place(relx=.1, rely=0.0125, relwidth=1, relheight=1 / 30)
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
        self.StateNumber = args[6]
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
        self.relheight = 1 / len(StatesFrame.States)/2
        self.relycor = 1-self.relheight * (len(StatesFrame.States)-self.StateNumber+1)-.05
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
        self.relycor = 0.1
        self.relheight = .8
        self.relwitdth = 1 / 8
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
                    self.prevState.StateActuation()
                StateButtons.CurrState = self.stateName
            elif StateButtons.CurrState == self.stateName and self.isArmState:
                self.prevState.StateActuation()
                self.StateActuaction()
                StateButtons.CurrState = self.prevState.stateName

    # Updates the visuals in the UI to specify whether a state is on or off
    # red if OFF and green if ON
    def StateActuaction(self):
        if self.state:
            # button = Button(self.parent, text=self.args[0], command=lambda: self.Logic())  # , font = self.fontSize)
            self.button.config(fg='red')
            self.state = False
            # msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)  # ////
            # bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        ##            #
        else:
            # button = Button(self.parent, text=self.args[0],command=lambda: self.Logic())  # , font = self.fontSize)
            self.button.config(fg='green')
            self.state = True
            if self.isVentAbort:
                Main.StateFrame.StateReset()
            # msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # ////
            # bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
        # button.place(relx=self.relxcor, rely=self.relycor, relheight=self.relheight, relwidth=self.relwitdth)


# Bottom most frame that holds the Vent and Abort buttons, the Renegade Logo and will also have the Countdown for Autosequence
class VentAbortFrame:
    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = [
        ["Vent", 0.05, 1, 3, 9, False, 0],
        ["Abort", 7/8-.05, 1, 3, 7, False, 0]
    ]

    def __init__(self, parent):
        self.parent = parent
        # Makes the Frame
        ventAbortFrame = Canvas(parent, bg="black", highlightbackground="orange", bd = 5)
        ventAbortFrame.place(relx=0.16, rely=0.85, relwidth=0.84, relheight=0.15)
#parent, bg=darkgrey, highlightbackground=orange, bd=5
        self.autoseqence = Label(ventAbortFrame, text="Boom Boom \n wont go boom boom", bg="black", fg="Green",
                                 font=("Verdana", 25))
        self.autoseqence.place(relx=.45, rely=0.2)
        self.autoseqence.after(1000, self.refresh_label)
        self.autosequence_str = ""

        # Adds in Renegade Logo
        #RenegadeLOGO = Image.open("GUI Images/RenegadeLogoSmall.png")
        #render = ImageTk.PhotoImage(RenegadeLOGO)
        #img = Button(ventAbortFrame, image=render, bg="black")
        #img.image = render
        #img.place(relx=.315, rely=0)
        #img.bind('<Triple-1>', self.LogoPress)  # bind double left clicks

        # Instantiated the buttons for the Vent and Abort State
        for stateData in VentAbortFrame.States:
            button = StateButtons(ventAbortFrame, stateData)
            button.VentAbortInstantiation()

    def LogoPress(self, event):
        BrandonLabel = Label(self.parent, text="BRANDON IS AMAZING", bg="black", fg="white", font=("Verdana", 50))
        BrandonLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

    def refresh_label(self):
        self.autosequence_str = 0# "State: " + can_receive.autosequence['state'] + "\n" + \
                                #"T  " + can_receive.autosequence['time'] + " s"
        self.autoseqence.config(text=self.autosequence_str)
        self.autoseqence.after(100, self.refresh_label)


class PropulsionFrame:
    killSwitchState = False
    # Displays all the sensor readings and what the current valve actuation state is
    # Also allows user to actuate valves individually if test mode is enabled

    # Data needed to set up the button
    # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
    valves = (
        ('HV', 0.35, .15, 17, 1, 34, 35),
        ('LV', .175, .3, 18, 1, 36, 37),
        ('FV', .425, .3, 21, 1, 42, 43),
        ('LMV', .25, 0.65, 24, 1, 48, 49),
        ('FMV', .35, .65, 25, 1, 50, 51),
        ('IGN1', .25, .9, 26, 1, 52, 53),
        ('IGN2', .35, .9, 27, 1, 54, 55)
    )

    # Data needed to set up the button
    # [ Sensor Name, relx ,rely , Reading Xcor Offest , Reading Ycor Offest,  Sensor ID]
    sensors = [

        ["Fuel\nTank 1", 0.45, 0.45, 0.01, 0.05, 81, red],
        ["Lox\nTank 1", 0.15, 0.45, 0.01, 0.05, 82, blue],
        ["Fuel\nTank 2", 0.5, 0.45, 0.01, 0.05, 81, red],
        ["Lox\nTank 2", 0.1, 0.45, 0.01, 0.05, 82, blue],
        ["MV\nPneumatic", 0.295, 0.4, 0.01, 0.05, 78, "purple"],
        ["Fuel\nProp Inlet", .475, 0.55, 0.01, 0.05, 57, red],
        ["LOx\nProp Inlet", .125, 0.55, 0.01, 0.05, 59, blue],
        ["LC1: ", .35, .8, 0.035, 0, 17, green],
    ]

    def __init__(self, parent):
        self.parent = parent
        # Creates the Center Frame where all the propulsion valves and sensors will be displayed
        self.propFrame = Canvas(parent, bg="black", highlightbackground="black")
        self.propFrame.place(relx=0.15, rely=0, relwidth=0.9, relheight=0.8)

        # Holds the instantiated Sensors
        self.sensorList = []
        self.valve_list = []

        # A bunch of images that are in the UI
        engineart = Image.open("GUI Images/Engine_Clipart.png")
        render = ImageTk.PhotoImage(engineart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.3, rely=.775)

        LOXTankart = Image.open("GUI Images/LOxTankClipart.png")
        render = ImageTk.PhotoImage(LOXTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.215, rely=.45)

        FuelTankart = Image.open("GUI Images/FuelTankClipart.png")
        render = ImageTk.PhotoImage(FuelTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.39, rely=.45)
        
        COPVTankart = Image.open("GUI Images/PressurantTankClipart.png")
        render = ImageTk.PhotoImage(COPVTankart)
        img = Label(self.propFrame, image=render, bg='Black')
        img.image = render
        img.place(relx=.305, rely=.01)
        

##        self.propFrame.create_rectangle(60,10,250,100,outline = yellow, fill="black")
##        self.propFrame.create_rectangle(300,10,500,100,outline = blue,fill="black")
##        self.propFrame.create_rectangle(300,575,500,675,outline = red,fill="black")
##        self.propFrame.create_rectangle(675,260,775,360,outline = purple,fill="black")
##        self.propFrame.create_rectangle(850,500,1200,650,outline = green,fill="black")
##        self.propFrame.create_rectangle(875,375,1111,475,outline = red,fill="black")
##        self.propFrame.create_rectangle(875,200,1000,300,outline = blue,fill="black")

        
         # Lines showing the fluid flow routing in the fluid system
        self.propFrame.create_line(550, 50, 550, 220, fill=yellow, width=5)
        self.propFrame.create_line(400, 220, 700, 220, fill=yellow, width=5)  #
        self.propFrame.create_line(400, 220, 400, 300, fill=yellow, width=5)  #
        self.propFrame.create_line(700, 220, 700, 300, fill=yellow, width=5)  #
        self.propFrame.create_line(550, 175, 600, 175, fill=yellow, width=5)  #
##        
        self.propFrame.create_line(550, 220, 550, 500, fill="purple", width=5)  #
        self.propFrame.create_line(475, 500, 625, 500, fill="purple", width=5)  #
        self.propFrame.create_line(625, 500, 625, 600, fill="purple", width=5)  #
        self.propFrame.create_line(475, 500, 475, 600, fill="purple", width=5)  #
##
##
        self.propFrame.create_line(400, 220, 400, 600, fill=blue, width=5)  #
        self.propFrame.create_line(400, 600, 535, 600, fill=blue, width=5)  #
        self.propFrame.create_line(535, 600, 535, 700, fill=blue, width=5)  #
        self.propFrame.create_line(400, 300, 300, 300, fill=blue, width=5)  #
##        self.propFrame.create_line(540, 50, 740, 50, fill=blue, width=5)  #
##
        self.propFrame.create_line(700, 220, 700,600, fill=red, width=5)  #
        self.propFrame.create_line(700, 600, 565, 600, fill=red, width=5)  #
        self.propFrame.create_line(565, 600, 565, 700, fill=red, width=5)  #
        self.propFrame.create_line(700, 300, 800, 300, fill=red, width=5)  #
##        self.propFrame.create_line(540, 700, 740, 700, fill=red, width=5)  #
        # Instantiates Every Valve
        for valve in PropulsionFrame.valves:
            self.valve_list.append(Valves(self.propFrame, valve))

        self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
        self.Button = Button(self.parent,image=self.photo, fg='red', bg='black', bd=5)
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
                    self.reminderButtonOfCurrState = Button(Main.StateFrame.stateFrame, text=StateButtons.CurrState,
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
            # msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandON], is_extended_id=False)
            # bus.send(msg)
        else:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideEnabledButton.png")
            self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            PropulsionFrame.killSwitchState = True
            StateButtons.CurrState = "Override"
            # msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandOFF], is_extended_id=False)
            # bus.send(msg)
        self.Button.place(relx=.7, rely=0.2)
        self.Button.bind('<Double-1>', self.KillSwitch)  # bind double left clicks

        # On double press, Call KillSwitch function


class Sensors:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        self.stateID = args[5]
        self.color = args[6]
        self.datalist = []
        aFont = tkFont.Font(family="Verdana", size=10, weight="bold")

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
            value = 1  # CanReceive.Sensors[self.stateID]
        if value >= DANGERZONE:
            self.ReadingLabel.config(fg=red, text=str(value) + " psi")  # Updates the label with the updated value
        else:
            self.ReadingLabel.config(fg=orange, text=str(value) + " psi")  # Updates the label with the updated value


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
        self.Button = Button(parent, font=("Verdana", 10), fg='red', bg='black')
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        self.Button.bind('<Double-1>', self.ValveActuaction)

    def ValveActuaction(self, event):
        # User is only allowed to actuate valves if in Test mode
        if StateButtons.CurrState != "Test" and StateButtons.CurrState != "Override":
            return 0
        if self.state:
            self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Closed-EnableOn.png")  # .subsample(2)
            self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
            self.state = False
            # print(self.commandOFF)
            # msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
            # bus.send(msg)
        else:
            self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Open-EnableOn.png")  # .subsample(2)
            self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
            self.state = True
            print(self.commandON)
            # msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
            # bus.send(msg)
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        # On double press, Call ValveActuaction function
        self.Button.bind('<Double-1>', self.ValveActuaction)

    def refresh_valve(self):
        # if self.id in can_receive.node_state and self.status is not can_receive.node_state[self.id]:
        #     self.status = can_receive.node_state[self.id]
        if True:
            if self.status == 0:  # Closed
                self.photo_name = "Valve Buttons/" + self.name + "-Closed-EnableStale.png"
            elif self.status == 1:  # Open
                self.photo_name = "Valve Buttons/" + self.name + "-Open-EnableStale.png"
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
    PropFrame = PropulsionFrame(app)
    Main.StateFrame = StatesFrame(app)
    Vent_Abort_frame = VentAbortFrame(app)
    Time_frame = TimeFrame(app)

    app.attributes("-fullscreen", True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no
    # taskbars true fullscreen
    app.bind("<Escape>", lambda event: app.destroy())  # binds escape key to killing the window
    app.bind("<F11>", lambda event: app.attributes("-fullscreen", True))  # switches from zoomed to fullscreen
    app.bind("<F12>", lambda event: app.attributes("-fullscreen", False))  # switches from fullscreen to zoomed

    app.mainloop()


class Main:
    StateFrame = None

    def run(self):
        mainGUIloop()


if __name__ == '__main__':
    # subprocess.call(['sh', './cansetup.sh'])
    print("HI")
    GUI = Main()
    GUIThread = Thread(target=GUI.run)
    GUIThread.daemon = True

    # can_receive = CanReceive()
    # can_receive_thread = Thread(target=can_receive.run)
    # can_receive_thread.daemon = True

    GUIThread.start()
    # can_receive_thread.start()
    # signal.pause()
