import datetime
import signal
import tkinter as tk
from threading import Thread
import time
import tkinter.font as tk_font  # for font size
# import subprocess
# from matplotlib import pyplot as plt
# from matplotlib.figure import Figure
# import matplotlib.animation as animation
# from matplotlib import style
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from PIL import Image, ImageTk
# All Can bus lines will have the bottom dash lines to help s2how which lines to
# uncomment when on Pi or comment out when on a computer
import can  # /////////////////////////////////////////////////////////////////////////
# from CanSend import CanSend
from CanReceive import CanReceive

# This code is initializing the bus variable with the channel and bustype.
# noinspection PyTypeChecker
bus = can.interface.Bus(channel='can1', bustype='socketcan')  # ///////////////


# The style of graph matplotlib will be using
# style.use('dark_background')

# PGSEbuttonOFF = Image.open("GUI Images/SV circle symbol red png.png")
# PGSEbuttonON = Image.open("GUI Images/SV circle symbol green png.png")

# Main Class, Everything is controlled from here

class Main:
    @staticmethod
    def run():
        # Root for application -----------------------------------------------------------------------------------
        root = tk.Tk()
        # Main Frame --------------------------------------------------------------------------------------------
        # All the frames will be placed inside the main frame
        main_frame = tk.Frame(root, bg="Black", bd=5)
        main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Each Frame has its own class
        # Top Frame --------------------------------------------------------------------------------------------
        # Contains all the telemetry data
        TopFrame(main_frame)
        # Time Frame --------------------------------------------------------------------------------------------
        # Displays the current time
        TimeFrame(main_frame)
        # Left Frame --------------------------------------------------------------------------------------------
        # Contains all the Operational States
        left_frame = LeftFrame(main_frame)
        # Right Frame --------------------------------------------------------------------------------------------
        # Contains Several Graphs
        RightFrame(main_frame)
        # Center Frame --------------------------------------------------------------------------------------------
        # Displays the Propulsion Feed System
        # Displays the actuation state of individual valves and sensor readings
        # Allows for access to actuate individual valves when system is in Test mode
        # Getting the png to show wasn't working when inside the class, so I brought it out to main class
        # to then give the Center Class the frame with the PNG already on it
        center_frame = tk.Frame(main_frame, bg="Black")
        center_frame.place(relx=0.11, rely=0.2, relwidth=0.7, relheight=0.65)
        # # Put schematic draft for layout
        # schematicImage = tk.PhotoImage(file="Images\GUI Prop Layout.png")
        # schematicLabel = tk.Label(centerFrame, image=schematicImage, bg="black")
        # schematicLabel.place(relx=0, rely=0, relwidth=1, relheight=1)
        CenterFrame(center_frame)
        # Bottom Frame --------------------------------------------------------------------------------------------
        # Bottom Frame Getting the png to show wasn't working when inside the class, so I brought it out to main class
        # to then give the Bottom Class the frame with the PNG already on it
        # Bottom Frame takes in the left frame to allow for the Vent and Abort functions to modify the states in the
        # left frame
        bottom_frame = tk.Frame(main_frame, bg="Black")
        bottom_frame.place(relx=0.14, rely=0.85, relwidth=0.65, relheight=0.2)

        # Graphics import and placements -----------------------------------------------------------------------
        #         RenegadeLOGOSAD = tk.PhotoImage(file="/home/pi/Documents/GUI Images/Sad Renegade LOGO.png")
        #         logo2 = tk.Label(bottomFrame, image=RenegadeLOGOSAD, bg = "black")
        #         logo2.place(relx=0.315, rely='-.1250')

        renegade_logo = tk.PhotoImage(file="GUI Images/RenegadeLogoSmall.png")
        logo1 = tk.Label(bottom_frame, image=renegade_logo, bg="black")
        logo1.place(relx=.415, rely='-.1250')

        engine_art = tk.PhotoImage(file="GUI Images/Engine Clipart smol.png")
        logo2 = tk.Label(center_frame, image=engine_art, bg="black")
        logo2.place(relx=.735, rely=.40)

        lox_tank_art = tk.PhotoImage(file="GUI Images/TankPlainClipart.png")
        logo3 = tk.Label(center_frame, image=lox_tank_art, bg="black")
        logo3.place(relx=.475, rely=.2)

        fuel_tank_art = tk.PhotoImage(file="GUI Images/TankPlainClipart.png")
        logo4 = tk.Label(center_frame, image=fuel_tank_art, bg="black")
        logo4.place(relx=.475, rely=.615)

        copv_tank_art = tk.PhotoImage(file="GUI Images/TankPlainClipartCOPV.png")
        logo5 = tk.Label(center_frame, image=copv_tank_art, bg="black")
        logo5.place(relx=.0, rely=.0)

        dome_reg_art = tk.PhotoImage(file="GUI Images/AquaDomeReg Clipart.png")
        logo6 = tk.Label(center_frame, image=dome_reg_art, bg="black")
        logo6.place(relx=.25, rely=.185)
        logo7 = tk.Label(center_frame, image=dome_reg_art, bg="black")
        logo7.place(relx=.25, rely=.5)

        BottomFrame(bottom_frame, left_frame)

        # Matplotlib Refresh Function call -----------------------------------------------------------------------
        # Calls the animation function and refreshes the matplotlib graphs every 1000 ms (1 second)
        #         ani1 = animation.FuncAnimation(f1,animate, interval=1000)
        #         ani2 = animation.FuncAnimation(f2,animate, interval=1000)
        #         ani3 = animation.FuncAnimation(f3,animate, interval=1000)

        # Start window--------------------------------------------------------------------------------------------
        root.attributes("-zoomed",
                        True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true
        # fullscreen
        root.bind("<Escape>", lambda event: root.destroy())  # binds escape key to killing the window
        root.bind("<F11>", lambda event: root.attributes("-fullscreen", True))  # switches from zoomed to fullscreen
        root.bind("<F12>", lambda event: root.attributes("-fullscreen", False))  # switches from fullscreen to zoomed

        # Starts the GUI
        root.mainloop()


# Top Frame Class --------------------------------------------------------------------------------------------
class TopFrame:
    # The class takes in the parent Frame (Main Frame) as an input

    def __init__(self, parent):
        # Make the Top Frame
        self.top_frame = tk.Frame(parent, bg="black", bd=5)
        # Places the Top Frame
        # Coordinates are relative to the Main Frame
        self.top_frame.place(relx=0.405, rely=0, relwidth=.825, relheight=0.2, anchor="n")

        # Make sub Frames for each Telemetry Node It is seperated into individual Nodes for future proofing since
        # they may all be operated differently in the future
        self.TelemetryNode(self.top_frame)
        self.upper_prop_system_node = self.UpperPropSystemNode(self.top_frame)
        self.pad_ground_node = self.PadGroundNode(self.top_frame)
        self.refresh_label()

    def refresh_label(self):
        self.upper_prop_system_node.refresh_label()
        self.pad_ground_node.refresh_label()
        self.top_frame.after(100, self.refresh_label)

    # Currently, all Nodes follow the same code structure
    class TelemetryNode:
        GUI_objects = {}

        def __init__(self, parent):
            # Makes Frame
            # Coordinates are relative to the Top Frame --------------------------------------------------------------
            telemetry_frame = tk.Frame(parent, bg="grey", bd=5)
            telemetry_frame.place(relx=0, rely=0, relwidth=(1 / 3.1), relheight=1)

            # Coordinates are relative to the Top Frame --------------------------------------------------------------
            # Makes 4 labels and then stores them in a list
            telemetry_labels = []
            for i in range(4):
                placed_label = tk.Label(telemetry_frame, text="", bg="grey", anchor="w")
                placed_label.place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)
                telemetry_labels.append(placed_label)
            # Gives each label a text
            telemetry_labels[0]["text"] = "Telemetry Node"
            telemetry_labels[1]["text"] = "Activity: "
            telemetry_labels[2]["text"] = "Temp: "
            telemetry_labels[3]["text"] = "Bus Info"

            # Shows the current state of the node
            node_state = tk.Label(telemetry_frame, text="Default State", bg="black", fg="white")
            node_state.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)
            # reset button
            reset_button = tk.Button(telemetry_frame, text="reset", command=lambda: reset(),
                                     font=("Verdana", 10),
                                     fg='black', bg='white')
            reset_button.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)
            self.GUI_objects['TelemetryFrame'] = telemetry_frame
            self.GUI_objects['TelemetryLabels'] = telemetry_labels
            self.GUI_objects['NodeState'] = node_state
            self.GUI_objects['resetButton'] = reset_button

    class UpperPropSystemNode:
        NodeStateContainer = []

        def __init__(self, parent):
            upper_prop_system_frame = tk.Frame(parent, bg="grey", bd=5)
            upper_prop_system_frame.place(relx=(1 / 3 + 0.0015), rely=0, relwidth=(1 / 3.1), relheight=1)

            upper_prop_system_labels = []
            for i in range(4):
                label = tk.Label(upper_prop_system_frame, text="", bg="grey", anchor="w")
                upper_prop_system_labels.append(label)
                label.place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            upper_prop_system_labels[0]["text"] = "Upper Prop System Node"
            upper_prop_system_labels[1]["text"] = "Activity: "
            upper_prop_system_labels[2]["text"] = "MCU Temp: "
            upper_prop_system_labels[3]["text"] = "Bus Info"

            node_state = tk.Label(upper_prop_system_frame, text="Hi", bg="black",
                                  fg="white")
            self.NodeStateContainer.append(node_state)
            node_state.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

            reset_button = tk.Button(upper_prop_system_frame, text="reset", command=lambda: reset(),
                                     font=("Verdana", 10),
                                     fg='black', bg='white')
            reset_button.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)
            self.refresh_label()

        def refresh_label(self):
            self.NodeStateContainer[0].config(text=str(can_receive.node_dict_list["UpperPropNode"]["state"]))

    class PadGroundNode:
        NodeStateContainer = []

        def __init__(self, parent):
            pad_ground_frame = tk.Frame(parent, bg="grey", bd=5)
            pad_ground_frame.place(relx=(2 / 3 + 0.0015), rely=0, relwidth=(1 / 3.1), relheight=1)
            pad_ground_labels = []
            for i in range(4):
                label = tk.Label(pad_ground_frame, text="", bg="grey", anchor="w")
                pad_ground_labels.append(label)
                label.place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            pad_ground_labels[0]["text"] = "Pad Ground Node"
            pad_ground_labels[1]["text"] = "Activity: "
            pad_ground_labels[2]["text"] = "MCU Temp: "
            pad_ground_labels[3]["text"] = "Bus Info"

            node_state = tk.Label(pad_ground_frame, text="Default State", bg="black", fg="white")
            self.NodeStateContainer.append(node_state)
            node_state.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

            reset_button = tk.Button(pad_ground_frame, text="reset", command=lambda: reset(), font=("Verdana", 10),
                                     fg='black', bg='white')
            reset_button.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1 / 3)

        def refresh_label(self):
            self.NodeStateContainer[0].config(text=str(can_receive.node_dict_list["PadGroundNode"]["state"]))


# Left Frame --------------------------------------------------------------------------------------------
class LeftFrame:
    # Keeps track of the operational state the system is in  ----------------------------------------------------
    # Standby: System will not actuate any valves "Passive" or "Active" will be shown to display whether this
    # mode is active Testing: Gives access to user to actuate individual valves Purge: Don't really know High Press
    # Press Arm: something about an arms, I thought Dan was into feet tbh High Press Pressurize: Allows pressure to
    # go into the COPV Tank Press Arm: I wonder if I can beat Dan in an Arm wrestle??? Right now yes I am soft and
    # weak -Dan When and where? - Pizza Tank Pressurize: Pressurizes the Tanks and allows the COPV to still receive
    # pressure to get backfilled Fire Arm: My arms are starting to get tired or writing comments Fire: Boom Boom
    # Time From Purge to Fire state you cannot actuate any valves unless you override the system by enabling testing
    # mode
    # Testing mode will have to be disabled to continue with the operational States Once in Purge you have
    # entered Terminal countdown and can only go down the list of states. Only way out is through venting or aborting
    # State can be UnArmed by reclicking the Arm button and return to the state before it

    # CurrState Keeps track of the Operational State the system is in
    # It takes in a list of data from the left buttons list corresponding to the state it is in
    # System Boots up in Standby/ Passive, both mean the same thing
    CurrState = ["Standby"]
    # Keeps track of whether the Test State is active
    # When Test State is True, User can actuate Individual Valves
    TestState = False

    # Data needed to set up the button for each State
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

    # The class takes in the parent Frame (Main Frame) as an input
    def __init__(self, parent):
        # Creates the Left Frame
        # Coordinates Relative to Main Frame
        self.leftFrame = tk.Frame(parent, bg="grey", bd=5)
        self.leftFrame.place(relx=0.0001, rely=1 / 5, relwidth=.1, relheight=0.8)

        # Font Size used for some labels
        self.fontSize1 = tk_font.Font(size=17)

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
    def vent_or_abort(self):
        # Resets every state in the state list
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
            self.passiveState = None
            self.args = args
            # Creates Button for that State
            # Coordinates Relative to Left Frame
            self.Button = tk.Button(parent, text=self.args[0], command=lambda: self.state_actuation,
                                    font=("Verdana", 10), fg='red', bg='black')
            self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 8)

            # commandID, commandOFF, commandON are needed for the Can Commands
            self.commandID = self.args[2]
            self.commandOFF = self.args[3]
            self.commandON = self.args[4]

            self.parent = parent  # Parent Frame
            self.prevState = prev  # Holds the previous node
            self.stateName = args[0]  # Stores the Name of the state
            self.isAnArmState = args[4]  # True is the State is an Arm State

            # Font Size used for some labels
            self.fontSize1 = tk_font.Font(size=20)

        # Stores the logic for the transition between States ----------------------------------------------------------
        @property
        def state_actuation(self):
            # If the Current state is not in Test Mode
            # If the Test Mode is not enabled
            #   These may sound redundant, but you can be in another state and test mode be enabled for overrides
            #   If Terminal Count has Started (State Purge through Fire), Test mode can be enabled to override the
            #       state conditions if needed
            # If the button pressed is not the Test Button, Test has different logic
            if LeftFrame.CurrState[0] != "Test" and not LeftFrame.TestState and self.stateName != "Test":
                # If the current state is the same as the state pressed
                # and the state pressed is an Arm State
                # Arm States can be un armed if they pressed again, the current state will be set to the previous state
                if LeftFrame.CurrState[0] == self.stateName and self.isAnArmState:
                    # Updates the Buttons to show the updated states
                    # Current state gets de-enabled/red
                    # Previous state gets enabled/green
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.state_actuation,
                                            font=("Verdana", 10), fg='red', bg='black')
                    self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 8)
                    if self.prevState.stateName != "Test":
                        self.prevState.Button = tk.Button(self.parent, text=self.prevState.args[0],
                                                          command=lambda: self.prevState.state_actuation,
                                                          font=("Verdana", 10), fg='green', bg='black')
                        self.prevState.Button.place(relx=0, rely=((1 / 8) * (self.prevState.args[1] - 1)) - 1 / 18,
                                                    relwidth=1, relheight=1 / 8)

                        # Can Bus
                        msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
                        bus.send(msg)
                        LeftFrame.CurrState = self.prevState.args
                    else:
                        LeftFrame.CurrState = ["Standby"]

                # If the current state is same as the state previous to the one pressed
                # This is the main form of state transition
                elif LeftFrame.CurrState[0] == self.prevState.stateName or LeftFrame.CurrState[0] == "Standby":
                    # State pressed gets enabled/green and previous state gets de-enabled/red
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.state_actuation,
                                            font=("Verdana", 10), fg='green', bg='black')
                    self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 1)) - 1 / 18, relwidth=1,
                                      relheight=1 / 8)
                    self.prevState.Button = tk.Button(self.parent, text=self.prevState.args[0],
                                                      command=lambda: self.prevState.state_actuation,
                                                      font=("Verdana", 10), fg='red', bg='black')
                    self.prevState.Button.place(relx=0, rely=((1 / 8) * (self.prevState.args[1] - 1)) - 1 / 18,
                                                relwidth=1, relheight=1 / 8)
                    # Can Bus
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON],
                                      is_extended_id=False)  # ////
                    bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////
                    #                     CanSend.Sendsomebullshit()

                    # Current State Gets updated
                    LeftFrame.CurrState = self.args

            # If the state pressed is the Test State
            if self.stateName == "Test":
                # system leaves Passive state
                self.passiveState = tk.Label(self.parent, text="Active", bg="grey", fg="Green", font=self.fontSize1)
                self.passiveState.place(relx=0, rely=0.0125, relwidth=1, relheight=1 / 30)

                # If Test mode is currently disabled
                if not LeftFrame.TestState:
                    # Enable test mode and update the state displays
                    LeftFrame.TestState = True
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.state_actuation,
                                            font=("Verdana", 10), fg='green', bg='black')
                    self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 8)
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandON],
                                      is_extended_id=False)  # ////
                    bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////
                    #                     CanSend.Sendsomebullshit()
                    LeftFrame.CurrState = self.args
                else:
                    # Disable Test mode
                    LeftFrame.TestState = False
                    self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.state_actuation,
                                            font=("Verdana", 10), fg='red', bg='black')
                    self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 1)) - 1 / 18, relwidth=1, relheight=1 / 8)
                    msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF],
                                      is_extended_id=False)  # ////
                    bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////
                    #                     CanSend.Sendsomebullshit()
                    LeftFrame.CurrState = ["Standby"]

            return 0


# Bottom Frame ------------------------------------------------------------------------------------------------------
class BottomFrame:
    # This holds the Vent and Abort Buttons and the Logos of the groups involved
    # Takes in as arguments the Main Frame and the Left Frame
    # The Left Frame is needed because the Vent and Abort states will need to de-enable the other states

    # Data needed to set up the button for each State
    # [ State Name, X coordinate]
    bottomButtons = (
        ("Vent", 0, 1, 8, 9),
        ("Abort", 3 / 4, 1, 6, 7)
    )

    def __init__(self, parent, left_frame):
        # Makes the Vent and Abort Buttons
        # They both have access to each other in case one needs to be enabled right after the other
        vent = self.Button(parent, BottomFrame.bottomButtons[0], left_frame)
        abort = self.Button(parent, BottomFrame.bottomButtons[1], left_frame, vent)
        # other is just were the other state (either vent or abort) will be stored
        # got lazy with naming
        vent.other = abort

    # Makes and manages the buttons and state logic for the vent and abort
    class Button:
        def __init__(self, parent, args, left_frame, other=None):
            # Font size for the buttons
            self.fontSize = tk_font.Font(size=26)

            # Instantiate buttons
            self.Button = tk.Button(parent, text=args[0], font=self.fontSize, command=lambda: self.valve_actuation(),
                                    fg='red', bg='grey')
            self.Button.place(relx=args[1], rely=0, relheight=1, relwidth=1 / 4)
            self.status = False

            # Can stuff
            self.commandID = args[2]
            self.commandOFF = args[3]
            self.commandON = args[4]

            self.args = args
            self.parent = parent
            self.leftFrame = left_frame

            # other is just were the other state (either vent or abort) will be stored
            # got lazy with naming
            self.other = other

        # Logic for the vent and abort
        def valve_actuation(self):
            # Calls function from LeftFrame to reset all the state labels
            LeftFrame.vent_or_abort(self.leftFrame)
            # If the state is currently off, turn it on
            if not self.status:
                # Updates the display
                self.Button = tk.Button(self.parent, text=self.args[0], font=self.fontSize,
                                        command=lambda: self.valve_actuation(),
                                        fg='green', bg='grey')
                self.Button.place(relx=self.args[1], rely=0, relheight=1, relwidth=1 / 4)
                # Sets the state to true
                self.status = True

                # if the other state (Vent or abort) is currently on, turn it off
                if self.other.status:
                    self.other.Button = tk.Button(self.parent, text=self.other.args[0], font=self.fontSize,
                                                  command=lambda: self.other.valve_actuation(),
                                                  fg='red', bg='grey')
                    self.other.Button.place(relx=self.other.args[1], rely=0, relheight=1, relwidth=1 / 4)
                    self.other.status = False
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # ////
                bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
            #                 CanSend.Sendsomebullshit()

            else:  # Turns off the state pressed
                self.status = False
                self.Button = tk.Button(self.parent, text=self.args[0], font=self.fontSize,
                                        command=lambda: self.valve_actuation(),
                                        fg='red', bg='grey')
                self.Button.place(relx=self.args[1], rely=0, relheight=1, relwidth=1 / 4)
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)  # ////
                bus.send(msg)  # //////////////////////////////////////////////////////////////////////////////////////
                #                 CanSend.Sendsomebullshit()

                # System state moved to standby
                LeftFrame.CurrState = ["StandBy"]

            return 0


# Center Frame ------------------------------------------------------------------------------------------------------
class CenterFrame:
    currValveState = "0000000000"

    def __init__(self, parent):
        # Displays all the sensor readings and what the current valve actuation state is
        # Also allows user to actuate valves individually if test mode is enabled

        # Data needed to set up the button
        # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
        valves = (
            ('HP', 0, .65, 16, 2, 32, 33),
            ('HV', .075, .825, 17, 2, 34, 35),
            ('LV', .375, .025, 18, 3, 36, 37),
            ('LDR', .15, .15, 19, 3, 38, 39),  # LDR
            ('LDV', .225, .025, 20, 3, 40, 41),
            ('FV', .375, .8, 21, 3, 42, 43),
            ('FDR', .15, .65, 22, 3, 44, 45),
            ('FDV', .225, .8, 17, 23, 3, 46, 47),
            ('LMV', .815, 0.15, 24, 2, 48, 49),
            ('FMV', .665, .15, 25, 2, 50, 51),
        )

        self.valve_list = []

        # Creates a button for each valve
        for valve in valves:
            self.valve_list.append(self.Valve(parent, valve))

        sensors = (
            ("COPV LOx", 0.06, 0.0125, 0.075, 0.00, 84),
            ("COPV Fuel", 0.06, 0.055, 0.075, 0.00, 83),
            ("Fuel Tank", 0.505, 0.575, 0.06, 0.04, 81),
            ("Lox Tank", 0.505, 0.125, 0.06, 0.04, 82),
            ("Lox\n Dome", 0.305, 0.05, 0.02, 0.08, 80),
            ("Fuel\n Dome", 0.305, 0.7, 0.02, 0.08, 79),
            ("MV\n Pneumatic", 0.875, 0.005, 0.05, 0.08, 78),
            ("Fuel\n Prop Inlet", .65, 0.25, 0.025, 0.08, 57),
            ("LOx\n Prop Inlet", .8125, 0.25, 0.025, 0.08, 59),
            ("---: ", .55, 0.225, 0.03, 0.00, 0),
            ("---: ", .55, 0.34, 0.03, 0.00, 0),
            ("---: ", .55, 0.455, 0.03, 0.00, 0),
            # Engine Sensors
            ("Fuel Inlet", .86, .38, 0.05, 0.04, 10),
            ("Fuel Injector", .86, .46, 0.05, 0.04, 58),
            ("LOX Injector", .86, .54, 0.05, 0.04, 12),
            ("Pc Chamber 1", .86, .62, 0.05, 0.04, 56),
            ("Pc Chamber 2", .86, .70, 0.05, 0.04, 55),
            ("Pc Chamber 3", .86, .78, 0.05, 0.04, 15),
            ("Temp\n ChamberExt", .86, .86, 0.05, 0.08, 16),
            ("LC1: ", .725, .86, 0.065, 0, 17),
            ("LC2: ", .725, .90, 0.065, 0, 18),
            ("LC3: ", .725, .94, 0.065, 0, 19)
        )

        # stores each sensor in the list
        self.sensorList = []
        # Instantiates each sensor in the Sensors list
        for sensor in sensors:
            self.sensorList.append(self.Sensor(parent, sensor))

        # Refreshlabel() Refreshes the Readings
        self.refresh_label()

    # Readings Refresher, Recursive Function
    def refresh_label(self):
        # print(CanReceive.ValveState)
        # for each sensor in the sensor list. refresh the label
        for sensor in self.sensorList:
            # calls the sensors label refresh function
            sensor.refresh_label()
        for valve in self.valve_list:
            valve.refresh_valve()
        #         # recalls this function after 500 ms
        #         if CanReceive.ValveState != LeftFrame.currValveState:
        #             for i in CanReceive.ValveState:
        #                 if CanReceive.ValveState[i] != LeftFrame.currValveState[i]:
        # for valve in self.valve_list:

        self.sensorList[1].ReadingLabel.after(250, self.refresh_label)

    # Instantiate Sensor
    class Sensor:
        def __init__(self, parent, args):
            # Makes label with name of sensor
            self.label = tk.Label(parent, text=args[0], font=("Verdana", 10), fg='white', bg='black')
            self.label.place(relx=args[1], rely=args[2], anchor="nw")
            # Makes label with the reading for its corresponding sensor
            self.ReadingLabel = tk.Label(parent, text="N/A", font=("Verdana", 10), fg='orange', bg='black')
            self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")
            # self.SensorID = args[3]
            self.stateID = args[5]

        # Updates the reading
        # Gets called by the Center Frame class
        def refresh_label(self):
            # value = random.randint(1, 100)  # CanReceive.getVar(self.SensorID)
            if self.stateID == 0:
                value = 0
            else:
                value = CanReceive.Sensors[self.stateID]
            self.ReadingLabel.config(text=value)  # Updates the label with the updated value

    # Instantiates the valves
    class Valve:
        def __init__(self, parent, args):
            # Makes button that can be used by user to actuate valve
            self.name = args[0]
            self.photo_name = args[0]
            self.x_pos = args[1]
            self.y_pos = args[2]
            self.photo = tk.PhotoImage(file="GUI Images/" + self.photo_name + "Button.png").subsample(5)
            self.Button = tk.Button(parent, image=self.photo, command=lambda: self.two_factor_authentication(),
                                    font=("Verdana", 10), fg='red', bg='black')
            self.Button.place(relx=self.x_pos, rely=self.y_pos)

            self.status = 0  # Keeps track of valve actuation state

            self.commandID = args[4]
            self.commandOFF = args[5]
            self.commandON = args[6]

            self.args = args
            self.parent = parent

            # Used for Two-Factor Authentication
            self.time1 = time.time()
            self.time2 = 0

        def refresh_valve(self):
            if self.name in can_receive.node_state and self.status is not can_receive.node_state[self.name]:
                if can_receive.node_state[self.name] == 0:
                    self.photo_name = "Disabled"
                else:
                    self.photo_name = self.name
                self.photo = tk.PhotoImage(file="GUI Images/" + self.photo_name + "Button.png").subsample(5)
                self.Button = tk.Button(self.parent, image=self.photo, command=lambda: self.two_factor_authentication(),
                                        bg='black')
                self.Button.place(relx=self.x_pos, rely=self.y_pos)

        # Two-Factor Authentication
        # Valve has to be pressed twice in the span of 1 second
        # In case someone spams the button press
        # At least half second needs to have passed from last valve actuation to be actuated again
        # Calls valve_actuation() if TFA passed
        def two_factor_authentication(self):
            if abs(self.time2 - self.time1) < 1:
                self.time1 = time.time()
                return 0
            if time.time() - self.time1 > 0.5:
                self.time1 = time.time()
            else:
                self.valve_actuation()
                self.time1 = time.time()
            return 0

        # Sends out Can bus command for valve actuation
        # Can only be done if Test Mode is enabled
        # Updates UI to show Valve actuation state
        def valve_actuation(self):
            if not LeftFrame.TestState:
                return 0
            self.time2 = time.time()  # stores the time at which the valve was actuated

            # If valve is Off turn On
            if not self.status:
                self.status = True
                self.Button = tk.Button(self.parent, text=self.args[0],
                                        command=lambda: self.two_factor_authentication(), font=("Verdana", 10),
                                        fg='green', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)  # /////
                bus.send(msg)  # ///////////////////////////////////////////////////////////////////////////////////
            #                 CanSend.Sendsomebullshit()

            else:  # Vice versa
                self.status = False
                self.Button = tk.Button(self.parent, text=self.args[0],
                                        command=lambda: self.two_factor_authentication(), font=("Verdana", 10),
                                        fg='red', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)  # /////
                bus.send(msg)  # ///////////////////////////////////////////////////////////////////////////////////
            #                 CanSend.Sendsomebullshit()

            return 0

        # def RefreshButton():


# Time Frame  ------------------------------------------------------------------------------------------------------
class TimeFrame:
    # Displays the current time on the GUI, still needs work

    def refresh_label(self):
        time_label = tk.Label(self.time_frame, bg="gray", text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        time_label.place(relx=0.1, rely=0.1)
        self.time_frame.after(1000, self.refresh_label)

    def __init__(self, parent):
        self.time_frame = tk.Frame(parent, bg="gray", bd=5)
        self.time_frame.place(relx=.815, rely=.008, relwidth=.185, relheight=0.05)
        self.time_frame.after(1000, self.refresh_label)

        # clockFrame = self.TelemetryNode(time_frame)


class RightFrame:
    def __init__(self, parent):
        right_frame = tk.Frame(parent, bg="grey", bd=5)
        right_frame.place(relx=.815, rely=.07, relwidth=.1875, relheight=.95)

        self.Graph1(right_frame)
        self.Graph2(right_frame)
        self.Graph3(right_frame)

    class Graph1:
        def __init__(self, parent):
            graph_frame = tk.Frame(parent, bg="grey", bd=5)
            graph_frame.place(relx='-0.025', rely=0, relwidth=1.06, relheight=(1 / 3.1))

    #             canvas = FigureCanvasTkAgg(f1, graphframe)
    #             canvas.draw()
    #             canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    #
    #             toolbar = NavigationToolbar2Tk(canvas, graphframe)
    #             toolbar.update()
    #             canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph2:
        def __init__(self, parent):
            graph_frame = tk.Frame(parent, bg="grey", bd=5)
            graph_frame.place(relx='-0.025', rely=(1 / 3 + 0.0015) * 1, relwidth=1.06, relheight=(1 / 3.1))

    #             canvas = FigureCanvasTkAgg(f2, graphframe)
    #             canvas.draw()
    #             canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    #
    #             toolbar = NavigationToolbar2Tk(canvas, graphframe)
    #             toolbar.update()
    #             canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph3:
        def __init__(self, parent):
            graph_frame = tk.Frame(parent, bg="grey", bd=5)
            graph_frame.place(relx='-0.025', rely=(1 / 3 + 0.0015) * 2, relwidth=1.06, relheight=(1 / 3.1))


#             canvas = FigureCanvasTkAgg(f3, graphframe)
#             canvas.draw()
#             canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
# 
#             toolbar = NavigationToolbar2Tk(canvas, graphframe)
#             toolbar.update()
#             canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


# f1 = Figure(figsize = (5,5), dpi = 55)
# f2 = Figure(figsize = (5,5), dpi = 55)
# f3 = Figure(figsize = (5,5), dpi = 55)
# 
# a1 = f1.add_subplot(111)
# a2 = f2.add_subplot(111)
# a3 = f3.add_subplot(111)


def reset():
    print("reset")


# Animate Function is used to animate and refresh the plots
# currently set to using random numbers and only the most recent 10 numbers are displayed/stored

x, y = [0] * 20, [0] * 20
x1, y1 = [0] * 20, [0] * 20

# def animate(i):
#     global x
#     global y
#     global x1
#     global y1
#     x.append(999)
#     y.append(999)
#     x = x[-10:]
#     y = y[-10:]
#     a1.clear()
#     a1.plot(x, y)
#     x1.append(999)
#     y1.append(999)
#     x1 = x1[-10:]
#     y1 = y1[-10:]
#     a2.clear()
#     a2.plot(x1, y1)
#     a3.clear()
#     a3.plot(x1, y)


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

#     LCan2 = Canstuff()
#     LCan2Thread = Thread(target=LCan2.run)
#     LCan2Thread.start()
