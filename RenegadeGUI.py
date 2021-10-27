import tkinter as tk
from threading import Thread
import time
import datetime
import random
from tkinter import font as tkFont  # for font size
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk
# All Can bus lines will have the bottom dash lines to help show which lines to
# uncomment when on Pi or comment out when on a computer
import can  #/////////////////////////////////////////////////////////////////////////
# from CanSend import CanSend
from CanRecieve import CanRecieve
bus = can.interface.Bus(channel= 'can0', bustype='socketcan_ctypes')  #///////////////

# The style of graph matplotlib will be using
style.use('dark_background')

# PGSEbuttonOFF = Image.open("GUI Images/SV circle symbol red png.png")
# PGSEbuttonON = Image.open("GUI Images/SV circle symbol green png.png")

# Main Class, Everything is controlled from here
class Main:
    def run(self):
        # Root for application -----------------------------------------------------------------------------------
        root = tk.Tk()

        # Main Frame --------------------------------------------------------------------------------------------
        # All the frames will be placed inside the main frame
        mainFrame = tk.Frame(root, bg="Black", bd=5)
        mainFrame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Each Frame has its own class
        # Top Frame --------------------------------------------------------------------------------------------
        # Contains all the telemetry data
        topFrame = TopFrame(mainFrame)
        # Time Frame --------------------------------------------------------------------------------------------
        # Displays the current time
        timeFrame = TimeFrame(mainFrame)
        # Left Frame --------------------------------------------------------------------------------------------
        # Contains all the Operational States
        leftFrame = LeftFrame(mainFrame)
        # Right Frame --------------------------------------------------------------------------------------------
        # Contains Several Graphs
        rightFrame = RightFrame(mainFrame)
        # Center Frame --------------------------------------------------------------------------------------------
        # Displays the Propulsion Feed System
        # Displays the actuation state of individual valves and sensor readings
        # Allows for access to actuate individual valves when system is in Test mode
        # Getting the png to show wasnt working when inside the class, so i brought it out to main class
        # to then give the Center Class the frame with the PNG already on it
        centerFrame = tk.Frame(mainFrame, bg="Black")
        centerFrame.place(relx=0.11, rely=0.2, relwidth=0.7, relheight=0.65)
        # # Put schematic draft for layout
        # schematicImage = tk.PhotoImage(file="Images\GUI Prop Layout.png")
        # schematicLabel = tk.Label(centerFrame, image=schematicImage, bg="black")
        # schematicLabel.place(relx=0, rely=0, relwidth=1, relheight=1)
        center = CenterFrame(centerFrame)
        # Bottom Frame --------------------------------------------------------------------------------------------
        # Bottom Frame Getting the png to show wasnt working when inside the class, so i brought it out to main class
        # to then give the Bottom Class the frame with the PNG already on it
        # Bottom Frame takes in the left frame to allow for the Vent and Abort functions to modify the states in the
        # left frame
        bottomFrame = tk.Frame(mainFrame, bg="Black")
        bottomFrame.place(relx=0.14, rely=0.85, relwidth=0.65, relheight=0.2)


        # Graphics import and placements -----------------------------------------------------------------------   
#         RenegadeLOGOSAD = tk.PhotoImage(file="/home/pi/Documents/GUI Images/Sad Renegade LOGO.png")
#         logo2 = tk.Label(bottomFrame, image=RenegadeLOGOSAD, bg = "black")
#         logo2.place(relx=0.315, rely='-.1250')        
        
        RenegadeLOGO = tk.PhotoImage(file="GUI Images/RenegadeLogoSmall.png")
        logo1 = tk.Label(bottomFrame, image=RenegadeLOGO, bg = "black")
        logo1.place(relx=.415, rely='-.1250')
        
        engineart = tk.PhotoImage(file="GUI Images/Engine Clipart smol.png")
        logo2 = tk.Label(centerFrame, image=engineart, bg = "black")
        logo2.place(relx=.735, rely=.40)
        
        LOXTankart = tk.PhotoImage(file="GUI Images/TankPlainClipart.png")
        logo3 = tk.Label(centerFrame, image=LOXTankart, bg = "black")
        logo3.place(relx=.475, rely=.2)
        
        FuelTankart = tk.PhotoImage(file="GUI Images/TankPlainClipart.png")
        logo4 = tk.Label(centerFrame, image=FuelTankart, bg = "black")
        logo4.place(relx=.475, rely=.615)
        
        COPVTankart = tk.PhotoImage(file="GUI Images/TankPlainClipartCOPV.png")
        logo5 = tk.Label(centerFrame, image=COPVTankart, bg = "black")
        logo5.place(relx=.0, rely=.0)
        
        DomeRegart = tk.PhotoImage(file="GUI Images/AquaDomeReg Clipart.png")
        logo6 = tk.Label(centerFrame, image=DomeRegart, bg = "black")
        logo6.place(relx=.25, rely=.185)
        logo7 = tk.Label(centerFrame, image=DomeRegart, bg = "black")
        logo7.place(relx=.25, rely=.5)
        
        
        bottom = BottomFrame(bottomFrame, leftFrame)

        # Matplotlib Refresh Function call -----------------------------------------------------------------------
        # Calls the animation function and refreshes the matplotlib graphs every 1000 ms (1 second)
        ani1 = animation.FuncAnimation(f1,animate, interval=1000)
        ani2 = animation.FuncAnimation(f2,animate, interval=1000)
        ani3 = animation.FuncAnimation(f3,animate, interval=1000)
        
        # Start window--------------------------------------------------------------------------------------------
        root.attributes("-zoomed", True) #"zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen
        root.bind("<Escape>", lambda event:root.destroy()) #binds escape key to killing the window
        root.bind("<F11>", lambda event: root.attributes("-fullscreen", True)) #switches from zoomed to fullscreen
        root.bind("<F12>", lambda event: root.attributes("-fullscreen", False)) #switches from fullscreen to zoomed
        
        # Starts the GUI
        root.mainloop()


# Top Frame Class --------------------------------------------------------------------------------------------
class TopFrame:
    # The class takes in the parent Frame (Main Frame) as an input
    def __init__(self, parent):
        # Make the Top Frame
        topFrame = tk.Frame(parent, bg="black", bd=5)
        # Places the Top Frame
        # Coordinates are relative to the Main Frame
        topFrame.place(relx=0.405, rely=0, relwidth=.825, relheight=0.2, anchor="n")

        # Make sub Frames for each Telemetry Node It is seperated into individual Nodes for future proofing since
        # they may all be operated differently in the future
        telemetryFrame = self.TelemetryNode(topFrame)
        upperPropSystemFrame = self.UpperPropSystemNode(topFrame)
        engineFrame = self.EngineNode(topFrame)
        padGroundFrame = self.PadGroundNode(topFrame)

    # Currently all Nodes follow the same code structure
    class TelemetryNode:
        def __init__(self, parent):
            # Makes Frame
            # Coordinates are relative to the Top Frame --------------------------------------------------------------
            telemetryframe = tk.Frame(parent, bg="grey", bd=5)
            telemetryframe.place(relx=0, rely=0, relwidth=(1 / 4.1), relheight=1)

            # Coordinates are relative to the Top Frame --------------------------------------------------------------
            # Makes 4 labels and then stores them in a list
            telemetryLabels = [0] * 4
            for i in range(4):
                telemetryLabels[i] = tk.Label(telemetryframe, text="", bg="grey", anchor="w")
                telemetryLabels[i].place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            # Gives each label a text
            telemetryLabels[0]["text"] = "Telemetry Node"
            telemetryLabels[1]["text"] = "Activity: "
            telemetryLabels[2]["text"] = "Temp: "
            telemetryLabels[3]["text"] = "Bus Info"

            # Shows the current state of the node
            nodeState = tk.Label(telemetryframe, text="State", bg="black", fg="white")
            nodeState.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)
            # Reset button
            resetButton = tk.Button(telemetryframe, text="Reset", command=lambda: Reset(), font=("Verdana", 10),
                                    fg='black', bg='white')
            resetButton.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)

    class UpperPropSystemNode:
        def __init__(self, parent):
            upperPropSystemframe = tk.Frame(parent, bg="grey", bd=5)
            upperPropSystemframe.place(relx=(1 / 4 + 0.0015), rely=0, relwidth=(1 / 4.1), relheight=1)

            upperPropSystemLabels = [0] * 4
            for i in range(4):
                upperPropSystemLabels[i] = tk.Label(upperPropSystemframe, text="", bg="grey", anchor="w")
                upperPropSystemLabels[i].place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            upperPropSystemLabels[0]["text"] = "Upper Prop System Node"
            upperPropSystemLabels[1]["text"] = "Activity: "
            upperPropSystemLabels[2]["text"] = "MCU Temp: "
            upperPropSystemLabels[3]["text"] = "Bus Info"

            nodeState = tk.Label(upperPropSystemframe, text="pee", bg="black", fg="white")
            nodeState.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

            resetButton = tk.Button(upperPropSystemframe, text="Reset", command=lambda: Reset(), font=("Verdana", 10),
                                    fg='black', bg='white')
            resetButton.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)

    class EngineNode:
        def __init__(self, parent):
            engineframe = tk.Frame(parent, bg="grey", bd=5)
            engineframe.place(relx=(1 / 4 + 0.0015) * 2, rely=0, relwidth=(1 / 4.1), relheight=1)

            engineLabels = [0] * 4
            for i in range(4):
                engineLabels[i] = tk.Label(engineframe, text="NA", bg="grey", anchor="w")
                engineLabels[i].place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            engineLabels[0]["text"] = "Engine Node"
            engineLabels[1]["text"] = "Activity: "
            engineLabels[2]["text"] = "MCU Temp: "
            engineLabels[3]["text"] = "Bus Info"

            nodeState = tk.Label(engineframe, text="poopee", bg="black", fg="white")
            nodeState.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

            resetButton = tk.Button(engineframe, text="Reset", command=lambda: Reset(), font=("Verdana", 10),
                                    fg='black', bg='white')
            resetButton.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)

    class PadGroundNode:
        def __init__(self, parent):
            padGroundframe = tk.Frame(parent, bg="grey", bd=5)
            padGroundframe.place(relx=(1 / 4 + 0.0015) * 3, rely=0, relwidth=(1 / 4.1), relheight=1)

            padGroundLabels = [0] * 4
            for i in range(4):
                padGroundLabels[i] = tk.Label(padGroundframe, text="", bg="grey", anchor="w")
                padGroundLabels[i].place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            padGroundLabels[0]["text"] = "Pad Ground Node"
            padGroundLabels[1]["text"] = "Activity: "
            padGroundLabels[2]["text"] = "MCU Temp: "
            padGroundLabels[3]["text"] = "Bus Info"

            nodeState = tk.Label(padGroundframe, text="peepoo", bg="black", fg="white")
            nodeState.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

            resetButton = tk.Button(padGroundframe, text="Reset", command=lambda: Reset(), font=("Verdana", 10),
                                    fg='black', bg='white')
            resetButton.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)


# Left Frame --------------------------------------------------------------------------------------------
class LeftFrame:
    # Keeps track of the operational state the system is in  ----------------------------------------------------
    #     Standby: System will not actuate any valves
    #       "Passive" or "Active" will be shown to display wether or not this mode is active
    #     Testing: Gives access to user to actuate individual valves
    #     Purge: Dont really know
    #     High Press Press Arm: something about an arms, I thought Dan was into feet tbh
    #     High Press Pressurize: Allows pressure to go into the COPV
    #     Tank Press Arm: I wonder if I can beat Dan in an Arm wrestle??? Right now yes I am soft and weak -Dan When and where? - Pizza
    #     Tank Pressurize: Pressurizes the Tanks and allows the COPV to still recieve pressure to get back filled
    #     Fire Arm: My arms are starting to get tired or writing comments
    #     Fire: Boom Boom Time
    # From Purge to Fire state you cannot actuate any valves unless you override the system by enabling testing mode
    # Testing mode will have to be disabled to continue with the operational States
    # Once in Purge you have entered Terminal countdown and can only go down the list of states.
    # Only way out is through venting or aborting
    # State can be UnArmed by reclicking the Arm button and return to the state before it

    # CurrState Keeps track of the Operational State the system is in
    # It takes in a list of data from the left buttons list corresponding to the state it is in
    # System Boots up in Standby/ Passive, both mean the same thing
    CurrState = ["Standby"]
    # Keeps track of whether or not the Test State is active
    # When Test State is True, User can actuate Individual Valves
    TestState = False

    # Data needed to setup the button for each State
    # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState]
    States = [
        ["Test", 2, 1, 4, 5, False],
        ["Purge", 3, 1, 6, 7, False],
        ["Hi-Press\nPress Arm", 4, 1, 8, 9, True],
        ["Hi-Press\nPressurize", 5, 1, 10, 11, False],
        ["Tank Press \nArm", 6, 1, 12, 13, True],
        ["Tank \nPressurize", 7, 1, 14, 15, False],
        ["Fire Arm", 8, 1, 16, 17, True],
        ["FIRE", 9, 1, 18, 19, False]
    ]

    # The class takes in the parent Frame (Main Frame) as an input
    def __init__(self, parent):
        # Creates the Left Frame
        # Coordinates Relative to Main Frame
        self.leftFrame = tk.Frame(parent, bg="grey", bd=5)
        self.leftFrame.place(relx=0.0001, rely=1 / 5, relwidth=.1, relheight=0.8)

        # Font Size used for some of the labels
        self.fontSize1 = tkFont.Font(size=17)

        # Creates label for Passive/Standby State
        self.passiveState = tk.Label(self.leftFrame, text="Passive", bg="grey", fg="Red", font=self.fontSize1)
        self.passiveState.place(relx=0, rely=0.0125, relwidth=1, relheight=1 / 30)

        # Creates a linked list in where each node only knows about the node before it
        prev = None  # Holds the previous node
        # Iterates though each state in the list of States
        # And then saves it as the previous state to then be given to the next node to be stored
        for state in LeftFrame.States:
            curr = self.State(self.leftFrame, state, prev)
            prev = curr

    # Function is called by the Vent or Abort Buttons
    def VentorAbort(self):
        # Resets every state in in the state list
        prev = None
        for button in LeftFrame.States:
            curr = self.State(self.leftFrame, button, prev)
            prev = curr
        # The system returns to a passive state
        self.passiveState = tk.Label(self.leftFrame, text="Passive", bg="grey", fg="Red", font=self.fontSize1)
        self.passiveState.place(relx=0, rely=0.0125, relwidth=1, relheight=1 / 30)

    # Instantiates each State, Creates the button for each state and holds the logic for the actuation and commands
    # for each state
    class State:
        # Takes in a parent frame (Left Frame), args: list with the data for that state (States)
        # , prev: Previous Node/State
        def __init__(self, parent, args, prev=None):
            self.args = args
            # Creates Button for that State
            # Coordinates Relative to Left Frame
            self.Button = tk.Button(parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                    font=("Verdana", 10), fg='red', bg='black')
            self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 9)

            # commandID, commandOFF, commandON are needed for the Can Commands
            self.commandID = self.args[2]
            self.commandOFF = self.args[3]
            self.commandON = self.args[4]

            self.parent = parent  # Parent Frame
            self.prevState = prev  # Holds the previous node
            self.stateName = args[0]  # Stores the Name of the state
            self.isAnArmState = args[4]  # True is the State is an Arm State

            # Font Size used for some of the labels
            self.fontSize1 = tkFont.Font(size=20)

        # Stores the logic for the transition between States ----------------------------------------------------------
        def StateActuaction(self):
            # If the Current state is not in Test Mode
            # If the Test Mode is not enabled
            #   These may sound redundant but you can be in another state and test mode be enabled for overrides
            #   If Terminal Count has Started (State Purge through Fire), Test mode can be enabled to override the
            #       state conditions if needed
            # If the button pressed is not the Test Button, Test has different logic
            if LeftFrame.CurrState[0] != "Test" and not LeftFrame.TestState and self.stateName != "Test":
                # If the button pressed is the Purge button
                if self.stateName == "Purge":
                    # Shows the Purge State as Enabled/ Green
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                            font=("Verdana", 10), fg='green', bg='black')
                    self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 9)

                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  #////
                    bus.send(msg)  #//////////////////////////////////////////////////////////////////////////////////

                    # The System is now not in a passive State
                    # Changes Label to show that it is now active
                    self.passiveState = tk.Label(self.parent, text="Active", bg="grey", fg="Green", font=self.fontSize1)
                    self.passiveState.place(relx=0, rely=0.0125, relwidth=1, relheight=1 / 30)

                    # Updates the current state to the Purge State
                    LeftFrame.CurrState = self.args

                # If the current state is the same as the state pressed
                # and the state pressed is an Arm State
                # Arm States can be un armed if they pressed again, the current state will be set to the previous state
                elif LeftFrame.CurrState[0] == self.stateName and self.isAnArmState:
                    # Updates the Buttons to show the updated states
                    # Current state gets de-enabled/red
                    # Previous state gets enabled/green
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                            font=("Verdana", 10), fg='red', bg='black')
                    self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 9)
                    self.prevState.Button = tk.Button(self.parent, text=self.prevState.args[0],
                                                      command=lambda: self.prevState.StateActuaction(),
                                                      font=("Verdana", 10), fg='green', bg='black')
                    self.prevState.Button.place(relx=0, rely=((1 / 9) * (self.prevState.args[1] - 1)) - 1 / 18,
                                                relwidth=1, relheight=1 / 9)

                    # Can Bus
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  #//////////////////////////////////////////////////////
                    bus.send(msg)  #//////////////////////////////////////////////////////////////////////////////////
#                     CanSend.Sendsomebullshit()
                    # Current state gets updated to be the previous state
                    LeftFrame.CurrState = self.prevState.args

                # If the current state is same as the state previous to the one pressed
                # This is the main form of state transition
                if LeftFrame.CurrState[0] == self.prevState.stateName:
                    # State pressed gets enabled/green and previous state gets de-enabled/red
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                            font=("Verdana", 10), fg='green', bg='black')
                    self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1,
                                      relheight=1 / 9)
                    self.prevState.Button = tk.Button(self.parent, text=self.prevState.args[0],
                                                      command=lambda: self.prevState.StateActuaction(),
                                                      font=("Verdana", 10), fg='red', bg='black')
                    self.prevState.Button.place(relx=0, rely=((1 / 9) * (self.prevState.args[1] - 1)) - 1 / 18,
                                                relwidth=1, relheight=1 / 9)
                    # Can Bus
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  #////
                    bus.send(msg)  #//////////////////////////////////////////////////////////////////////////////////
#                     CanSend.Sendsomebullshit()

                    # Current State Gets updated
                    LeftFrame.CurrState = self.args

            # If the state pressed is the Test State
            if self.stateName == "Test":
                # system leaves Passive state
                self.passiveState = tk.Label(self.parent, text="Active", bg="grey", fg="Green", font=self.fontSize1)
                self.passiveState.place(relx=0, rely=0.0125, relwidth=1, relheight=1 / 30)

                # If Test mode is currently disabled
                if LeftFrame.TestState == False:
                    # Enable test mode and update the state displays
                    LeftFrame.TestState = True
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                            font=("Verdana", 10), fg='green', bg='black')
                    self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 9)
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)#////
                    bus.send(msg)#//////////////////////////////////////////////////////////////////////////////////
#                     CanSend.Sendsomebullshit()

                else:
                    # Disable Test mode
                    LeftFrame.TestState = False
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                            font=("Verdana", 10), fg='red', bg='black')
                    self.Button.place(relx=0, rely=((1 / 9) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 9)
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)  #////
                    bus.send(msg)  #//////////////////////////////////////////////////////////////////////////////////
#                     CanSend.Sendsomebullshit()

            return 0

# Bottom Frame ------------------------------------------------------------------------------------------------------
class BottomFrame:
    # This holds the Vent and Abort Buttons and the Logos of the groups involved
    # Takes in as arguments the Main Frame and the Left Frame
    # The Left Frame is needed because the Vent and Abort states will need to de-enable the other states

    # Data needed to setup the button for each State
    # [ State Name, X coordinate]
    bottomButtons = [
        ["Vent", 0, 1, 20, 21],
        ["Abort", 3 / 4, 1, 22, 23]
    ]

    def __init__(self, parent, leftFrame):
        # Makes the Vent and Abort Buttons
        # They both have access to each other in case one needs to be enabled right after the other
        vent = self.Button(parent, BottomFrame.bottomButtons[0], leftFrame)
        abort = self.Button(parent, BottomFrame.bottomButtons[1], leftFrame, vent)
        # other is just were the other state (either vent or abort) will be stored
        # got lazy with naming
        vent.other = abort

    # Makes and manages the buttons and state logic for the vent and abort
    class Button:
        def __init__(self, parent, args, leftFrame, other=None):
            # Font size for the buttons
            self.fontSize = tkFont.Font(size=26)

            # Instantiates buttons
            self.Button = tk.Button(parent, text=args[0], font=self.fontSize, command=lambda: self.ValveActuaction(),
                                    fg='red', bg='grey')
            self.Button.place(relx=args[1], rely=0, relheight=1, relwidth=1 / 4)
            self.status = False

            # Can stuff
            self.commandID = args[2]
            self.commandOFF = args[3]
            self.commandON = args[4]

            self.args = args
            self.parent = parent
            self.leftFrame = leftFrame

            # other is just were the other state (either vent or abort) will be stored
            # got lazy with naming
            self.other = other

        # Logic for the vent and abort
        def ValveActuaction(self):
            # Calls function from LeftFrame to reset all the state labels
            LeftFrame.VentorAbort(self.leftFrame)
            # If the state is currently off, turn it on
            if not self.status:
                # Updates the display
                self.Button = tk.Button(self.parent, text=self.args[0], font=self.fontSize,
                                        command=lambda: self.ValveActuaction(),
                                        fg='green', bg='grey')
                self.Button.place(relx=self.args[1], rely=0, relheight=1, relwidth=1 / 4)
                # Sets the state to true
                self.status = True

                # if the other state (Vent or abort) is currently on, turn it off
                if self.other.status:
                    self.other.Button = tk.Button(self.parent, text=self.other.args[0], font=self.fontSize,
                                                  command=lambda: self.other.ValveActuaction(),
                                                  fg='red', bg='grey')
                    self.other.Button.place(relx=self.other.args[1], rely=0, relheight=1, relwidth=1 / 4)
                    self.other.status = False
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False) # ////
                bus.send(msg) # //////////////////////////////////////////////////////////////////////////////////////
#                 CanSend.Sendsomebullshit()

            else:  # Turns off the state pressed
                self.status = False
                self.Button = tk.Button(self.parent, text=self.args[0], font=self.fontSize,
                                        command=lambda: self.ValveActuaction(),
                                        fg='red', bg='grey')
                self.Button.place(relx=self.args[1], rely=0, relheight=1, relwidth=1 / 4)
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False) # ////
                bus.send(msg) # //////////////////////////////////////////////////////////////////////////////////////
#                 CanSend.Sendsomebullshit()

                # System state moved to standby
                LeftFrame.CurrState = ["StandBy"]

            return 0

class Canstuff:
    def run(self):
        while True:
            print("Brandon is superior than Dan")
            
# Center Frame ------------------------------------------------------------------------------------------------------
class CenterFrame:
    currValveState = "0000000000"
    def __init__(self, parent):
        # Displays all the sensor readings and what the current valve actuation state is
        # Also allows user to actuate valves individually if test mode is enabled

        # Data needed to setup the button
        # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
        Valves = [
            ['HP', 0, .65, 16, 2, 32, 33],
            ['HV', .075, .825, 17, 2, 34, 35],
            ['LV', .375, .025, 18, 3, 36, 37],
            ['LDR', .15, .15, 19, 3, 38, 39],
            ['LDV', .225, .025, 20, 3, 40, 41],
            ['FV', .375, .8, 21, 3, 42, 43],
            ['FDR', .15, .65, 22, 3, 44, 45],
            ['FDV', .225, .8, 17, 23, 3, 46, 47],
            ['LMV', .815, 0.15, 24, 2, 48, 49],
            ['FMV', .665, .15, 25, 2, 50, 51],
        ]

        self.valvelist = []

        # Creates a button for each valve
        for valve in Valves:
            self.valvelist.append(self.Valve(parent, valve))

        Sensors = [
            ["COPV 1", 0.06, 0.0125, 0.075,0.00],
            ["COPV 2", 0.06, 0.055, 0.075,0.00],
            ["Fuel Tank", 0.505, 0.575, 0.06,0.04],
            ["Lox Tank", 0.505, 0.125, 0.06,0.04],
            ["Lox\n Dome", 0.305, 0.05, 0.02,0.08],
            ["Fuel\n Dome", 0.305, 0.7, 0.02,0.08],
            ["MV\n Pneumatic", 0.875, 0.005, 0.05,0.08],
            ["Fuel\n Prop Inlet", .65, 0.25, 0.025,0.08],
            ["LOx\n Prop Inlet", .8125, 0.25, 0.025,0.08],
            ["---: ", .55, 0.225, 0.03, 0.00],
            ["---: ", .55, 0.34, 0.03, 0.00],
            ["---: ", .55, 0.455, 0.03, 0.00],
            # Engine Sensors
            ["Fuel Inlet", .86, .38, 0.05,0.04],
            ["Fuel Injector", .86, .46, 0.05,0.04],
            ["LOX Injector", .86, .54, 0.05,0.04],
            ["Pc Chamber 1", .86, .62, 0.05,0.04],
            ["Pc Chamber 2", .86, .70, 0.05,0.04],
            ["Pc Chamber 3", .86, .78, 0.05,0.04],
            ["Temp\n ChamberExt", .86, .86, 0.05,0.08],
            ["LC1: ", .725, .86, 0.065,0],
            ["LC2: ", .725, .90, 0.065,0],
            ["LC3: ", .725, .94, 0.065,0]
        ]

        # stores each sensor in the list
        self.sensorList = []
        # Instantiates each sensor in the Sensors list
        for sensor in Sensors:
            self.sensorList.append(self.Sensor(parent, sensor))

        # Refreshlabel() Refreshes the Readings
        self.RefreshLabel()

    # Readings Refresher, Recursive Function
    def RefreshLabel(self):
        #print(CanRecieve.ValveState)
        # for each sensor in the sensor list. refresh the label
        for sensor in self.sensorList:
            # calls the sensors label refresh function
            sensor.RefreshLabel()
#         # recalls this functino after 500 ms
#         if CanRecieve.ValveState != LeftFrame.currValveState:
#             for i in CanRecieve.ValveState:
#                 if CanRecieve.ValveState[i] != LeftFrame.currValveState[i]:            
        #for valve in self.valvelist:
            
        self.sensorList[1].ReadingLabel.after(250, self.RefreshLabel)

    # Instantiate Sensor
    class Sensor:
        def __init__(self, parent, args):
            # Makes label with name of sensor
            self.label = tk.Label(parent, text=args[0], font=("Verdana", 10), fg='white', bg='black')
            self.label.place(relx=args[1], rely=args[2], anchor="nw")
            # Makes label with the reading for its corresonding sensor
            self.ReadingLabel = tk.Label(parent, text="N/A", font=("Verdana", 10), fg='orange', bg='black')
            self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")
            # self.SensorID = args[3]

        # Updates the reading
        # Gets called by the Center Frame class
        def RefreshLabel(self):
            value = random.randint(1, 100)  # CanRecieve.getVar(self.SensorID)
            self.ReadingLabel.config(text=value)  # Updates the label with the updated value

    # Instantiates the valves
    class Valve:
        def __init__(self, parent, args):
            # Makes button that can be used by user to actuate valve
            self.Button = tk.Button(parent, text=args[0], command=lambda: self.TwoFactorAuthentication(),
                                    font=("Verdana", 10), fg='red', bg='black')
            self.Button.place(relx=args[1], rely=args[2])

            self.status = False  # Keeps track of valve actuation state

            self.commandID = args[4]
            self.commandOFF = args[5]
            self.commandON = args[6]

            self.args = args
            self.parent = parent

            # Used for Two Factor Authentication
            self.time1 = time.time()
            self.time2 = 0

        # Two Factor Authentication
        # Valve has to be pressed twice in the span of 1 second
        # In case someone spams the button press
        # At least half second needs to have passed from last valve actuation to be actuated again
        # Calls ValveActucation() if TFA passed
        def TwoFactorAuthentication(self):
            if abs(self.time2 - self.time1) < 1:
                self.time1 = time.time()
                return 0
            if time.time() - self.time1 > 0.5:
                self.time1 = time.time()
            else:
                self.ValveActuaction()
                self.time1 = time.time()
            return 0

        # Sends out Can bus command for valve actuation
        # Can only be done if Test Mode is enabled
        # Updates UI to show Valve actuaction state
        def ValveActuaction(self):
            if not LeftFrame.TestState:
                return 0
            self.time2 = time.time()  # stores the time at which the valve was actuated

            # If valve is Off turn On
            if not self.status:
                self.status = True
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.TwoFactorAuthentication(),
                                        font=("Verdana", 10), fg='green', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False) #/////
                bus.send(msg) #///////////////////////////////////////////////////////////////////////////////////
#                 CanSend.Sendsomebullshit()

            else:  # Vice versa
                self.status = False
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.TwoFactorAuthentication(),
                                        font=("Verdana", 10), fg='red', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False) #/////
                bus.send(msg) #///////////////////////////////////////////////////////////////////////////////////
#                 CanSend.Sendsomebullshit()

            return 0
        
        #def RefreshButton():
            
    
# Time Frame  ------------------------------------------------------------------------------------------------------
class TimeFrame:
    # Displays the current time on the GUI, still needs work
    def __init__(self, parent):
        timeFrame = tk.Frame(parent, bg="black", bd=5)
        timeFrame.place(relx=.825, rely=.035, relwidth=.175, relheight=0.05)

        # clockFrame = self.TelemetryNode(timeFrame)
        
class RightFrame:
    def __init__(self, parent):
        rightFrame = tk.Frame(parent, bg="grey", bd=5)
        rightFrame.place(relx=.815, rely=.07, relwidth=.1875, relheight=.95)

        graph1 = self.Graph1(rightFrame)
        graph2 = self.Graph2(rightFrame)
        graph3 = self.Graph3(rightFrame)

    class Graph1:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx= '-0.025', rely=0, relwidth=1.06, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f1, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph2:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx= '-0.025', rely=(1 / 3 + 0.0015) * 1, relwidth=1.06, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f2, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph3:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx= '-0.025', rely=(1 / 3 + 0.0015) * 2, relwidth=1.06, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f3, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


f1 = Figure(figsize = (5,5), dpi = 55)
f2 = Figure(figsize = (5,5), dpi = 55)
f3 = Figure(figsize = (5,5), dpi = 55)

a1 = f1.add_subplot(111)
a2 = f2.add_subplot(111)
a3 = f3.add_subplot(111)

def Reset():
    print("Reset")

# Animate Function is used to animate and refresh the plots
# currently set to using random numbers and only the most recent 10 numbers are displayed/stored

x,y = [0]*20,[0]*20
x1,y1 = [0]*20,[0]*20

def animate(i):
    global x
    global y
    global x1
    global y1
    x.append(999)
    y.append(999)
    x = x[-10:]
    y = y[-10:]
    a1.clear()
    a1.plot(x,y)
    x1.append(999)
    y1.append(999)
    x1 = x1[-10:]
    y1 = y1[-10:]
    a2.clear()
    a2.plot(x1, y1)
    a3.clear()
    a3.plot(x1, y)
    

            
if __name__ == '__main__':
    
    GUI = Main()
    GUIThread = Thread(target=GUI.run)
    GUIThread.daemon = True
    
#     cansend = CanSend()
#     cansendThread = Thread(target=cansend.run)
#     cansendThread.daemon = True
    
    canrecieve = CanRecieve()
    canrecieveThread = Thread(target=canrecieve.run)
    canrecieveThread.daemon = True
    
    GUIThread.start()
#     cansendThread.start()
    canrecieveThread.start()

#     LCan2 = Canstuff()
#     LCan2Thread = Thread(target=LCan2.run)
#     LCan2Thread.start()
