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
import can

#
style.use('dark_background')
bus = can.interface.Bus(channel= 'can0', bustype='socketcan_ctypes')

class Main:
    def __init__(self):

        # Root for application //////////////////////////////////////////////////////////////////////////////////////
        root = tk.Tk()

        # Group 1 Mode Display //////////////////////////////////////////////////////////////////////////////////////
        # All the frames are stored in this group
        group1ModeFrame = tk.Frame(root, bg="Black", bd=5)
        group1ModeFrame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Each Frame has its own class
        topFrame = TopFrame(group1ModeFrame)
        timeFrame = TimeFrame(group1ModeFrame)
        leftFrame = LeftFrame(group1ModeFrame)

        # Getting the image to show wasnt working when inside the class, so i brought it out to main class
        centerFrame = tk.Frame(group1ModeFrame, bg="Black")
        centerFrame.place(relx=0.14, rely=0.2, relwidth=0.65, relheight=0.65)
        # Put schematic draft for layout
##        schematicImage = tk.PhotoImage(file="Images\GUI Prop Layout.png")
##        schematicLabel = tk.Label(centerFrame, image=schematicImage, bg = "black")
##        schematicLabel.place(relx=0, rely=0,relwidth=1, relheight=1)
        center = CenterFrame(centerFrame)

        bottomFrame = tk.Frame(group1ModeFrame, bg="Black")
        bottomFrame.place(relx=0.14, rely=0.85, relwidth=0.65, relheight=0.2)
        # Put schematic draft for layout
##        schematicImage1 = tk.PhotoImage(file="Images\qqq123.png")
##        schematicLabel1 = tk.Label(bottomFrame, image=schematicImage1, bg = "black")
##        schematicLabel1.place(relx=0.45, rely=0)
        bottom = BottomFrame(bottomFrame)

        rightFrame = RightFrame(group1ModeFrame)


        # Calls the animation function and refreshes the matplotlib graphs every 1000 ms (1 second)
        ani1 = animation.FuncAnimation(f1,animate, interval=1000)
        ani2 = animation.FuncAnimation(f2,animate, interval=1000)
        ani3 = animation.FuncAnimation(f3,animate, interval=1000)


        # Start window--------------------------------------------------------------------------------------------
#         root.attributes("-zoomed", True) #fullscreen except taskbars on startup
        root.attributes("-fullscreen", True) #complete fullscreen on startup
#         root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
        root.bind("<Escape>", lambda event:root.destroy()) #binds escape key to killing the window
        
        root.mainloop()
        
        


class TopFrame:
    def __init__(self, parent):
        topFrame = tk.Frame(parent, bg="black", bd=5)
        topFrame.place(relx=0.405, rely=0, relwidth=.825, relheight=0.2, anchor="n")

        telemetryFrame = self.TelemetryNode(topFrame)
        upperPropSystemFrame = self.UpperPropSystemNode(topFrame)
        engineFrame = self.EngineNode(topFrame)
        padGroundFrame = self.PadGroundNode(topFrame)

    class TelemetryNode:
        def __init__(self, parent):
            telemetryframe = tk.Frame(parent, bg="grey", bd=5)
            telemetryframe.place(relx=0, rely=0, relwidth=(1 / 4.1), relheight=1)

            telemetryLabels = [0] * 4
            for i in range(4):
                telemetryLabels[i] = tk.Label(telemetryframe, text="", bg="grey", anchor="w")
                telemetryLabels[i].place(relx=0, rely=(1 / 4) * i, relwidth=2 / 3, relheight=1 / 4)

            telemetryLabels[0]["text"] = "Telemetry Node"
            telemetryLabels[1]["text"] = "Activity: "
            telemetryLabels[2]["text"] = "Temp: "
            telemetryLabels[3]["text"] = "Bus Info"

            nodeState = tk.Label(telemetryframe, text="poo", bg="black", fg="white")
            nodeState.place(relx=2 / 3, rely=2 / 3, relwidth=(1 / 3), relheight=1 / 3)

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


class LeftFrame:
    TestState = False

    def __init__(self, parent):
        leftFrame = tk.Frame(parent, bg="grey", bd=5)
        leftFrame.place(relx=0.0001, rely=1/5, relwidth=.1, relheight=0.8)

        # Data needed to setup the button
        # [ State Name, State ID , commandID, commandOFF , commandON]
        leftButtons = [
            ["Test", 2,1,4,5],
            ["Purge", 3,1,6,7],
            ["Hi-Press\nPress Arm", 4,1,8,9],
            ["Hi-Press\nPressurize", 5,1,10,11],
            ["Tank Press \nArm", 6,1,12,13],
            ["Tank \nPressurize", 7,1,14,15],
            ["Fire Arm", 8,1,16,17],
            ["FIRE", 9,1,18,19]
        ]
        for button in leftButtons:
            self.Button(leftFrame, button)

    class Button:
        def __init__(self, parent, args):
            self.args = args
            self.Button = tk.Button(parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                    font=("Verdana", 11), fg='red', bg='black')
            self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 2)), relwidth=1, relheight=1 / 8)
            self.Status = False
            self.commandID = self.args[2]
            self.commandOFF = self.args[3]
            self.commandON = self.args[4]
            self.parent = parent

        def StateActuaction(self):
            if not self.Status:
                self.Status = True
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                        font=("Verdana", 11), fg='green', bg='black')
                self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 2)), relwidth=1, relheight=1 / 8)
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
                bus.send(msg)
                if self.args[0] == "Test":
                    LeftFrame.TestState = True
            else:
                self.Status = False
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.StateActuaction(),
                                        font=("Verdana", 11), fg='red', bg='black')
                self.Button.place(relx=0, rely=((1 / 8) * (self.args[1] - 2)), relwidth=1, relheight=1 / 8)

                # self.Button.place(relx=0, rely=((1 / 8) * self.args[1]), relwidth=1, relheight=1 / 8)
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
                bus.send(msg)
                if self.args[0] == "Test":
                    LeftFrame.TestState = False
            return 0


class BottomFrame:
    def __init__(self, parent):
        # Preset font size
        fontSize = tkFont.Font(size=30)

        # Vent Button
        ventButton = tk.Button(parent, text="Vent", font=fontSize, command=lambda: ventFunction(), bg="grey")
        ventButton.place(relx=0, rely=0, relwidth=1 / 4, relheight=1)

        # Abort Button
        abortButton = tk.Button(parent, text="Abort", font=fontSize, command=lambda: abortFunction(), bg="grey")
        abortButton.place(relx=3 / 4, rely=0, relwidth=1 / 4, relheight=1)


class CenterFrame:
    def __init__(self, parent):



        # Data needed to setup the button
        # [ Valve Name, relx ,rely , State ID , commandID, commandOFF , commandON]
        centerButtons = [
            ['HP', .15, .85, 16, 2, 32, 33],
            ['HV', .25, .77, 17, 2, 34, 35],
            ['LV', .475, .01, 18, 3, 36, 37],
            ['LDR', .2, .45, 19, 3, 38, 39],
            ['LDV',.35, .45, 20, 3, 40, 41],
            ['FV', .475, .57, 21, 3, 42, 43],
            ['FDR', .2, .65, 22, 3, 44, 45],
            ['FDV',.35, .65, 17, 23, 3, 46, 47],
            ['LMV', .575, 0.475, 24, 2, 48, 49],
            ['FMV', .575, .3, 25, 2, 50, 51],
        ]

        for button in centerButtons:
            self.Button(parent, button)

        PGSESensors = [
            ["COPV 1", 0.125, 0.15, 0.05,0.05],
            ["COPV 2", 0.125, 0.25, 0.05,0.05],
            ["Fuel", 0.475, 0.75, 0,0.05],
            ["Lox", 0.475, 0.15, 0,0.05],
            ["Lox Dome", 0.25, 0.375, 0.05,0.05],
            ["Fuel Dome", 0.25, 0.6, 0.05,0.05],
            ["Main Valve", 0.575, 0.375, 0.05,0.05],
            ["Fuel Prop Inlet", .75, 0.35, 0.05,0.05],
            ["LOx Prop Inlet", .675, 0.45, 0.05,0.05],
            ["LOx TC1: ", .35, 0.025, 0.05,0.05],
            ["LOx TC2: ", .35, 0.15, 0.05, 0.05],
            ["LOx TC3: ", .35, 0.275, 0.05, 0.05]

        ]

        engineSensors = [
            ["Fuel Inlet", .575, .1, 0.025,0.05],
            ["Fuel Injector", .7, .1, 0.05,0.05],
            ["LOx Injector", .85, .1, 0.05,0.05],
            ["Pc Chamber 1", .55, .01, 0.05,0.05],
            ["PC Chamber 2", .7, .01, 0.05,0.05],
            ["Pc Chamber 3", .85, .01, 0.05,0.05],
            ["TC Chamber ", .85, .2, 0.05,0.05],
            ["LC1: ", .625, .7, 0.05,0],
            ["LC2:", .625, .8, 0.05,0],
            ["LC3", .625, .9, 0.05,0]
        ]

        self.sensorList = []
        for sensor in PGSESensors:
            self.sensorList.append(self.PGSESensor(parent, sensor))

        for sensor in engineSensors:
            self.sensorList.append(self.EngineSensor(parent, sensor))

        self.RefreshLabel()

    def RefreshLabel(self):
        for sensor in self.sensorList:
            sensor.RefreshLabel()
        self.sensorList[1].ReadingLabel.after(250, self.RefreshLabel)

    class PGSESensor():
        def __init__(self, parent, args):
            self.label = tk.Label(parent, text=args[0], font=("Verdana", 13), fg='white', bg='black')
            self.label.place(relx=args[1], rely=args[2], anchor="nw")
            self.ReadingLabel = tk.Label(parent, text="N/A", font=("Verdana", 13), fg='orange', bg='black')
            self.ReadingLabel.place(relx=args[1]+args[3], rely=args[2] + args[4], anchor="nw")
            # self.SensorID = args[3]

        def RefreshLabel(self):
            value = 999  # CanRecieve.getVar(self.SensorID)
            self.ReadingLabel.config(text=value)

    class EngineSensor():
        def __init__(self, parent, args):
            self.label = tk.Label(parent, text=args[0], font=("Verdana", 13), fg='white', bg='black')
            self.label.place(relx=args[1], rely=args[2], anchor="nw")
            self.ReadingLabel = tk.Label(parent, text="N/A", font=("Verdana", 13), fg='orange', bg='black')
            self.ReadingLabel.place(relx=args[1] + args[3], rely=args[2] + args[4], anchor="nw")
            # self.SensorID = args[3]

        def RefreshLabel(self):
            value = 999  # CanRecieve.getVar(self.SensorID)
            self.ReadingLabel.config(text=value)

    class Button:
        def __init__(self, parent, args):
            self.Button = tk.Button(parent, text=args[0], command=lambda: self.TwoFactorAuthentication(),
                                    font=("Verdana", 13),
                                    fg='red', bg='black')
            self.Button.place(relx=args[1], rely=args[2])
            self.status = False
            self.commandID = args[4]
            self.commandOFF = args[5]
            self.commandON = args[6]
            self.args = args
            self.parent = parent
            self.time1 = time.time()
            self.time2 = 0

        def TwoFactorAuthentication(self):
            if abs(self.time2 - self.time1) < 1:
                self.time1 = time.time()
                return 0
            if time.time() - self.time1 > 1:
                self.time1 = time.time()
            else:
                self.ValveActuaction()
                self.time1 = time.time()
            return 0

        def ValveActuaction(self):
            if LeftFrame.TestState == False:
                return 0
            self.time2 = time.time()
            if not self.status:
                self.status = True
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.TwoFactorAuthentication(),
                                        font=("Verdana", 13), fg='green', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandON], is_extended_id=False)
                bus.send(msg)
            else:
                self.status = False
                self.Button = tk.Button(self.parent, text=self.args[0], command=lambda: self.TwoFactorAuthentication(),
                                        font=("Verdana", 13), fg='red', bg='black')
                self.Button.place(relx=self.args[1], rely=self.args[2])
                msg = can.Message(arbitration_id=self.commandID, data=[self.commandOFF], is_extended_id=False)
                bus.send(msg)
            return 0

class TimeFrame:
    def __init__(self, parent):
        timeFrame = tk.Frame(parent, bg="black", bd=5)
        timeFrame.place(relx=.825, rely=.035, relwidth=.175, relheight=0.05)

        #clockFrame = self.TelemetryNode(timeFrame)
        
class RightFrame:
    def __init__(self, parent):
        rightFrame = tk.Frame(parent, bg="grey", bd=5)
        rightFrame.place(relx=.815, rely=.07, relwidth=.19, relheight=.95)

        graph1 = self.Graph1(rightFrame)
        graph2 = self.Graph2(rightFrame)
        graph3 = self.Graph3(rightFrame)

    class Graph1:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx=0, rely=0, relwidth=1, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f1, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph2:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx=0, rely=(1 / 3 + 0.0015) * 1, relwidth=1, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f2, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    class Graph3:
        def __init__(self, parent):
            graphframe = tk.Frame(parent, bg="grey", bd=5)
            graphframe.place(relx=0, rely=(1 / 3 + 0.0015) * 2, relwidth=1, relheight=(1 / 3.1))

            canvas = FigureCanvasTkAgg(f3, graphframe)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, graphframe)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


f1 = Figure(figsize = (2,5), dpi = 100)
f2 = Figure(figsize = (3,5), dpi = 100)
f3 = Figure(figsize = (4,5), dpi = 100)

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

main = Main()
