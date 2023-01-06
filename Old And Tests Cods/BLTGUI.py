# Import the library tkinter
from tkinter import *
from tkinter import font as tkFont  # for font size
from threading import Thread
from PIL import Image, ImageTk
from os.path import exists
import bitstring
import datetime
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from matplotlib import style

# # This code is initializing the bus variable with the channel and bustype.
# # noinspection PyTypeChecker

CanStatus = False
try:
    import can  # /////////////////////////////////////////////////////////////////////////

    bus = can.interface.Bus(channel='can0', bustype='socketcan')  # ///////////////
    CanStatus = True
    from CanReceive import CanReceive

except AttributeError:
    CanStatus = False
except ModuleNotFoundError:
    pass


def CanBusSend(ID, DATA):
    print(DATA)
    if CanStatus:
        msg = can.Message(arbitration_id=ID,
                          data=DATA, is_extended_id=False)
        bus.send(msg)


style.use("dark_background")

REFRESHRATE = 250  # ms
GRAPHDATAREFRESHRATE = 250  # ms

# This code is initializing the bus variable with the channel and bustype.
# noinspection PyTypeChecker
# bus = can.interface.Bus(channel='can0', bustype='socketcan')  # ///////////////

yellow = "yellow3"
blue = "dodgerblue"
red = "red"
green = "green"
purple = "purple4"
darkGrey = "grey3"
orange = 'orange'
black = "black"
grey = "grey35"
white = "white"
DANGERZONE = 300

NODEID = 8
VERIFICATIONID = 166


class Main:
    # Data needed to set up the Valve, Sensors, States
    # [ Valve Name, relx ,rely , Object ID , commandID, commandOFF , commandON, ]

    # Name, Relx, Rely , Object ID, HP Channel, Command OFF, Command ON
    valves = [
        ['HV', .55, .25, 16, 2, 32, 33, yellow, 122],
        ['HP', .6, .15, 17, 1, 38, 39, yellow, 121],
        ['LDR', .35, .35, 19, 3, 38, 39, blue,133],
        ['FDR', .445, .35, 22, 7, 44, 45, red,137],
        ['LDV', .225, .35, 20, 4, 40, 41, blue,134],
        ['FDV', .55, .35, 23, 8, 44, 45, red,138],
        ['LV', .275, .45, 18, 1, 36, 37, blue,131],
        ['FV', .535, .45, 21, 5, 42, 43, red,135],
        ['LMV', .35, .6875, 24, 4, 48, 49, blue,124],
        ['FMV', .475, .6875, 25, 3, 50, 51, red,123],
        ['IGN1', .475, .775, 26, 5, 52, 53, green,125], 
        ['IGN2', .475, .85, 27, 7, 54, 55, green,127]
    ]
    # [ Sensor Name, relx ,rely , Reading Xcor Offest , Reading Ycor Offest,  Raw Sensor ID, Converted Sensor ID,
    # labelColor]
    sensors = [
        ["High\nPress Fuel side", 0.475, 0.05, 0.0, 0.05, 70, 81, yellow],#, 1, 1],
        ["High\nPress 2", 0.525, 0.05, 0.0, 0.05, 72, 81, yellow],#, 1, 1],
        ["MV\nPneumatic", 0.4, 0.6, 0.01, 0.05, 56, 81, purple],#, 1, 1],
        ["Fuel\nTank 1", 0.675, 0.600, 0, 0.05, 62, 81, red],#, 0.0258, -161.04],
        ["Fuel Dome Reg 1", 0.675, 0.600, 0, 0.05, 74, 81, red],#, 0.0258, -161.04],
        ["LOx Dome Reg", 0.675, 0.600, 0, 0.05, 76, 81, red],#, 0.0258, -161.04],
        ["Lox\nTank 1", 0.225, 0.600, 0, 0.05, 66, 81, blue],#, 1, 1],
        ["Fuel\nTank 2", 0.725, 0.600, 0, 0.05, 64, 81, red],#, 0.0293, -190.04],
        ["Lox\nTank 2", 0.175, 0.600, 0.0, 0.05, 68, 81, blue],#, 1,1],
        ["Fuel\nProp Inlet", .7, 0.7, 0.0, 0.05, 58, 81, red],#, 1, 1],
        ["Fuel\nInjector", .7, 0.7, 0.0, 0.05, 54, 81, red],#, 1, 1],
        ["LOx\nProp Inlet", .2, 0.7, 0.0, 0.05, 60, 81, blue],#, 1, 1],
        ["LC1: ", .55, .7, 0.035, 0, 37, 37, green],#, 1, 1],
        ["Chamber 1", .55, 0.6, 0.065, 0, 50, 51, green],
        ["LC2: ", .55, .75, 0.035, 0, 43, 43, green],#, 1, 1],
        ["Chamber 2", .55, 0.65, 0.065, 0, 52, 81, green],
        ["LC3: ", .55, .8, 0.035, 0, 49, 49, green],#, 1, 1],

        #["Chamber 2", .55, 0.65, 0.065, 0, 20, 81, green],

    ]
    
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = [
        ["Active", 2, 1, 3, 5, False, 1],
        ["Test", 2, 1, 3, 5, False, 2],
        ["Hi-Press\nPress Arm", 3, 1, 10, 11, True,3],
        ["Hi-Press\nPressurize", 4, 1, 12, 13, False,4],
        ["Tank Press \nArm", 5, 1, 14, 15, True, 5],
        ["Tank \nPressurize", 6, 1, 16, 17, False, 6],
        ["Fire Arm", 7, 1, 18, 19, True, 7],
        ["FIRE", 8, 1, 20, 21, False, 8]
    ]
    Vent = [
        "Vent", 0.15, 1, 3, 9, False, 0
    ]
    Abort = [
        "Abort", .275, 1, 3, 7, False, 0
    ]
    Controllers = [
        ["Tank Controller HiPress", 2, False, black],
        ["Tank Controller Lox", 3, True, blue],
        ["Tank Controller Fuel", 4, True, red],
        ["Engine Controller 1", 5, False, black],
        ["Auto Sequence", 1, False, black],
        ["Node Controller", 0, False, black],
    ]

    # System starts off in a passive state
    CurrState = "Passive"

    def __init__(self):
        self.appMainScreen = None
        self.parentMainScreen = None

        """ Manual Override """
        self.ManualOverridePhoto = None
        self.ManualOverrideButton = None
        self.overrideCommandID = 1
        self.overrideCommandOFF = 22
        self.overrideCommandON = 23

        self.sensorList = []
        self.valveList = []
        self.controllerList = []

        self.LOxSetPressure = 150
        self.FuelSetPressure = 150

        self.manualOverrideState = False

        self.nodeCommandReset = 240
        self.nodeCommandID = 200

        self.ValveOptionsDropDownMenu = None
        self.statusLabel = None

        self.graphingStatus = True
        self.refreshCounter = True

    def imagePlacement(self):
        """ Propulsion System Diagram"""
        EngineArt = Image.open("GUI Images/Engine_Clipart.png")
        render = ImageTk.PhotoImage(EngineArt)
        img = Label(self.parentMainScreen, image=render, bg=black)
        img.image = render
        img.place(relx=.4, rely=.775)

        LOXTankArt = Image.open("GUI Images/LOxTankClipart.png")
        render = ImageTk.PhotoImage(LOXTankArt)
        img = Label(self.parentMainScreen, image=render, bg=black)
        img.image = render
        img.place(relx=.3, rely=.55)

        FuelTankArt = Image.open("GUI Images/FuelTankClipart.png")
        render = ImageTk.PhotoImage(FuelTankArt)
        img = Label(self.parentMainScreen, image=render, bg=black)
        img.image = render
        img.place(relx=.5075, rely=.55)

        COPVTankArt = Image.open("GUI Images/PressurantTankClipart.png")
        render = ImageTk.PhotoImage(COPVTankArt)
        img = Label(self.parentMainScreen, image=render, bg=black)
        img.image = render
        img.place(relx=.405, rely=.01)

        # Adds in Renegade Logo
#         RenegadeLOGO = Image.open("GUI Images/RenegadeLogoSmall.png")
#         render = ImageTk.PhotoImage(RenegadeLOGO)
#         img = Label(self.parentMainScreen, image=render, bg='Black')
#         img.image = render
#         img.place(relx=.405, rely=0.85)

    def propLinePlacement(self):
        # Lines showing the fluid flow routing in the fluid system
        self.parentMainScreen.create_line(800, 50, 800, 250, fill=yellow, width=5)
        self.parentMainScreen.create_line(600, 250, 1000, 250, fill=yellow, width=5)  #
        self.parentMainScreen.create_line(600, 250, 600, 400, fill=yellow, width=5)  #
        self.parentMainScreen.create_line(800, 250, 800, 400, fill=yellow, width=5)  #
        self.parentMainScreen.create_line(800, 175, 1200, 175, fill=yellow, width=5)  #
        self.parentMainScreen.create_line(1000, 250, 1000, 400, fill=yellow, width=5)  #
        self.parentMainScreen.create_line(1100, 175, 1100, 300, fill=yellow, width=5)  #

        self.parentMainScreen.create_line(800, 300, 800, 400, fill=purple, width=5)  #
        self.parentMainScreen.create_line(500, 400, 1100, 400, fill=purple, width=5)  #
        self.parentMainScreen.create_line(700, 600, 900, 600, fill=purple, width=5)  #
        self.parentMainScreen.create_line(800, 400, 800, 600, fill=purple, width=5)  #
        self.parentMainScreen.create_line(900, 600, 900, 750, fill=purple, width=5)  #
        self.parentMainScreen.create_line(700, 600, 700, 750, fill=purple, width=5)  #

        self.parentMainScreen.create_line(600, 400, 600, 750, fill=blue, width=5)  #
        self.parentMainScreen.create_line(600, 750, 785, 750, fill=blue, width=5)  #
        self.parentMainScreen.create_line(785, 750, 785, 900, fill=blue, width=5)  #
        self.parentMainScreen.create_line(600, 500, 500, 500, fill=blue, width=5)  #

        self.parentMainScreen.create_line(1000, 400, 1000, 750, fill=red, width=5)  #
        self.parentMainScreen.create_line(1000, 750, 815, 750, fill=red, width=5)  #
        self.parentMainScreen.create_line(815, 750, 815, 900, fill=red, width=5)  #
        self.parentMainScreen.create_line(1000, 500, 1100, 500, fill=red, width=5)  # 

        self.parentMainScreen.create_rectangle(1275, 600, 1475, 850, outline=red, fill="black")
        self.parentMainScreen.create_rectangle(300, 600, 500, 850, outline=blue, fill="black")
        self.parentMainScreen.create_rectangle(1050, 600, 1250, 900, outline=green, fill="black")
        self.parentMainScreen.create_rectangle(850, 30, 1100, 150, outline=yellow, fill="black")
        self.parentMainScreen.create_rectangle(750, 625, 870, 725, outline=purple, fill="black")

    def ManualOverride(self, event):
        if Main.CurrState != "Override":
            self.savedCurrState = Main.CurrState
            for i in range(len(Main.States)):
                if Main.States[i][0] == Main.CurrState:
                    self.reminderButtonOfCurrState = Button(self.parentMainScreen, text=Main.CurrState,
                                                            fg='orange', bg='black', bd=5, font=20)
                    # Goes to logic function when button is pressed
                    self.reminderButtonOfCurrState.place(relx=0.0125, rely=1 - (1 / len(Main.States) / 2) * (
                            len(Main.States) - Main.States[i][6] + 1) - .05, relheight=1 / len(Main.States) / 2,
                                                         relwidth=0.125)
        if self.manualOverrideState:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
            self.Button = Button(self.parentMainScreen, image=self.photo, fg='red', bg='black', bd=5)
            self.parentMainScreen.killSwitchState = False
            self.reminderButtonOfCurrState.destroy()
            Main.CurrState = self.savedCurrState
            # msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandON], is_extended_id=False)
            # bus.send(msg)
        else:
            self.photo = PhotoImage(file="GUI Images/ManualOverrideEnabledButton.png")
            self.Button = Button(self.parentMainScreen, image=self.photo, fg='green', bg='black', bd=5)
            self.manualOverrideState = True
            Main.CurrState = "Override"
            # msg = can.Message(arbitration_id=self.overrideCommandID, data=[self.overrideCommandOFF], is_extended_id=False)
            # bus.send(msg)
        self.Button.place(relx=.7, rely=0.2)
        self.Button.bind('<Double-1>', self.ManualOverride)  # bind double left clicks

        # On double press, Call KillSwitch function

    # Readings Refresher, Recursive Function
    def Refresh(self):
        if self.refreshCounter >= REFRESHRATE:
            self.refreshCounter = 0
            # for each sensor in the sensor list. refresh the label
            self.axes1.clear()
            self.axes2.clear()
            self.axes3.clear()
            self.axes4.clear()
            legendsGraph1 = []
            legendsGraph2 = []
            legendsGraph3 = []
            legendsGraph4 = []

            for sensor in self.sensorList:
                sensor.Refresh(True)
                if self.graphingStatus:

                    if sensor.Graph1Status.get():
                        self.axes1.plot(sensor.sensorData, label=sensor.args[0])
                        self.figure1.canvas.draw()
                        legendsGraph1.append(sensor.args[0])
                    if sensor.Graph2Status.get():
                        self.axes2.plot(sensor.sensorData, label=sensor.args[0])
                        self.figure2.canvas.draw()
                        legendsGraph2.append(sensor.args[0])
                    if sensor.Graph3Status.get():
                        self.axes3.plot(sensor.sensorData, label=sensor.args[0])
                        self.figure3.canvas.draw()
                        legendsGraph3.append(sensor.args[0])
                    if sensor.Graph4Status.get():
                        self.axes4.plot(sensor.sensorData, label=sensor.args[0])
                        self.figure4.canvas.draw()
                        legendsGraph4.append(sensor.args[0])

            if legendsGraph1:
                self.axes1.legend(legendsGraph1, loc="upper left")
                self.figure1.canvas.draw()
            if legendsGraph2:
                self.axes2.legend(legendsGraph2, loc="upper left")
                self.figure2.canvas.draw()
            if legendsGraph3:
                self.axes3.legend(legendsGraph3, loc="upper left")
                self.figure3.canvas.draw()
            if legendsGraph4:
                    self.axes4.legend(legendsGraph4, loc="upper left")
                    self.figure4.canvas.draw()

            for valve in self.valveList:
                valve.refresh_valve()
#             for controller in self.controllerList:
#                 controller.Refresh()

            self.autosequence_str = "T  " + str(CanReceive.AutosequenceTime) + " s"
            self.autoseqence.config(text=self.autosequence_str)
            self.time.config(text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            #self.nodeState.config(text=CanReceive.NodeStatus)  # can_receive.node_dict_list[self.name]["state"]))

            self.sensorList[1].ReadingLabel.after(GRAPHDATAREFRESHRATE, self.Refresh)
        else:
            for sensor in self.sensorList:
                sensor.Refresh(False)
                self.refreshCounter += GRAPHDATAREFRESHRATE

            self.sensorList[1].ReadingLabel.after(GRAPHDATAREFRESHRATE, self.Refresh)
            
        self.VehicleState.config(text = " Vehicle State: " + CanReceive.NodeStatus)
        self.MissionState.config(text = "Mission State: " + CanReceive.NodeStatus)


    def StateReset(self):
        Main.CurrState = "Passive"
        # Store previosly instantiated State. Arm States may be able to access the state before it
        prevState = None
        # Every state in State Array gets instantiated and a Button is made for it
        for i in range(len(Main.States)):
            button = States(self.parentMainScreen, Main.States[i], prevState=prevState)
            # Creates the button and places it into the Frame. May change name later since it really inst instantiating
            button.MainStateInstantiation()
            # Updates the prevState so that the next state may be able to access it. Its pretty much a Linked List
            prevState = button

    def AutoSequence(self):
        self.autoseqence = Label(self.parentMainScreen, text="Boom Boom \n wont go boom boom", bg="black", fg="Green",
                                 font=("Verdana", 25))
        self.autoseqence.place(relx=.2, rely=0.05)
        self.autosequence_str = ""

    def PauseGraphs(self):
        #print(self.graphingStatus)
        self.graphingStatus = not self.graphingStatus

    def graphs(self):
        self.pauseButton = Button(self.parentSecondScreen, font=("Verdana", 10), fg='red', bg='black',
                                  text="GRAPH PAUSE\nBUTTON", command=lambda: self.PauseGraphs())
        self.pauseButton.place(relx=.7, rely=.5)

        self.graphFrame1 = Canvas(self.parentMainScreen, bg=black)
        self.graphFrame1.place(relx=.775, rely=.1, relwidth=.225, relheight=2 / 5)
        self.figure1 = Figure(figsize=(5, 5), dpi=100)
        self.canvasfigure1 = FigureCanvasTkAgg(self.figure1, master=self.graphFrame1)
        self.axes1 = self.figure1.add_subplot()
        self.canvasfigure1.get_tk_widget().pack()

        self.graphFrame2 = Canvas(self.parentMainScreen, bg=black)
        self.graphFrame2.place(relx=.775, rely=.6, relwidth=.225, relheight=2 / 5)
        self.figure2 = Figure(figsize=(5, 5), dpi=100)
        self.canvasfigure2 = FigureCanvasTkAgg(self.figure2, master=self.graphFrame2)
        self.axes2 = self.figure2.add_subplot()
        self.canvasfigure2.get_tk_widget().pack()

        self.graphFrame3 = Canvas(self.parentSecondScreen, bg=black)
        self.graphFrame3.place(relx=.775, rely=.05, relwidth=.225, relheight=2 / 5)
        self.figure3 = Figure(figsize=(5, 5), dpi=100)
        self.canvasfigure3 = FigureCanvasTkAgg(self.figure3, master=self.graphFrame3)
        self.axes3 = self.figure3.add_subplot()
        self.canvasfigure3.get_tk_widget().pack()

        self.graphFrame4 = Canvas(self.parentSecondScreen, bg=black)
        self.graphFrame4.place(relx=.775, rely=.5, relwidth=.225, relheight=2 / 5)
        self.figure4 = Figure(figsize=(5, 5), dpi=100)
        self.canvasfigure4 = FigureCanvasTkAgg(self.figure4, master=self.graphFrame4)
        self.axes4 = self.figure4.add_subplot()
        self.canvasfigure4.get_tk_widget().pack()

    def ValveSettingsPopUp(self):
        """
        Creates Pop Up Window with a Drop down menu with all the valve
        when a valve is chosen FunctionsDropDownMenu appears with the options available for that valve
        After a Operation is chosen Valve Set Function is called to do the Entry check and sends the command
        """
        self.ValveSetsPopUp = Toplevel(self.appMainScreen, background=grey)
        self.ValveSetsPopUp.geometry("750x250")
        self.chosenValveFunction = None
        clicked = StringVar()
        clicked.set("Choose Valve")
        self.valveOptions = []
        for valve in self.valveList:
            self.valveOptions.append(valve.name)
        self.ValveChoiceDropDown = OptionMenu(self.ValveSetsPopUp, clicked, *self.valveOptions,
                                              command=lambda Valve2: self.FunctionsDropDownMenu(Valve2, "Valve"))
        self.ValveChoiceDropDown.place(relx=0.2, rely=0.5)
        self.ValveFunctionLabel = Label(self.ValveSetsPopUp, bg=grey)
        self.ValveFunctionLabel.place(relx=.5, rely=0.4)

    def SensorSettingsPopUp(self):
        self.SensorSetsPopUp = Toplevel(self.appMainScreen, background=grey)
        self.SensorSetsPopUp.geometry("750x250")
        self.chosenSensorFunction = None
        clicked = StringVar()
        clicked.set("Choose Sensor")
        self.sensorOptions = []
        for sensor in self.sensorList:
            self.sensorOptions.append(sensor.name)
        self.SensorChoiceDropDown = OptionMenu(self.SensorSetsPopUp, clicked, *self.sensorOptions,
                                               command=lambda Sensor2: self.FunctionsDropDownMenu(Sensor2, "Sensor"))
        self.SensorChoiceDropDown.place(relx=0.2, rely=0.5)
        self.SensorFunctionLabel = Label(self.SensorSetsPopUp, bg=grey)
        self.SensorFunctionLabel.place(relx=.5, rely=0.4)

    def ControllerSettingsPopUp(self):
        self.ControllerPopUp = Toplevel(self.appMainScreen, background=grey)
        self.ControllerPopUp.geometry("750x250")
        self.chosenTankPressFunction = None
        clicked = StringVar()
        clicked.set("Choose Tank Press Controller")
        self.ControllerOptions = []
        for controller in self.controllerList:
            self.ControllerOptions.append(controller.name)
        self.ControllerChoiceDropDown = OptionMenu(self.ControllerPopUp, clicked, *self.ControllerOptions,
                                                   command=lambda Sensor2: self.FunctionsDropDownMenu(Sensor2,
                                                                                                      "Tank Press Controller"))
        self.ControllerChoiceDropDown.place(relx=0.2, rely=0.5)
        self.ControllerFunctionLabel = Label(self.ControllerPopUp, bg=grey)
        self.ControllerFunctionLabel.place(relx=.5, rely=0.4)

    def FunctionsDropDownMenu(self, object, type):
        if type == "Valve":
            for valve in self.valveList:
                if valve.name == object:
                    self.chosenValve = valve
                    break
            clicked2 = StringVar()
            clicked2.set("Choose Function")
            self.valveSetFunctions = [
                "Reset", "Valve Type", "Full Duty Time", "Full Duty Cycle PWM",
                "Hold Duty Cycle PWM", "Warm Duty Cycle PWM",
            ]
            if "IGN" in object:
                self.valveSetFunctions = [
                    "Reset", "Live Out Time"
                ]
            self.ValveOptionsDropDownMenu = OptionMenu(self.ValveSetsPopUp, clicked2, *self.valveSetFunctions,
                                                       command=lambda
                                                           Function: self.ValveSetFunction(Function))
            self.ValveOptionsDropDownMenu.config(width=20)
            self.ValveOptionsDropDownMenu.place(relx=0.2, rely=0.7)
            if self.chosenValveFunction is not None:
                self.ValveFunctionLabel.config(text=self.chosenValve.name + " " + self.chosenValveFunction)
        elif type == "Sensor":
            for sensor in self.sensorList:
                if sensor.name == object:
                    self.chosenSensor = sensor
                    break
            clicked2 = StringVar()
            clicked2.set("Choose Function")
            self.sensorSetFunctions = [
                "Reset", "Sample Rate", "Alpha EMA"
            ]
            self.SensorOptionsDropDownMenu = OptionMenu(self.SensorSetsPopUp, clicked2, *self.sensorSetFunctions,
                                                        command=lambda
                                                            Function: self.SensorSetFunction(Function))
            self.SensorOptionsDropDownMenu.config(width=20)
            self.SensorOptionsDropDownMenu.place(relx=0.2, rely=0.7)
            if self.chosenSensorFunction is not None:
                self.SensorFunctionLabel.config(text=self.chosenSensor.name + " " + self.chosenSensorFunction)
        elif type == "Tank Press Controller":
            for Controller in self.controllerList:
                if Controller.name == object:
                    self.chosenController = Controller
                    break
            clicked2 = StringVar()
            clicked2.set("Choose Function")

            self.ControllerSetFunctions = [
                "Reset",
                "Kp",
                "Ki",
                "Kd",
                "Controller Threshold",
                "Vent Fail Safe Pressure",
                "Valve Minimum Energize Time",
                "Valve Minimum Deenergize Time"
            ]

            if "Engine" in object:
                self.ControllerSetFunctions = [
                    "Reset",
                    "Fuel MV Autosequence Actuation",
                    "Lox MV Autosequence Actuation",
                    "Igniter 1 Actuation",
                    "Igniter 2 Actuation",
                    "ThrottleProgramPoint",
                    "Throttle Program Reset ALL"
                    "Throttle Program Reset Specific Target Point"
                ]

            if "Auto Sequence" in object:
                self.ControllerSetFunctions = [
                    "Reset",
                    "Countdown Start",
                ]

            self.TankPressControllerOptionsDropDownMenu = OptionMenu(self.ControllerPopUp, clicked2,
                                                                     *self.ControllerSetFunctions,
                                                                     command=lambda
                                                                         Function: self.ControllerSetFunction(Function))
            self.TankPressControllerOptionsDropDownMenu.config(width=20)
            self.TankPressControllerOptionsDropDownMenu.place(relx=0.2, rely=0.7)
            if self.chosenTankPressFunction is not None:
                self.ControllerFunctionLabel.config(text=self.chosenController[0] + " " + self.chosenTankPressFunction)

    def ValveSetFunction(self, Function):
        self.chosenValveFunction = Function
        self.ValveDataEntryButton = Button(self.ValveSetsPopUp, height=1, width=10, background="grey50", text="Enter")
        self.ValveDataEntryButton.place(relx=.5, rely=.7)
        self.ValveStatusLabel = Label(self.ValveSetsPopUp, font=("Helvetica", 12), bg=grey)
        self.ValveStatusLabel.place(relx=.7, rely=0.6)
        self.ValveSetData = StringVar()
        self.ValveSetDataEntry = Entry(self.ValveSetsPopUp, background="grey50", textvariable=self.ValveSetData)
        self.ValveSetDataEntry.place(relx=.5, rely=.5)
        self.ValveFunctionLabel.config(text=self.chosenValve.name + " " + self.chosenValveFunction)
        if Function == "Reset":
            self.ValveSetDataEntry.destroy()
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.resetAll(self.ValveSetData, self.statusLabel))
        elif Function == "Valve Type":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.setValveType(self.ValveSetData, self.ValveStatusLabel))
        elif Function == "Full Duty Time":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.setFullDutyTime(self.ValveSetData, self.ValveStatusLabel))
        elif Function == "Full Duty Cycle PWM":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.setFullDutyCyclePWM(self.ValveSetData, self.ValveStatusLabel))
        elif Function == "Hold Duty Cycle PWM":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.setHoldDutyCyclePWM(self.ValveSetData, self.ValveStatusLabel))
        elif Function == "Warm Duty Cycle PWM":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.setWarmDutyCyclePWM(self.ValveSetData, self.ValveStatusLabel))
        elif Function == "Live Out Time":
            self.ValveDataEntryButton.config(
                command=lambda: self.chosenValve.intTypeCheck(self.ValveSetData, self.ValveStatusLabel))

    def SensorSetFunction(self, Function):
        self.chosenSensorFunction = Function
        self.SensorDataEntryButton = Button(self.SensorSetsPopUp, height=1, width=10, background="grey50", text="Enter")
        self.SensorDataEntryButton.place(relx=.5, rely=.7)
        self.SensorStatusLabel = Label(self.SensorSetsPopUp, font=("Helvetica", 12), bg=grey)
        self.SensorStatusLabel.place(relx=.7, rely=0.6)
        self.SensorSetData = StringVar()
        self.SensorSetDataEntry = Entry(self.SensorSetsPopUp, background="grey50", textvariable=self.SensorSetData)
        self.SensorSetDataEntry.place(relx=.5, rely=.5)
        self.SensorFunctionLabel.config(text=self.chosenSensor.name + " " + self.chosenSensorFunction)
        if Function == "Reset":
            self.SensorSetDataEntry.destroy()
            self.SensorDataEntryButton.config(
                command=lambda: self.chosenSensor.resetAll(self.SensorSetData, self.SensorStatusLabel))
        elif Function == "Sample Rate":
            self.SensorDataEntryButton.config(
                command=lambda: self.chosenSensor.setSampleRate(self.SensorSetData, self.SensorStatusLabel))
        elif Function == "Alpha EMA":
            self.SensorDataEntryButton.config(
                command=lambda: self.chosenSensor.setAlphaEMA(self.SensorSetData, self.SensorStatusLabel))

    def ControllerSetFunction(self, Function):
        self.chosenControllerFunction = Function
        self.ControllerDataEntryButton = Button(self.ControllerPopUp, height=1, width=10, background="grey50",
                                                text="Enter")
        self.ControllerDataEntryButton.place(relx=.5, rely=.7)
        self.ControllerstatusLabel = Label(self.ControllerPopUp, font=("Helvetica", 12), bg=grey)
        self.ControllerstatusLabel.place(relx=.7, rely=0.6)
        self.ControllerSetData = StringVar()
        self.ControllerSetDataEntry = Entry(self.ControllerPopUp, background="grey50",
                                            textvariable=self.ControllerSetData)
        self.ControllerSetDataEntry.place(relx=.5, rely=.5)
        self.ControllerFunctionLabel.config(text=self.chosenController.name + " " + self.chosenControllerFunction)
        if Function == "Reset":
            self.ControllerSetDataEntry.destroy()
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.resetAll(self.ControllerSetData, self.ControllerstatusLabel))
        elif Function == "Kp":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setK_p(self.ControllerSetData, self.ControllerstatusLabel))
        elif Function == "Ki":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setK_i(self.ControllerSetData, self.ControllerstatusLabel))
        elif Function == "Kd":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setK_d(self.ControllerSetData, self.ControllerstatusLabel))
        elif Function == "Controller Threshold":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setControllerThreshold(self.ControllerSetData,
                                                                             self.ControllerstatusLabel))
        elif Function == "Vent Fail Safe Pressure":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setVentFailsafePressure(self.ControllerSetData,
                                                                              self.ControllerstatusLabel))
        elif Function == "Valve Minimum Energize Time":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setValveMinimumEnergizeTime(self.ControllerSetData,
                                                                                  self.ControllerstatusLabel))
        elif Function == "Valve Minimum Deenergize Time":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setValveMinimumDeenergizeTime(self.ControllerSetData,
                                                                                    self.ControllerstatusLabel))
        elif Function == "Fuel MV Autosequence Actuation":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setFuelMVAutosequenceActuation(self.ControllerSetData,
                                                                                     self.ControllerstatusLabel))
        elif Function == "Lox MV Autosequence Actuation":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setLoxMVAutosequenceActuation(self.ControllerSetData,
                                                                                    self.ControllerstatusLabel))
        elif Function == "Igniter 1 Actuation":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setIgniter1ActuationActuation(self.ControllerSetData,
                                                                                    self.ControllerstatusLabel))
        elif Function == "Igniter 2 Actuation":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setIgniter2ActuationActuation(self.ControllerSetData,
                                                                                    self.ControllerstatusLabel))
        elif Function == "ThrottleProgramPoint":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setThrottleProgramPoint(self.ControllerSetData,
                                                                              self.ControllerstatusLabel))
        elif Function == "Throttle Program Reset ALL":
            self.ControllerSetDataEntry.destroy()
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.throttleProgramReset(self.ControllerSetData,
                                                                           self.ControllerstatusLabel))
        elif Function == "Throttle Program Reset Specific Target Point":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.throttleProgramResetSpecific(self.ControllerSetData,
                                                                                   self.ControllerstatusLabel))
        elif Function == "Countdown Start":
            self.ControllerDataEntryButton.config(
                command=lambda: self.chosenController.setCountdownStart(self.ControllerSetData,
                                                                        self.ControllerstatusLabel))

    def AutoSequenceSettings(self):
        self.AutoSequencePopUp = Toplevel(self.appMainScreen, background=grey)
        self.AutoSequencePopUp.geometry("750x250")
        self.AutoSequenceSetData = StringVar()
        self.AutoSequenceDataEntryButton = Button(self.AutoSequencePopUp, height=1, width=10, background="grey50",
                                                  text="Enter")
        self.AutoSequenceDataEntryButton.place(relx=.5, rely=.7)
        self.AutoSequenceSetDataEntry = Entry(self.AutoSequencePopUp, background="grey50",
                                              textvariable=self.AutoSequenceSetData)
        self.AutoSequenceSetDataEntry.place(relx=.5, rely=.5)

    def NodeReset(self):
        DATA = [254]
        CanBusSend(1, DATA)

    def AutoSequenceReset(self):
        settingID = 0
        ID = 0
        DATA = [VERIFICATIONID, ID, settingID]
        CanBusSend(NODEID, DATA)

    def Menus(self, parent, app):
        self.menu = Menu(parent, background="grey50", fg=black)
        self.fileMenu = Menu(self.menu)
        self.graphs = Menu(self.menu)
        self.graphMenu1 = Menu(self.menu)
        self.graphMenu2 = Menu(self.menu)
        self.graphMenu3 = Menu(self.menu)
        self.graphMenu4 = Menu(self.menu)
        self.SetPoints = Menu(self.menu)
        self.TeensyNodes = Menu(self.menu)
        self.DataRequests = Menu(self.menu)
        self.SensorSets = Menu(self.menu)
        self.AutoSequenceMenu = Menu(self.menu)

        self.graphs.add_cascade(label="Graph 1", menu=self.graphMenu1)
        self.graphs.add_cascade(label="Graph 2", menu=self.graphMenu2)
        self.graphs.add_cascade(label="Graph 3", menu=self.graphMenu3)
        self.graphs.add_cascade(label="Graph 4", menu=self.graphMenu4)
        self.menu.add_cascade(label="Graphs", menu=self.graphs)
        self.menu.add_cascade(label="Set Points", menu=self.SetPoints)
        self.menu.add_cascade(label="Teensy Nodes", menu=self.TeensyNodes)
        self.menu.add_cascade(label="Data Requests", menu=self.DataRequests)

        self.AutoSequenceMenu.add_command(label="Reset", command=lambda: self.AutoSequenceReset())
        self.AutoSequenceMenu.add_command(label="Count Down Start", command=lambda: self.AutoSequenceSettings())

        self.SetPoints.add_command(label="Valves", command=lambda: self.ValveSettingsPopUp())
        self.SetPoints.add_command(label="Sensors", command=lambda: self.SensorSettingsPopUp())
        self.SetPoints.add_cascade(label="Auto Sequence", menu=self.AutoSequenceMenu)
        self.SetPoints.add_command(label="Controllers", command=lambda: self.ControllerSettingsPopUp())

        self.TeensyNodes.add_command(label="Teensy Node Reset", command=lambda: self.NodeReset())

        app.config(menu=self.menu)

        for sensor in self.sensorList:
            self.graphMenu1.add_checkbutton(label=sensor.args[0], variable=sensor.Graph1Status)
            self.graphMenu2.add_checkbutton(label=sensor.args[0], variable=sensor.Graph2Status)
            self.graphMenu3.add_checkbutton(label=sensor.args[0], variable=sensor.Graph3Status)
            self.graphMenu4.add_checkbutton(label=sensor.args[0], variable=sensor.Graph4Status)

    def run(self):  # This takes place of the init
        """ TKinter Initialization"""
        self.root = Tk()
        self.appMainScreen = Toplevel(self.root)
        self.appMainScreen.configure(background=black)
        self.appMainScreen.geometry("1920x1080")

        self.appSecondScreen = Toplevel(self.root)
        self.appSecondScreen.configure(background=black)
        self.appSecondScreen.geometry("1920x1080+1920+0")

        """ Main Canvas Initialization"""
        self.parentMainScreen = Canvas(self.appMainScreen, bg=black, highlightbackground=black, highlightthickness=0)
        self.parentMainScreen.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.parentSecondScreen = Canvas(self.appSecondScreen, bg=black, highlightbackground=black,
                                         highlightthickness=0)
        self.parentSecondScreen.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        
        self.VehicleState = Label(self.parentMainScreen, text="Vehicle State", fg=orange, bg=black, font=("Arial", 25))
        self.VehicleState.place(relx=.01, rely=0.025, relheight=1 / 30)
        self.MissionState = Label(self.parentMainScreen, text="Mission State", fg=orange, bg=black, font=("Arial", 25))
        self.MissionState.place(relx=.01, rely=0.075, relheight=1 / 30)
        
        self.imagePlacement()
        self.propLinePlacement()
        self.AutoSequence()
        self.StateReset()
        self.graphs()
        self.Vent = States(self.parentMainScreen, Main.Vent)
        self.Vent.VentAbortInstantiation()
        self.Abort = States(self.parentMainScreen, Main.Abort)
        self.Abort.VentAbortInstantiation()
        # Instantiates Every Valve
        for valve in Main.valves:
            self.valveList.append(Valves(self.parentMainScreen, valve, self.parentSecondScreen))

        # Instantiates Every Sensor
        for sensor in Main.sensors:
            self.sensorList.append(Sensors(self.parentMainScreen, sensor, self.parentSecondScreen))

#         # Instantiates Every Controller
#         for controller in Main.Controllers:
#             self.controllerList.append(Controller(controller, self.parentMainScreen, self.parentSecondScreen))

        self.Menus(self.parentMainScreen, self.appMainScreen)
        self.Menus(self.parentSecondScreen, self.appSecondScreen)

        self.time = Label(self.parentMainScreen, fg="Orange", bg=black,
                          text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), font=("Verdana", 17))
        self.time.place(relx=.85, rely=0.01)

        self.ManualOverridePhoto = PhotoImage(file="GUI Images/ManualOverrideDisabledButton.png")
        self.ManualOverrideButton = Button(self.parentMainScreen, image=self.ManualOverridePhoto, fg='red', bg='black',
                                           bd=5)
        self.ManualOverrideButton.place(relx=.7, rely=0.2)
        self.ManualOverrideButton.bind('<Double-1>', self.ManualOverride)  # bind double left clicks

        self.parentSecondScreen.create_rectangle(550, 10, 1100, 550, outline=orange, fill="black", width=5)
        self.parentSecondScreen.create_rectangle(10, 10, 525, 550, outline=orange, fill="black", width=5)
        self.parentSecondScreen.create_rectangle(10, 600, 525, 1000, outline=orange, fill="black", width=5)
        self.parentSecondScreen.create_rectangle(550, 600, 1100, 1000, outline=orange, fill="black", width=5)

        self.NodeState1 = Label(self.parentSecondScreen, text="Node State 1", fg=orange, bg=black, font=("Arial", 25))
        self.NodeState1.place(relx=.1, rely=.6, relheight=1 / 30)
        self.NodeState2 = Label(self.parentSecondScreen, text="Node State 2", fg=orange, bg=black, font=("Arial", 25))
        self.NodeState2.place(relx=.4, rely=.6, relheight=1 / 30)
        
        self.parentMainScreen.create_rectangle(10, 160, 275, 1020, outline=orange, fill="black", width=5)

        # RefreshLabel() Refreshes the Readings
        self.Refresh()

        """ Runs GUI Loop"""
        self.appMainScreen.attributes("-fullscreen",
                                      True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen
        self.appMainScreen.bind("<Escape>",
                                lambda event: self.appMainScreen.destroy())  # binds escape key to killing the window
        self.appMainScreen.bind("<F11>",
                                lambda event: self.appMainScreen.attributes("-fullscreen",
                                                                            True))  # switches from zoomed to fullscreen
        self.appMainScreen.bind("<F12>",
                                lambda event: self.appMainScreen.attributes("-fullscreen",
                                                                            False))  # switches from fullscreen to zoomed

        self.appSecondScreen.attributes("-fullscreen",
                                        False)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen
        self.appSecondScreen.bind("<Escape>", lambda
            event: self.appSecondScreen.destroy())  # binds escape key to killing the window
        self.appSecondScreen.bind("<F11>",
                                  lambda event: self.appSecondScreen.attributes("-fullscreen",
                                                                                True),
                                  lambda event: self.appSecondScreen.geometry(
                                      "1920x1080-1920+0"))  # switches from zoomed to fullscreen
        # self.appSecondScreen.bind("<F11>",
        #                           lambda event: self.appSecondScreen.geometry("1920x1080-1920+0"))  # switches from zoomed to fullscreen

        self.appSecondScreen.bind("<F12>",
                                  lambda event: self.appSecondScreen.attributes("-fullscreen",
                                                                                False))  # switches from fullscreen to zoomed
        self.root.withdraw()

        self.root.mainloop()
        #self.appMainScreen.mainloop()


class Sensors:
    numOfSensors = 0

    def __init__(self, parent, args, SecondScreen):
        self.parent = parent
        self.SecondScreen = SecondScreen
        self.args = args
        self.idRaw = args[5]
        self.idConv = self.idRaw + 1
        self.idConvEma = self.idConv + 256
        self.idFake = self.idRaw + 100

        self.color = args[7]
        self.sensorData = [0] * 100
        self.Graph1Status = IntVar()
        self.Graph2Status = IntVar()
        self.Graph3Status = IntVar()
        self.Graph4Status = IntVar()
        self.index = 0
        self.name = args[0]
        # self.dataList = []

        aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        self.label = Label(parent, text=args[0], font=aFont, fg=self.color, bg='black')
        self.label.place(relx=args[1], rely=args[2], anchor="nw")
        # Makes label with the reading for its corresponding sensor
        self.ReadingLabel = Label(parent, text="N/A", font=("Verdana", 12), fg='orange', bg='black')
        self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")

        self.label2 = Label(SecondScreen, text=args[0], font=aFont, fg=self.color, bg='black')
        self.label2.place(relx=Sensors.numOfSensors % 2 * .125 + .025, rely=(Sensors.numOfSensors // 2) * .075 + .05,
                          anchor="nw")
#         self.RawReadingLabel2 = Label(SecondScreen, text="N/A Raw", font=("Verdana", 9), fg='orange', bg='black')
#         self.RawReadingLabel2.place(relx=Sensors.numOfSensors % 2 * .125 + .025 + .05,
#                                     rely=(Sensors.numOfSensors // 2) * .075 + .05 + .0125, anchor="nw")
        self.ConvReadingLabel2 = Label(SecondScreen, text="N/A Converted", font=("Verdana", 9), fg='orange', bg='black')
        self.ConvReadingLabel2.place(relx=Sensors.numOfSensors % 2 * .125 + .025 + .05,
                                     rely=(Sensors.numOfSensors // 2) * .075 + .05, anchor="nw")

        Sensors.numOfSensors += 1

    def resetAll(self, var, label):
        print("Node ID: ", 8)
        print("Byte 0", "Verification ID: ", "IDK")
        print("Byte 1", "Object ID: ", self.idRaw)
        print("Byte 2", "Setting ID: ", 1)
        settingID = 0
        DATA = [VERIFICATIONID, self.idRaw, settingID, ]
        CanBusSend(NODEID, DATA)
        label.config(text="Command Sent!", fg="green")

    def setSampleRate(self, var, label):
        print("hi")
        val = var.get()
        if isinstance(val, str):
            print(val.upper())
            if val.upper() == "SLOW":
                settingID = 1
                print("Node ID: ", 8)
                print("Byte 0", "Verification ID: ", "IDK")
                print("Byte 1", "Object ID: ", self.idRaw)
                print("Byte 2", "Setting ID: ", 1)
                print("Byte 3", "Setting Bytes: ", 0)
                print(self.name)
                DATA = [VERIFICATIONID, self.idRaw, settingID, ]
                CanBusSend(NODEID, DATA)
            elif val.upper() == "MEDIUM":
                settingID = 2
                print("Node ID: ", 8)
                print("Byte 0", "Verification ID: ", "IDK")
                print("Byte 1", "Object ID: ", self.idRaw)
                print("Byte 2", "Setting ID: ", 1)
                print("Byte 3", "Setting Bytes: ", 0)
                print(self.name)
                DATA = [VERIFICATIONID, self.idRaw, settingID, ]
                CanBusSend(NODEID, DATA)
            elif val.upper() == "Fast":
                settingID = 3
                print("Node ID: ", 8)
                print("Byte 0", "Verification ID: ", "IDK")
                print("Byte 1", "Object ID: ", self.idRaw)
                print("Byte 2", "Setting ID: ", 1)
                print("Byte 3", "Setting Bytes: ", 0)
                print(self.name)
                DATA = [VERIFICATIONID, self.idRaw, settingID, ]
                CanBusSend(NODEID, DATA)

        else:
            print(val)

    def setAlphaEMA(self, var, label):
        settingID = 4
        if self.intTypeCheck(var, int, label, 8):
            binstr = bitstring.BitArray(int=int(var.get()), length=8).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.idRaw)
            print("Byte 2", "Setting ID: ", 4)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.idRaw, settingID, int(binstr[0:8], 2)]
            CanBusSend(NODEID, DATA)

    def intTypeCheck(self, var, type, label, size):
        num = var.get()
        if type == int:
            if isint(num):
                try:
                    binstr = bitstring.BitArray(int=int(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nInteger Number is required as Input", fg="red")
                return False
        elif type == float:
            if isfloat(num):
                try:
                    binstr = bitstring.BitArray(float=float(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nDecimal Value is required as Input", fg="red")
                return False

    # Updates the reading
    # Gets called by the PropulsionFrame class
    def Refresh(self, LabelRefresh):
        value = random.randint(1, 100)
        if CanStatus:
            value = CanReceive.Sensors[self.idConv]
        self.sensorData = self.sensorData[1:] + self.sensorData[:1]
        self.sensorData[-1] = value
        self.index += 1
        if LabelRefresh:
            self.ReadingLabel.config(fg=orange,text=str(value) + " psi")  # Updates the label with the updated value
            self.ConvReadingLabel2.config(fg=orange,text=str(value) + " psi") 

class Valves:
    numOfValves = 0

    def __init__(self, parent, args, SecondScreen):
        self.parent = parent
        self.SecondScreen = SecondScreen
        self.args = args
        self.state = False
        self.photo_name = args[0]
        self.status = 0  # Keeps track of valve actuation state

        self.name = args[0]
        self.x_pos = args[1]
        self.y_pos = args[2]
        self.id = args[3]
        self.commandID = 1
        self.HPChannel = args[4]
        self.commandOFF = args[5]
        self.commandON = args[6]
        self.color = args[7]
        
        if "IGN" in self.photo_name:
            self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Off-EnableOn.png").subsample(2)
        else:
            self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Closed-EnableOn.png").subsample(2)
        self.Button = Button(parent, font=("Verdana", 10), fg='red', bg='black')
        self.Button.place(relx=self.x_pos, rely=self.y_pos)
        self.Button.config(image=self.photo)
        self.Button.bind('<Double-1>', self.ValveActuation)

        aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        self.label2 = Label(SecondScreen, text=args[0], font=aFont, fg=self.color, bg='black')
        self.label2.place(relx=Valves.numOfValves % 2 * .1 + .3,
                          rely=(Valves.numOfValves // 2) * .075 + .05, anchor="nw")
        self.StatusLabel2 = Label(SecondScreen, text="N/A Status", font=("Verdana", 9), fg='orange', bg='black')
        self.StatusLabel2.place(relx=Valves.numOfValves % 2 * .1 + .3 + .025,
                                    rely=(Valves.numOfValves // 2) * .075 + .05 + .0125,
                                    anchor="nw")
        self.VoltageLabel2 = Label(SecondScreen, text="N/A Voltage", font=("Verdana", 9), fg='orange', bg='black')
        self.VoltageLabel2.place(relx=Valves.numOfValves % 2 * .1 + .3 + .025,
                                     rely=(Valves.numOfValves // 2) * .075 + .05 - .0125,
                                     anchor="nw")
        Valves.numOfValves += 1

    def ValveActuation(self, event):
        # User is only allowed to actuate valves if in Test mode
        if Main.CurrState != "Test" and Main.CurrState != "Override":
            return 0
        print(self.name, self.status)
        if self.state:
#             if "IGN" in self.photo_name:
#                 self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Off-EnableOn.png")  # .subsample(2)
#             else:
#                 self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Closed-EnableOn.png")  # .subsample(2)
# 
#             self.Button = Button(self.parent, image=self.photo, fg='red', bg='black', bd=5)
#             self.Button.config(image=self.photo)

            #self.state = False
            DATA = [self.commandOFF]
            CanBusSend(self.commandID, DATA)
        else:
#             if "IGN" in self.photo_name:
#                 self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Off-EnableOn.png")  # .subsample(2)
#             else:
#                 self.photo = PhotoImage(file="Valve Buttons/" + self.name + "-Open-EnableOn.png")  # .subsample(2)
#             self.Button = Button(self.parent, image=self.photo, fg='green', bg='black', bd=5)
#             self.Button.config(image=self.photo)
            #self.state = True
            DATA = [self.commandON]
            CanBusSend(self.commandID, DATA)
        #self.Button.place(relx=self.x_pos, rely=self.y_pos)
        # On double press, Call ValveActuaction function
        #self.Button.bind('<Double-1>', self.ValveActuation)

    def resetAll(self, var, label):
        print("Node ID: ", 8)
        print("Byte 0", "Verification ID: ", "IDK")
        print("Byte 1", "Object ID: ", self.id)
        print("Byte 2", "Setting ID: ", 1)
        settingID = 0
        DATA = [VERIFICATIONID, self.id, settingID]
        CanBusSend(NODEID, DATA)
        label.config(text="Command Sent!", fg="green")

    def setValveType(self, var, label):
        settingID = 1
        val = var.get()
        if isinstance(val, str):
            print(val.upper())
            if val.upper() == "NORMALLY CLOSED":
                print("Node ID: ", 8)
                print("Byte 0", "Verification ID: ", "IDK")
                print("Byte 1", "Object ID: ", self.id)
                print("Byte 2", "Setting ID: ", 1)
                print("Byte 3", "Setting Bytes: ", 0)
                print(self.name)
                DATA = [VERIFICATIONID, self.id, settingID, 0]
                CanBusSend(NODEID, DATA)
            elif val.upper() == "NORMALLY OPEN":
                print("Node ID: ", 8)
                print("Byte 0", "Verification ID: ", "IDK")
                print("Byte 1", "Object ID: ", self.id)
                print("Byte 2", "Setting ID: ", 1)
                print("Byte 3", "Setting Bytes: ", 0)
                print(self.name)
                DATA = [VERIFICATIONID, self.id, settingID, 1]
                CanBusSend(NODEID, DATA)

    def setFullDutyTime(self, var, label):
        settingID = 2
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 2)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setFullDutyCyclePWM(self, var, label):
        settingID = 3
        if self.intTypeCheck(var, int, label, 16):
            binstr = bitstring.BitArray(int=int(var.get()), length=16).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 3)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2)]
            CanBusSend(NODEID, DATA)

    def setHoldDutyCyclePWM(self, var, label):
        settingID = 4
        if self.intTypeCheck(var, int, label, 8):
            binstr = bitstring.BitArray(int=int(var.get()), length=8).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 4)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2)]
            CanBusSend(NODEID, DATA)

    def setWarmDutyCyclePWM(self, var, label):
        settingID = 5
        if self.intTypeCheck(var, int, label, 16):
            binstr = bitstring.BitArray(int=int(var.get()), length=16).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 5)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2)]
            CanBusSend(NODEID, DATA)

    def setLiveOutTime(self, var, label):
        settingID = 1
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 5)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def intTypeCheck(self, var, type, label, size):
        num = var.get()
        if type == int:
            if isint(num):
                try:
                    binstr = bitstring.BitArray(int=int(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nInteger Number is required as Input", fg="red")
                return False
        elif type == float:
            if isfloat(num):
                try:
                    binstr = bitstring.BitArray(float=float(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nDecimal Value is required as Input", fg="red")
                return False

    def refresh_valve(self):
        # if self.id in can_receive.node_state and self.status is not can_receive.node_state[self.id]:
        #     self.status = can_receive.node_state[self.id]
        if CanStatus:
            self.status = CanReceive.Valves[self.HPChannel]
            self.VoltageLabel2.config(text = CanReceive.Sensors[self.args[8]])
            if self.status == 0:  # Closed
                self.photo_name = "Valve Buttons/" + self.name + "-Closed-EnableStale.png"
                self.StatusLabel2.config(text  = "Closed")
                self.state = False
            elif self.status == 1:  # Open
                self.photo_name = "Valve Buttons/" + self.name + "-Open-EnableStale.png"
                self.StatusLabel2.config(text  = "Open`")
                self.state = True
            elif self.status == 2:
                self.photo_name = "Valve Buttons/" + self.name + "-FireCommanded-EnableStale.png"
            #             elif can_receive.currRefTime - can_receive.node_state_time[self.id] >= can_receive.staleTimeThreshold:
            #                 self.photo_name = "Valve Buttons/" + self.name + "-Stale-EnableStale.png"
            if not exists(self.photo_name):
                pass
                #print(self.photo_name + " Does not exist. Status is " + str(self.status))
            else:
                #print(self.photo_name, self.status)
                self.photo = PhotoImage(file=self.photo_name)
                self.Button.config(image=self.photo)
    

class States:

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
        self.relXCor = 0
        self.relYCor = 0
        self.relHeight = 1
        self.relWidth = 1
        self.bgColor = "black"
        self.fontSize = ("Verdana", 10)

    # The Main state buttons get made here
    def MainStateInstantiation(self):
        self.aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        self.relXCor = 0.0125
        self.relHeight = 7/ len(Main.States)/10
        self.relYCor = 1 - (self.relHeight * 1.15) * (len(Main.States) - self.StateNumber + 1) - .025
        self.relWidth = 0.125
        self.bgColor = "black"
        self.isVentAbort = False
        # Goes to logic function when button is pressed
        self.button = Button(self.parent, text=self.args[0], fg='red', bg='black', bd=5,
                             command=lambda: self.Logic(), font=20)  # , font = self.fontSize)
        self.button.place(relx=self.relXCor, rely=self.relYCor, relwidth=self.relWidth, relheight=self.relHeight)

    # The Vent and abort buttons are made here
    def VentAbortInstantiation(self):
        self.relXCor = self.args[1]
        self.relYCor = 0.85
        self.relHeight = .1
        self.relWidth = 1 / 10
        self.bgColor = darkGrey
        self.fontSize = ("Verdana", 26)
        self.isVentAbort = True
        self.button = Button(self.parent, text=self.args[0], command=lambda: self.StateActuation(), fg='red',
                             bg=darkGrey, font=self.fontSize, bd=5)  # , font=self.fontSize)
        self.button.place(relx=self.relXCor, rely=self.relYCor, relheight=self.relHeight, relwidth=self.relWidth)

    # Holds the logic for the state commands and the transition between the states
    # If in Test mode System leaves passive state and cant go into the other states until user has left Test mode
    # The transition between each state can only be done sequentially but Arm states can go back to its previous state
    # If user input follows the specified logic the State Actuaction function is called and it updated the UI buttons

    # Logic for Vent and Abort currently not done
    def Logic(self):
        if self.stateName == "Test":
            if Main.CurrState == "Passive":
                Main.CurrState = "Test"
                self.StateActuation()
            elif Main.CurrState == "Test":
                Main.CurrState = "Passive"
                self.StateActuation()
            else:
                return 0
        elif Main.CurrState != "Test":
            if self.prevState.stateName == Main.CurrState or (
                    Main.CurrState == "Passive" and self.prevState.stateName == "Test"):
                self.StateActuation()
                if self.prevState.stateName != "Test":
                    self.prevState.StateActuation()
                Main.CurrState = self.stateName
            elif Main.CurrState == self.stateName and self.isArmState:
                self.prevState.StateActuation()
                self.StateActuation()
                Main.CurrState = self.prevState.stateName

    # Updates the visuals in the UI to specify whether a state is on or off
    # red if OFF and green if ON
    def StateActuation(self):
        print(self.stateName)
        if self.state:
            self.button.config(fg='red')
            if self.isVentAbort:
                GUI.StateReset()
            self.state = False
            DATA = [self.commandOFF]
            CanBusSend(self.commandID, DATA)
        else:
            self.button.config(fg='green')
            self.state = True
            DATA = [self.commandON]
            CanBusSend(self.commandID, DATA)


class Controller:
    TankControllers = 0

    def __init__(self, args, Screen1, Screen2):
        self.name = args[0]
        self.id = args[1]
        self.isAPropTank = args[2]
        self.parentMain = Screen1
        self.parent2 = Screen2
        self.color = args[3]
        aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        if self.isAPropTank:
            self.KpLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Kp")
            self.KpLabel.place(relx=.01, rely=0.5 + Controller.TankControllers * .2)
            self.KiLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Ki")
            self.KiLabel.place(relx=.05, rely=0.5 + Controller.TankControllers * .2)
            self.KdLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Kd")
            self.KdLabel.place(relx=.1, rely=0.5 + Controller.TankControllers * .2)
            self.EpLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Ep")
            self.EpLabel.place(relx=.15, rely=0.5 + Controller.TankControllers * .2)
            self.EiLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Ei")
            self.EiLabel.place(relx=.2, rely=0.5 + Controller.TankControllers * .2)
            self.EdLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Ed")
            self.EdLabel.place(relx=.25, rely=0.5 + Controller.TankControllers * .2)
            self.PIDSUMLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="PID SUM")
            self.PIDSUMLabel.place(relx=.3, rely=0.5 + Controller.TankControllers * .2)
            self.TargetValueLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Target Value")
            self.TargetValueLabel.place(relx=.35, rely=0.5 + Controller.TankControllers * .2)
            self.ThresholdLabel = Label(self.parent2, fg=self.color, bg=black, font=aFont, text="Threshold")
            self.ThresholdLabel.place(relx=.45, rely=0.5 + Controller.TankControllers * .2)
            self.KpLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.KpLabel2.place(relx=.01, rely=0.55 + Controller.TankControllers * .2)
            self.KiLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.KiLabel2.place(relx=.05, rely=0.55 + Controller.TankControllers * .2)
            self.KdLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.KdLabel2.place(relx=.1, rely=0.55 + Controller.TankControllers * .2)
            self.EpLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.EpLabel2.place(relx=.15, rely=0.55 + Controller.TankControllers * .2)
            self.EiLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.EiLabel2.place(relx=.2, rely=0.55 + Controller.TankControllers * .2)
            self.EdLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.EdLabel2.place(relx=.25, rely=0.55 + Controller.TankControllers * .2)
            self.PIDSUMLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.PIDSUMLabel2.place(relx=.3, rely=0.55 + Controller.TankControllers * .2)
            self.TargetValueLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.TargetValueLabel2.place(relx=.35, rely=0.55 + Controller.TankControllers * .2)
            self.ThresholdLabel2 = Label(self.parent2, font=("Verdana", 9), fg='orange', bg='black', text="NA")
            self.ThresholdLabel2.place(relx=.45, rely=0.55 + Controller.TankControllers * .2)
            Controller.TankControllers += 1

        # self.EMA.place(relx=.01, rely=0.575, relwidth=1 / 10, relheight=.02)

    def resetAll(self, var, label):
        settingID = 0
        DATA = [VERIFICATIONID, self.id, settingID]
        CanBusSend(NODEID, DATA)
        label.config(text="Command Sent!", fg="green")

    def setFuelMVAutosequenceActuation(self, var, label):
        settingID = 1
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 1)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, 1]
            CanBusSend(NODEID, DATA)

    def setLoxMVAutosequenceActuation(self, var, label):
        settingID = 2
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, 1]
            CanBusSend(NODEID, DATA)

    def setIgniter1ActuationActuation(self, var, label):
        settingID = 3
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 1)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, 1]
            CanBusSend(NODEID, DATA)

    def setIgniter2ActuationActuation(self, var, label):
        settingID = 4
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 1)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, 1]
            CanBusSend(NODEID, DATA)

    def setThrottleProgramPoint(self, var, label):
        settingID = 5
        if self.intTypeCheck(var, int, label, 16):
            binstr = bitstring.BitArray(int=int(var.get()), length=16).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 5)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2)]
            CanBusSend(NODEID, DATA)

    def throttleProgramReset(self, var, label):
        settingID = 6
        DATA = [VERIFICATIONID, self.id, settingID]
        CanBusSend(NODEID, DATA)
        label.config(text="Command Sent!", fg="green")

    def throttleProgramResetSpecific(self, var, label):
        settingID = 7
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setK_p(self, var, label):
        settingID = 1
        if self.intTypeCheck(var, float, label, 32):
            binstr = bitstring.BitArray(float=float(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setK_i(self, var, label):
        settingID = 2
        if self.intTypeCheck(var, float, label, 32):
            binstr = bitstring.BitArray(float=float(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setK_d(self, var, label):
        settingID = 3
        if self.intTypeCheck(var, float, label, 32):
            binstr = bitstring.BitArray(float=float(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 2)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setControllerThreshold(self, var, label):
        settingID = 4
        if self.intTypeCheck(var, float, label, 32):
            binstr = bitstring.BitArray(float=float(var.get()), length=32).bin
            print("Node ID: ", 8)
            print("Byte 0", "Verification ID: ", "IDK")
            print("Byte 1", "Object ID: ", self.id)
            print("Byte 2", "Setting ID: ", 2)
            print("Byte 3", "Setting Bytes: ", int(binstr[0:8], 2))
            print("Byte 4", "Setting Bytes: ", int(binstr[8:16], 2))
            print("Byte 5", "Setting Bytes: ", int(binstr[16:24], 2))
            print("Byte 6", "Setting Bytes: ", int(binstr[24:32], 2))
            print(self.name)
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setVentFailsafePressure(self, var, label):
        settingID = 5
        if self.intTypeCheck(var, float, label, 32):
            binstr = bitstring.BitArray(float=float(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setValveMinimumEnergizeTime(self, var, label):
        settingID = 6
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin

            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setValveMinimumDeenergizeTime(self, var, label):
        settingID = 7
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin
            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def setCountdownStart(self, var, label):
        settingID = 2
        if self.intTypeCheck(var, int, label, 32):
            binstr = bitstring.BitArray(int=int(var.get()), length=32).bin

            DATA = [VERIFICATIONID, self.id, settingID, int(binstr[0:8], 2), int(binstr[8:16], 2),
                    int(binstr[16:24], 2), int(binstr[24:32], 2)]
            CanBusSend(NODEID, DATA)

    def intTypeCheck(self, var, type, label, size):
        num = var.get()
        if type == int:
            if isint(num):
                try:
                    binstr = bitstring.BitArray(int=int(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nInteger Number is required as Input", fg="red")
                return False
        elif type == float:
            if isfloat(num):
                try:
                    binstr = bitstring.BitArray(float=float(num), length=size).bin
                    label.config(text="Command Sent!", fg="green")
                    return True
                except bitstring.CreationError as e:
                    label.config(text=e, fg="red")
                    return False
            else:
                label.config(text="Invalid Type.\nDecimal Value is required as Input", fg="red")
                return False

    def Refresh(self):
        if self.isAPropTank:
            if CanStatus:
                self.KpLabel2.config(text=CanReceive.Controllers[self.id][2])
                self.KiLabel2.config(text=CanReceive.Controllers[self.id][3])
                self.KdLabel2.config(text=CanReceive.Controllers[self.id][4])
                self.EpLabel2.config(text=round(CanReceive.Controllers[self.id][6]))
                self.EiLabel2.config(text=round(CanReceive.Controllers[self.id][8]))
                self.EdLabel2.config(text=round(CanReceive.Controllers[self.id][10]))
                self.PIDSUMLabel2.config(text=CanReceive.Controllers[self.id][13])
                self.TargetValueLabel2.config(text=CanReceive.Controllers[self.id][12])
                self.ThresholdLabel2.config(text=CanReceive.Controllers[self.id][5])


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


"""
Starts Code
"""
GUI = Main()
# GUI.run()
GUIThread = Thread(target=GUI.run)
GUIThread.daemon = True
if CanStatus:
    can_receive = CanReceive()
    can_receive_thread = Thread(target=can_receive.run)
    can_receive_thread.daemon = True
#
GUIThread.start()
if CanStatus:
    can_receive_thread.start()
