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
import matplotlib as mpl
import numpy as np
import config_HRC as HRC
from lint import docstring
import time

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

class Graph:
    def __init__(self, label, parent, relx, rely, bg=black):
        self.label = label
        self.frame = Canvas(parent, bg=bg)
        self.frame.place(relx=relx, rely=rely, relwidth=.225, relheight=2 / 5)
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvasfigure = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.axis = self.figure.add_subplot()
        self.canvasfigure.get_tk_widget().pack()

class TransformBox:
    def __init__(self,
            origin: tuple[float, float],
            dx:     tuple[float, float],
            dy:     tuple[float, float]):
        self.origin, self.dx, self.dy = tuple(map(np.array, (origin, dx, dy)))
        self.coords = np.array([dx, dy]).T
        self.affine = np.array([dx, dy, origin]).T
        self.transform = np.pad(self.affine, ((0,1), (0,0)), mode='constant', constant_values=0)
        self.transform[-1, -1] = 1

    def __str__(self):
        return str(self.affine)

    def __repr__(self):
        return str(self)
    
    def __call__(self, pts):
        pts = np.array(pts)
        if len(pts.shape) == 1:
            #return self.origin + self.dx*pts[0] + self.dy*pts[1]
            return self.origin + (self.coords @ pts.T).T

        pts = np.pad(pts, ((0,0), (0,1)), mode='constant', constant_values=1)
        #return pts @ self.affine.T
        return (pts @ self.transform.T)[:, :-1]

    def __mul__(self, right):
        res = self.transform @ right.transform
        dx, dy, origin = res[:-1].T
        return TransformBox(origin, dx, dy)

    def asRelArgs(self, pts, anchor='center', **args):
        pts = self(pts)
        res = dict(**args)
        res.update(dict(relx=pts[0], rely=pts[1], anchor=anchor))
        return res

    def asAbsArgs(self, pts, anchor='center', **args):
        pts = self(pts)
        res = dict(**args)
        res.update(dict(x=pts[0], y=pts[1], anchor=anchor))
        return res

    def inv(self):
        dx, dy, origin = np.linalg.inv(self.transform)[:-1].T
        return TransformBox(origin, dx, dy)

class ImageCache:
    def __init__(self):
        self.cache = dict()
    
    def __call__(self, src, resize=None):
        if src not in self.cache:
            self.cache[src] = Image.open(src)
            print("ImageCache: Loaded \"%s\""%src)
            if type(resize) != type(None):
                self.cache[src] = self.cache[src].resize(resize)
            self.cache[src] = ImageTk.PhotoImage(self.cache[src])
        return self.cache[src]

@docstring("""
# Base class that represents a GUI renderable object.
# 
# Otherwise, these objects are called Dynamic.
# Reset sets the object back to its initial state.
# Place relocates the object onto the display.
# Update refreshes non-render variables.
# Render performs a render.
""")
class Renderable:    
    def _args(self):
        return self.display, self.grid, self.pos, self.zorder
    
    def __init__(self, display, grid, pos, zorder=0):
        self.display = display
        self.grid = grid
        self.pos = pos

        self.zorder = zorder
        self.dirty = True

    def reset(self):
        raise NotImplementedError
    def place(self):
        raise NotImplementedError
    def render(self):
        raise NotImplementedError
    def update(self, **args):
        for k,v in args.items():
            if k in self.__dict__:
                if self.__dict__[k] == v:
                    continue
                self.__dict__[k] = v
                self.dirty = True
            else:
                raise KeyError(k)
    def onClick(self, event):
        pass # Most things do nothing when you click them.
    
class RenderableText(Renderable):
    defaultFont = None

    def __init__(self, renderable, font=None, fg=white, bg=black, text="N/A", formatter=None):
        super().__init__(*renderable._args())
        self._font = font if font is not None else RenderableText.defaultFont
        self._fg   = fg
        self._bg   = bg
        self._text = text# if formatter is None else formatter(value)
        self._fmt  = formatter
        self.reset()

        self.Label = Label(self.display, fg=self.fg, bg=self.bg, font=self.font, text=self.text)
        self.place()

        #self.Label.bind('<Double-1>', self.onClick)

    # def onClick(self, event):
    #     self.bg = green
    #     self.Label.config(bg=self.bg)
    #     self.render()

    def reset(self):
        self.font = self._font
        self.fg   = self._fg
        self.bg   = self._bg
        self.text = self._text
        self.fmt  = self._fmt
    
    def place(self):
        self.Label.place(**self.grid.asAbsArgs(self.pos))

    def updateFromValue(self, value):
        try:
            self.update(text=self.fmt(value))
        except Exception as e:
            pass
    
    def render(self):
        if not self.dirty:
            return
        self.dirty = False
        self.Label.config(text=self.text)

class RenderableImage(Renderable):
    defaultImage = None

    def __init__(self, renderable, img=None, fg=white, bg=black):
        super().__init__(*renderable._args())
        self._img  = img if img is not None else RenderableImage.defaultImage
        self._fg   = fg
        self._bg   = bg
        self.reset()

        self.Button = Button(self.display, bg=bg)
        self.place()
        self.render()
    
    def reset(self):
        self.img  = self._img
        self.fg   = self._fg
        self.bg   = self._bg
    
    def place(self):
        self.Button.place(**self.grid.asAbsArgs(self.pos))
    
    def render(self):
        if not self.dirty:
            return
        self.dirty = False
        self.Button.config(image=self.img)

class RenderableTextButton(Renderable):
    defaultFont = None

    def __init__(self, renderable, font=None, fg=white, bg=black, text="N/A", size=(64,64), onClick=lambda self, event: None):
        super().__init__(*renderable._args())
        self._font = font if font is not None else RenderableText.defaultFont
        self._fg   = fg
        self._bg   = bg
        self._text = text 
        self._size = size
        
        self.onClick = onClick
        self.reset()

        self.Button = Button(self.display, text=self.text, fg=self.fg, bg=self.bg, bd=5, font=self.font)
        self.place()

    def reset(self):
        self.font = self._font
        self.fg   = self._fg  
        self.bg   = self._bg  
        self.text = self._text
        self.size = self._size
    
    def place(self):
        self.Button.place(width=self.size[0], height=self.size[1], **self.grid.asAbsArgs(self.pos))
    
    def render(self):
        if not self.dirty:
            return
        self.dirty = False
        self.Button.config(text=self.text, fg=self.fg, bg=self.bg)

class Main:
    # Data needed to set up the Valve, Sensors, States
    # State LUT Key, VBuffer Index, color
    valves = [
        [HRC.HV_ID,    4, yellow],
        [HRC.HP_ID,    3, yellow],
        [HRC.LDR_ID,  11, blue  ],
        [HRC.FDR_ID,  13, red   ],
        [HRC.LDV_ID,   9, blue  ],
        [HRC.FDV_ID,  15, red   ],
        [HRC.LV_ID,   16, blue  ],
        [HRC.FV_ID,   19, red   ],
        [HRC.LMV_ID,  26, blue  ],
        [HRC.FMV_ID,  29, red   ],
        [HRC.IGN1_ID, 34, green ],
        [HRC.IGN2_ID, 35, green ]
    ]
    # [ 
    # Sensor LUT Key, Grid Key, Grid Position, Box Position, Box Adj, Color
    sensors = [
        [HRC.PT_LOX_HIGH_ID,      "HiPr", (  0,   0), (1, 0), (0, 1/3), yellow],
        [HRC.PT_FUEL_HIGH_ID,     "HiPr", (  1,   0), (0, 0), (0, 1/3), yellow],

        [HRC.PT_FUEL_TANK_1_ID,   "Fuel", (  0,   0), (0, 1), (0, 1/3), red   ],
        [HRC.PT_FUEL_DOME_ID,     "Fuel", (  0,   1), (0, 2), (0, 1/3), red   ],
        [HRC.PT_FUEL_TANK_2_ID,   "Fuel", (  1,   0), (0, 3), (0, 1/3), red   ],
        [HRC.PT_FUEL_INLET_ID,    "Fuel", (  1,   1), (0, 4), (0, 1/3), red   ],
        [HRC.PT_FUEL_INJECTOR_ID, "Fuel", (1/2,   2), (0, 5), (0, 1/3), red   ],

        [HRC.PT_LOX_DOME_ID,      "Loxy", (  0,   1), (1, 1), (0, 1/3), blue  ],
        [HRC.PT_LOX_TANK_1_ID,    "Loxy", (  1,   0), (1, 2), (0, 1/3), blue  ],
        [HRC.PT_LOX_TANK_2_ID,    "Loxy", (  0,   0), (1, 3), (0, 1/3), blue  ],
        [HRC.PT_LOX_INLET_ID,     "Loxy", (  1,   1), (1, 4), (0, 1/3), blue  ],
        
        [HRC.PT_CHAMBER_1_ID,     "Yeet", (  0,   0), (0, 6), (0, 1/3), green ],
        [HRC.PT_CHAMBER_2_ID,     "Yeet", (  1,   0), (0, 7), (0, 1/3), green ],
        [HRC.PT_PNUEMATICS_ID,    "Aero", (  0,   0), (0, 8), (0, 1/3), purple],

       #[HRC.PT_LOAD_CELL_1_ID,   "Yeet", (  0,   1), (1, 5), (0, 1/3), green ],
       #[HRC.PT_LOAD_CELL_2_ID,   "Yeet", (  1,   1), (1, 6), (0, 1/3), green ],
       #[HRC.PT_LOAD_CELL_3_ID,   "Yeet", (1/2, 3/2), (1, 7), (0, 1/3), green ],
    ]
    #### [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState, StateNumber]

    States = [
        [HRC.TEST,       "Test",                  (0, 8), (240, 85),  True],
        [HRC.STANDBY,    "Standby",               (0, 7), (240, 85),  True],
        [HRC.HIGH_PRESS + 4096, "Hi-Press Arm",   (0, 6), (240, 85),  False],
        [HRC.HIGH_PRESS, "Hi-Press",              (0, 5), (240, 85),  True],
        [HRC.TANK_PRESS + 4096, "Tank Press Arm", (0, 4), (240, 85),  False],
        [HRC.TANK_PRESS, "Tank Press",            (0, 3), (240, 85),  True],
        [HRC.IGNITE + 4096,     "Ignite Arm",     (0, 2), (240, 85),  False],
        [HRC.IGNITE,     "Ignite",                (0, 1), (240, 85),  True],
        [HRC.FIRE,       "FIRE",                  (0, 0), (240, 85),  True],
        [HRC.VENT,       "Vent",                  (1, 0), (180, 120), True],
        [HRC.ABORT,      "Abort",               (1.8, 0), (180, 120), True],
    ]
    Vent = [
        "Vent", 0.15, 1, 3, 9, False, 0
    ]
    Abort = [
        "Abort", .265, 1, 3, 7, False, 0
    ]
    Controllers = [
        #["Tank Controller HiPress", 2, False, yellow],
        #["Tank Controller Lox",     3, True,  blue ],  # Unused features
        #["Tank Controller Fuel",    4, True,  red  ],
        ["Engine Controller 1",      5, False, black],
        ##["Auto Sequence",            1, False, black],
        ##["Node Controller",          0, False, black],
    ]

    # System starts off in a passive state
    CurrState = HRC.STANDBY #"Passive"

    def __init__(self, canReceive, canSend, hexsha):
        self.canReceive = canReceive
        self.canSend = canSend
        self.hexsha = hexsha

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
        
        self.ThrottlePointsStorage = []
        
#         self.LOxSetPressure = 150
#         self.FuelSetPressure = 150

        self.manualOverrideState = False

        self.nodeCommandReset = 240
        self.nodeCommandID = 200

        self.ValveOptionsDropDownMenu = None
        self.statusLabel = None

        self.graphingStatus = True
        self.refreshCounter = True

        self.renderables = []

    def imagePlacement(self):
        """ Propulsion System Diagram"""

        buffer = [
            ["GUI Images/Engine_Clipart.png",        32],
            ["GUI Images/LOxTankClipart.png",        20],
            ["GUI Images/FuelTankClipart.png",       24],
            ["GUI Images/PressurantTankClipart.png",  0]
        ]

        tf = self.boxWireGrid

        for src, i in buffer:
            img = self.imageCache(src)
            label = Label(self.canvas[0], image=img, bg=black)
            label.image = img
            label.place(**self.boxWireGrid.asAbsArgs(self.Vertex_Buffer[i]))
        
    def propLinePlacement(self):
        # Lines showing the fluid flow routing in the fluid system
        aFont = tkFont.Font(family="Verdana", size=15, weight="bold")

        self.Vertex_Buffer = \
        Vertex_Buffer = [ 
            (  0,  1),
            (  0,  5), ( 12,  5), ( 16,  5), ( 12, 10),
            ( -8,  8), (  0,  8), (  8,  8),
            
            (  0, 11),
            (-12, 14), ( -8, 14), ( -4, 14), (  0, 14), ( 4, 14), (  8, 14), ( 12, 14),

            (-12, 18), ( -8, 18), (  8, 18), ( 12, 18),
            ( -8, 23), ( -4, 22), (  0, 22), (  4, 22), (  8, 23), 
            
            ( -8, 28), ( -4, 28), (-.6, 28), ( .6, 28), (  4, 28), (  8, 28),
            (-.6, 34), (  0, 34), ( .6, 34),
            
            ( 4, 32), ( 4, 35)
        ]
        # One of these vertices is unused, and a lot are unneeded.
        # They're used for positioning of valve buttons later.


        Color_Buffer = [yellow, purple, blue, red]

        Index_Buffer = [
            # High Pressure lines
            ( 0,  0,  1,  6,  8),
            ( 0,  1,  2,  3),
            ( 0,  2,  4),
            ( 0, 10,  5,  6,  7, 14),
            
            # Pnumatics
            ( 1,  8, 12, 22),
            ( 1,  9, 10, 11, 12, 13, 14, 15),
            ( 1, 26, 21, 22, 23, 29),

            # Lox
            ( 2, 10, 17, 20, 25, 26, 27, 31),
            ( 2, 16, 17),

            # Fuel
            ( 3, 14, 18, 24, 30, 29, 28, 33),
            ( 3, 18, 19)
        ]

        #self.WireDebugNumbers = []
        #for i, v in enumerate(Vertex_Buffer):
        #    self.WireDebugNumbers.append(Label(self.canvas[0], fg=orange, bg=black, font=aFont, text="%d"%i))
        #    self.WireDebugNumbers[-1].place(**self.boxWireGrid.asAbsArgs(v))

        for inds in Index_Buffer:
            color = Color_Buffer[inds[0]]
            verts = tuple(map(lambda i: self.boxWireGrid(Vertex_Buffer[i]).tolist(), inds[1:]))
            self.canvas[0].create_line(*verts, fill=color, width=5, capstyle='round')
            for i,v in zip(inds[1:], verts):
                self.canvas[0].create_line(v, v, fill=color, width=10, capstyle='round')
                #self.WireDebugNumbers.append(Label(self.canvas[0], fg=color, bg=black, font=aFont, text="%d"%i))
                #self.WireDebugNumbers[-1].place(x=v[0], y=v[1], anchor='center')
        
        # This holds the control buttons on the left.
        # self.canvas[0].create_rectangle(10, 160, 275, 1020, outline=orange, fill=black, width=5)

        RenderableText.defaultFont = aFont

        # Second display SENSORS box
        #self.SensorsLabel = Label(self.canvas[1], fg=orange, bg=black, font=aFont, text="SENSORS")
        #self.SensorsLabel.place(**self.boxSensorGrid.asAbsArgs((1/2, -2/3)))
        self.SensorsLabel = RenderableText(
            Renderable(self.canvas[1], self.boxSensorGrid, (1/2, -2/3)),
            fg=orange, text="SENSORS")

        # Second display VALVES box
        #self.ValvesLabel = Label(self.canvas[1], fg=orange, bg=black, font=aFont, text="VALVES")
        #self.ValvesLabel.place(**self.boxValveGrid.asAbsArgs((1/2, -2/3)))
        self.ValvesLabel = RenderableText(
            Renderable(self.canvas[1], self.boxValveGrid, (1/2, -2/3)),
            fg=orange, text="VALVES")
        
        # Second display ENGINE CONTROLLER box
        #self.FuelControllerLabel = Label(self.canvas[1], fg=green, bg=black, font=aFont, text="MAIN SEQUENCE")
        #self.FuelControllerLabel.place(**self.boxEngineControllerGrid.asAbsArgs((1/2, -2/3)))
        self.FuelControllerLabel = RenderableText(
            Renderable(self.canvas[1], self.boxEngineControllerGrid, (1/2, -2/3)),
            fg=orange, text="MAIN SEQUENCE")

    def ManualOverrideToggle(self, event):
        self.manualOverrideState = not self.manualOverrideState

        img = "GUI Images/ManualOverrideEnabledButton.png" if self.manualOverrideState else "GUI Images/ManualOverrideDisabledButton.png"
        self.ManualOverrideButton.update(img=self.imageCache(img))
        self.canSend.manual_override_toggle()

    def ManualOverride(self):
        self.ManualOverrideButton = RenderableImage(Renderable(self.canvas[0], self.boxButtonGrid, (1, 8)),
            img=self.imageCache("GUI Images/ManualOverrideDisabledButton.png"))
        self.ManualOverrideButton.Button.bind('<Double-1>', self.ManualOverrideToggle)

        # On double press, Call KillSwitch function
    def ThrottlePoints(self):
        if self.canReceive.ThrottlePoints != self.ThrottlePointsStorage:
            self.ThrottlePointsStorage = self.canReceive.ThrottlePoints
            aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
            print(self.canReceive.ThrottlePoints)
            for throttlepoint in range(len(self.canReceive.ThrottlePoints)):
                Timelabel = Label(self.canvas[1], text = "T + " + str(self.canReceive.ThrottlePoints[throttlepoint][0]), fg = green, bg = black, font = aFont)
                Timelabel.place(relx = 0.6, rely = 0.5 + throttlepoint*.1)
                Pressurelabel = Label(self.canvas[1], text = "Pressure: "+ str(self.canReceive.ThrottlePoints[throttlepoint][1]), fg = green, bg = black, font = aFont)
                Pressurelabel.place(relx = 0.65, rely = 0.5 + throttlepoint*.1)
    
    # Readings Refresher, Recursive Function
    def MainRefresh(self):
        if self.refreshCounter >= REFRESHRATE:
            self.refreshCounter = 0
            # for each sensor in the sensor list. refresh the label
            legendsGraphs = []
            for i in range(len(self.graphs)):
                legendsGraphs.append([])
                self.graphs[i].axis.clear()
            
            #self.ThrottlePoints()
            
            for sensor in self.sensorList:
                sensor.Refresh(True)
                if self.graphingStatus:
                    for status, legend, graph in zip(sensor.GraphStatus, legendsGraphs, self.graphs):
                        if status.get():
                            graph.axis.plot(sensor.sensorData, label=sensor.name)
                            graph.figure.canvas.draw()
                            legend.append(sensor.name)

            for legend, graph in zip(legendsGraphs, self.graphs):
                if legend:
                    graph.axis.legend(legend, loc="upper left")
                    graph.figure.canvas.draw()

            for valve in self.valveList:
                valve.refresh_valve()
            for controller in self.controllerList:
                controller.Refresh()
            for state in self.stateList:
                state.refresh()

            #self.autosequence_str = "T  " + str(self.canReceive.AutosequenceTime) + " s"
            #self.autoseqence.config(text=self.autosequence_str)
            self.time.config(text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            #self.nodeState.config(text=self.canReceive.NodeStatus)  # can_receive.node_dict_list[self.name]["state"]))

            self.ManualOverrideButton.render()

            self.sensorList[1].ReadingLabel.Label.after(GRAPHDATAREFRESHRATE, self.MainRefresh)
        else:
            for sensor in self.sensorList:
                sensor.Refresh(False)
                self.refreshCounter += GRAPHDATAREFRESHRATE

            self.sensorList[1].ReadingLabel.Label.after(GRAPHDATAREFRESHRATE, self.MainRefresh)

        self.NodeStateLabels[HRC.SR_ENGINE].config(text="Engine Node State: " + HRC.StateLUT[self.canReceive.rocketState[HRC.SR_ENGINE]])
        self.NodeStateLabels[HRC.SR_PROP  ].config(  text="Prop Node State: " + HRC.StateLUT[self.canReceive.rocketState[HRC.SR_PROP]])

        now_micros = time.time_ns() / 1000
        labeldata = [
            [HRC.SR_ENGINE, "Engine"],
            [HRC.SR_PROP,  "Prop"],
        ]
        for ID, name in labeldata:
            secs = (now_micros - self.canReceive.timeLastRecievedPing_micros[ID])/1e6

            timeout_secs = 10.0
            s = 1.0 - max(0.0, min(secs, timeout_secs))/timeout_secs
            color = self.PingLabelCMap(s)
            vals = ["{0:02x}".format(int(255*c)) for c in color[:-1]]
            color = "#" + "".join(vals)

            #color = green if secs < 3.0 else red
            self.PingLabels[ID].config(text="Last %s Ping: %.3f s"%(name, secs), fg=color)

        now = datetime.datetime.now().timestamp()
        if 1 < now - self.lastPingTime:
            self.lastPingTime = now
            self.canSend.ping()

    def StateReset(self):
        Main.CurrState = HRC.STANDBY
        # Store previosly instantiated State. Arm States may be able to access the state before it
        prevState = None
        # Every state in State Array gets instantiated and a Button is made for it
        for state in Main.States:
            button = States(self.canvas, self.canReceive, self.canSend, state, self.boxButtonGrid, self, prevState=prevState)
            # Creates the button and places it into the Frame. May change name later since it really inst instantiating
            button.MainStateInstantiation()
            # Updates the prevState so that the next state may be able to access it. Its pretty much a Linked List
            prevState = button

    def AutoSequence(self):
        self.autoseqence = Label(self.canvas[0], text="Boom Boom \n wont go boom boom", bg="black", fg="Green",
                                 font=("Verdana", 25))
        self.autoseqence.place(relx=.3, rely=0.1)
        self.autosequence_str = ""

    def PauseGraphs(self):
        #print(self.graphingStatus)
        self.graphingStatus = not self.graphingStatus

    def GenerateGraphs(self):

        self.pauseButton = Button(self.canvas[1], font=("Verdana", 10), fg='red', bg='black',
                                  text="GRAPH PAUSE\nBUTTON", command=lambda: self.PauseGraphs())
        self.pauseButton.place(relx=.85, rely=.45)

        self.graphs = [
            Graph("Graph 1", self.canvas[0], .775, .1 ),
            Graph("Graph 2", self.canvas[0], .775, .6 ),
            Graph("Graph 3", self.canvas[1], .775, .05),
            Graph("Graph 4", self.canvas[1], .775, .5 ),
        ]

    def GenerateBoxes(self):
        self.boxWireGrid = TransformBox((752, 50), (25,0), (0,25))

        boxSensorGrid = TransformBox((115.2, 124.2), (192, 0), (0, 81))
        boxValveGrid = TransformBox(boxSensorGrid((2,0)), (0.75*192, 0), (0, 81))
        boxEngineControllerGrid = TransformBox(boxValveGrid((0,7 + 1/6)), (0.75*192,0), (0,81))
        
        self.boxSensorGrid = boxSensorGrid
        self.boxValveGrid = boxValveGrid
        self.boxEngineControllerGrid = boxEngineControllerGrid

        # Main display boxes
        boxLoxGrid = TransformBox((355.2, 648), (96, 0), (0, 108))
        boxEngineGrid = TransformBox((1056, 635.04), (96, 0), (0, 108))
        boxFuelGrid = TransformBox(boxEngineGrid((2.5,0)), (96, 0), (0, 108))
        boxAeroGrid = TransformBox((748.8, 669.6), (96, 0), (0, 108))
        boxHighPress = TransformBox((912, 81), (96, 0), (0, 108))
        boxButtonGrid = TransformBox((144, 950), (240, 0), (0, -90))
        
        self.boxLoxGrid = boxLoxGrid
        self.boxEngineGrid = boxEngineGrid
        self.boxFuelGrid = boxFuelGrid
        self.boxAeroGrid = boxAeroGrid
        self.boxHighPress = boxHighPress
        self.boxButtonGrid = boxButtonGrid

        self.dictBoxGridsMain = dict(
            Loxy=self.boxLoxGrid,
            Yeet=self.boxEngineGrid,
            Fuel=self.boxFuelGrid,
            Aero=self.boxAeroGrid,
            HiPr=self.boxHighPress
        )

    def GenerateBoxDebug(self):

        pts = np.array([[0,0], [1,0], [1,1], [0,1], [0,0]])

        buffer = [
            # Display 1 Boxes
            [0, self.boxLoxGrid,    (-2/3, -1/2), 2+1/3, 2,     1, blue],
            [0, self.boxEngineGrid, (-2/3, -1/2), 2+1/3, 2+1/3, 1, green],
            [0, self.boxFuelGrid,   (-2/3, -1/2), 2+1/3, 3,     1, red],
            [0, self.boxAeroGrid,   (-2/3, -1/2), 1+1/3, 1,     1, purple],
            [0, self.boxHighPress,  (-2/3, -1/2), 2+1/3, 1,     1, yellow],
            [0, self.boxButtonGrid, (-0.55, -0.6), 2*0.55, 2*0.6+8, 5, orange],

            # Display 2 Boxes
            [1, self.boxSensorGrid,           (-0.5,-1.25), 2, 10,   5, orange],
            [1, self.boxValveGrid,            (-0.5,-1.25), 2, 7,    5, orange],
            [1, self.boxEngineControllerGrid, (-0.5,-1),    2, 3.5,  5, green],
        ]

        displays = [self.canvas[0], self.canvas[1]]
        
        for di, tf, pt, dx, dy, width, color in buffer:
            tf = tf * TransformBox(pt, (dx,0), (0,dy))
            displays[di].create_line(*tf(pts).tolist(), fill=color, width=width, joinstyle='miter')

        # DEBUG
        # self.button = Button(self.canvas[0], text="Test state report", fg='red', bg='black', bd=5,
        #                      command=lambda: self.canSend.TEST_send_state_reports(self.canReceive), font=20)
        # self.button.place(x=1500, y=400, width=256, height=256)

    def TimingSettingsPopUp(self):
        self.TimerPopUp = Toplevel(self.window[0], background=grey)
        self.TimerPopUp.geometry("750x250")
        self.chosenTimingFunction = None
        clicked = StringVar()
        clicked.set("Choose Object")
        self.TimerOptions = [x[1].replace('\n', ' ') for x in self.TimingCommands]

        self.TimerChoiceDropDown = OptionMenu(self.TimerPopUp, clicked, *self.TimerOptions,
                                                   command=lambda Sensor2: self.TimingDropDownMenu(Sensor2, self.TimerOptions))
        self.TimerChoiceDropDown.place(relx=0.2, rely=0.5)
        #self.TimerFunctionLabel = Label(self.TimerPopUp, bg=grey)
        #self.TimerFunctionLabel.place(relx=.5, rely=0.4)
    
    def TimingDropDownMenu(self, object, options):
        self.TimerDataEntryButton = Button(self.TimerPopUp, height=1, width=10, background="grey50",
                                                    text="Enter")
        self.TimerDataEntryButton.place(relx=.5, rely=.7)
        self.TimerstatusLabel = Label(self.TimerPopUp, font=("Helvetica", 12), bg=grey)
        self.TimerstatusLabel.place(relx=.7, rely=0.6)
        self.TimerSetData = StringVar()
        self.TimerSetDataEntry = Entry(self.TimerPopUp, background="grey50",
                                            textvariable=self.TimerSetData)
        self.TimerSetDataEntry.place(relx=.5, rely=.5)

        self.Timingcommand = self.TimingCommands[options.index(object)][2]
        self.TimerDataEntryButton.config(
                command=lambda: self.TimingParse()
            )

    def TimingParse(self):
        self.TimerFunctionLabel = Label(self.TimerPopUp, bg=grey)
        self.TimerFunctionLabel.place(relx=.5, rely=0.4)
        try:
            self.Timingcommand(int(float(self.TimerSetData.get())))
            self.TimerFunctionLabel.config(text="Command sent!")
        except Exception as e:
            self.TimerFunctionLabel.config(text=e)

    def SensorCalibPopUp(self):
        self.SensorCalibPopUp = Toplevel(self.window[0], background=grey)
        self.SensorCalibPopUp.geometry("750x250")
        self.SensorCalibEntries = [None, None, None]

        SensorCalibItems = [[sensor, HRC.SensorLUT[sensor]['name'].replace('\n', ' ')] for sensor in HRC.SensorLUT.keys()]
        self.SensorCalibLUT = {name:ID for ID,name in SensorCalibItems}
        
        clickedOpt = StringVar()
        clickedOpt.set("Choose Sensor")
        self.SensorCalibOptions = [name for ID,name in SensorCalibItems]
        self.SensorCalibOptChoiceDropDown = OptionMenu(self.SensorCalibPopUp, clickedOpt, *self.SensorCalibOptions,
                                                   command=lambda Sensor2: self.SensorCalibGate(0, Sensor2))
        self.SensorCalibOptChoiceDropDown.place(relx=0.2, rely=0.25)

        clickedVar = StringVar()
        clickedVar.set("Choose Variable")
        self.SensorCalibVariable = "m b".split(' ')
        self.SensorCalibVarChoiceDropDown = OptionMenu(self.SensorCalibPopUp, clickedVar, *self.SensorCalibVariable,
                                                   command=lambda Sensor2: self.SensorCalibGate(1, Sensor2))
        self.SensorCalibVarChoiceDropDown.place(relx=0.4, rely=0.25)

        clickedCom = StringVar()
        clickedCom.set("Choose Direction")
        self.SensorCalibCommand = "Set Get".split(' ')
        self.SensorCalibComChoiceDropDown = OptionMenu(self.SensorCalibPopUp, clickedCom, *self.SensorCalibCommand,
                                                   command=lambda Sensor2: self.SensorCalibGate(2, Sensor2))
        self.SensorCalibComChoiceDropDown.place(relx=0.6, rely=0.25)
        #self.SensorCalibFunctionLabel = Label(self.SensorCalibPopUp, bg=grey)
        #self.SensorCalibFunctionLabel.place(relx=.5, rely=0.4)
    
    def SensorCalibGate(self, item, value):
        self.SensorCalibEntries[item] = value

        for item in self.SensorCalibEntries:
            if item is None:
                return
        
        self.SensorCalibDropDownMenu()

    def SensorCalibDropDownMenu(self):
        self.SensorCalibDataEntryButton = Button(self.SensorCalibPopUp, height=1, width=10, background="grey50",
                                                    text="Enter")
        self.SensorCalibDataEntryButton.place(relx=.5, rely=.7)
        self.SensorCalibstatusLabel = Label(self.SensorCalibPopUp, font=("Helvetica", 12), bg=grey)
        self.SensorCalibstatusLabel.place(relx=.7, rely=0.6)
        self.SensorCalibSetData = StringVar()
        self.SensorCalibSetDataEntry = Entry(self.SensorCalibPopUp, background="grey50",
                                            textvariable=self.SensorCalibSetData)
        self.SensorCalibSetDataEntry.place(relx=.5, rely=.5)

        print("shit happens here")
        print(self.SensorCalibEntries)

        #self.SensorCalibCommand = self.TimingCommands[options.index(object)][2]
        self.SensorCalibDataEntryButton.config(
                command=lambda: self.SensorCalibParse()
            )

    def SensorCalibParse(self):
        self.SensorCalibFunctionLabel = Label(self.SensorCalibPopUp, bg=grey)
        self.SensorCalibFunctionLabel.place(relx=.5, rely=0.7)
        try:
            ID = self.SensorCalibLUT[self.SensorCalibEntries[0]]
            var = 0 if "m" else 1

            if self.SensorCalibEntries[2] == "Set":
                value = float(self.SensorCalibSetData.get())
                self.canSend.set_calibration_values(ID, var, value)
            else:
                self.canSend.get_calibration_values(ID, var)

            self.SensorCalibFunctionLabel.config(text="Command sent!")
        except Exception as e:
            self.SensorCalibFunctionLabel.config(text=e)
    
    def getAllSensorCalibVals(self):
        for ID in HRC.SensorLUT.keys():
            self.canSend.get_calibration_values(ID, 0)
            self.canSend.get_calibration_values(ID, 1)

    def Menus(self, parent, app):
        self.menu = Menu(parent, background="grey50", fg=black)
        self.fileMenu = Menu(self.menu)

        # Dropdown menus in the top left
        self.graphsMenu = Menu(self.menu)
        self.graphsSubmenus = [Menu(self.menu) for g in self.graphs]

        self.Commands_Vehicle = Menu(self.menu)
        self.Commands_Valves = Menu(self.menu)
        self.Commands_Timing = Menu(self.menu)
        self.Commands_Misc = Menu(self.menu)

        for menu, graph in zip(self.graphsSubmenus, self.graphs):
            self.graphsMenu.add_cascade(label=graph.label, menu=menu)
        
        self.menu.add_cascade(label="Graphs", menu=self.graphsMenu)
        self.menu.add_cascade(label="Vehicle Commands", menu=self.Commands_Vehicle)
        self.menu.add_cascade(label="Valve Commands",   menu=self.Commands_Valves)
        self.menu.add_cascade(label="Timing Commands",  menu=self.Commands_Timing)
        self.menu.add_cascade(label="Misc Commands",    menu=self.Commands_Misc)

        # Vehicle commands
        commands = [
            dict(label=HRC.StateLUT[HRC.ABORT     ].replace('_',' '), command=self.canSend.abort),
            dict(label=HRC.StateLUT[HRC.VENT      ].replace('_',' '), command=self.canSend.vent),
            dict(label=HRC.StateLUT[HRC.FIRE      ].replace('_',' '), command=self.canSend.fire),
            dict(label=HRC.StateLUT[HRC.TANK_PRESS].replace('_',' '), command=self.canSend.tank_press),
            dict(label=HRC.StateLUT[HRC.HIGH_PRESS].replace('_',' '), command=self.canSend.high_press),
            dict(label=HRC.StateLUT[HRC.STANDBY   ].replace('_',' '), command=self.canSend.standby),
            dict(label=HRC.StateLUT[HRC.IGNITE    ].replace('_',' '), command=self.canSend.ignite),
            dict(label=HRC.StateLUT[HRC.TEST      ].replace('_',' '), command=self.canSend.test)
        ]
        for command in commands:
            self.Commands_Vehicle.add_command(**command)

        # Valves & Igniters
        def label(ID, state):
            lut = HRC.ToggleLUT[ID]
            return lut['name'] + ' ' + lut['statestr'][lut['states'].index(state)]
        
        commands = [
            dict(label=label(HRC.IGN1_ID, HRC.IGN1_OFF),  command=self.canSend.ign1_off),
            dict(label=label(HRC.IGN1_ID, HRC.IGN1_ON),   command=self.canSend.ign1_on),
            dict(label=label(HRC.IGN2_ID, HRC.IGN2_OFF),  command=self.canSend.ign2_off),
            dict(label=label(HRC.IGN2_ID, HRC.IGN2_ON),   command=self.canSend.ign2_on),
            dict(label=label(HRC.HP_ID,   HRC.HP_CLOSE),  command=self.canSend.hp_close),
            dict(label=label(HRC.HP_ID,   HRC.HP_OPEN),   command=self.canSend.hp_open),
            dict(label=label(HRC.HV_ID,   HRC.HV_CLOSE),  command=self.canSend.hv_close),
            dict(label=label(HRC.HV_ID,   HRC.HV_OPEN),   command=self.canSend.hv_open),
            dict(label=label(HRC.FMV_ID,  HRC.FMV_CLOSE), command=self.canSend.fmv_close),
            dict(label=label(HRC.FMV_ID,  HRC.FMV_OPEN),  command=self.canSend.fmv_open),
            dict(label=label(HRC.LMV_ID,  HRC.LMV_CLOSE), command=self.canSend.lmv_close),
            dict(label=label(HRC.LMV_ID,  HRC.LMV_OPEN),  command=self.canSend.lmv_open),
            dict(label=label(HRC.LV_ID,   HRC.LV_CLOSE),  command=self.canSend.lv_close),
            dict(label=label(HRC.LV_ID,   HRC.LV_OPEN),   command=self.canSend.lv_open),
            dict(label=label(HRC.LDV_ID,  HRC.LDV_CLOSE), command=self.canSend.ldv_close),
            dict(label=label(HRC.LDV_ID,  HRC.LDV_OPEN),  command=self.canSend.ldv_open),
            dict(label=label(HRC.LDR_ID,  HRC.LDR_CLOSE), command=self.canSend.ldr_close),
            dict(label=label(HRC.LDR_ID,  HRC.LDR_OPEN),  command=self.canSend.ldr_open),
            dict(label=label(HRC.FV_ID,   HRC.FV_CLOSE),  command=self.canSend.fv_close),
            dict(label=label(HRC.FV_ID,   HRC.FV_OPEN),   command=self.canSend.fv_open),
            dict(label=label(HRC.FDV_ID,  HRC.FDV_CLOSE), command=self.canSend.fdv_close),
            dict(label=label(HRC.FDV_ID,  HRC.FDV_OPEN),  command=self.canSend.fdv_open),
            dict(label=label(HRC.FDR_ID,  HRC.FDR_CLOSE), command=self.canSend.fdr_close),
            dict(label=label(HRC.FDR_ID,  HRC.FDR_OPEN),  command=self.canSend.fdr_open),
        ]
        for command in commands:
            self.Commands_Valves.add_command(**command)

        # Timing
        self.TimingCommands = [
            [HRC.GET_LMV_OPEN,  "LOX MV\nOpen",   self.canSend.set_lmv_open],
            [HRC.GET_LMV_CLOSE, "LOX MV\nClose",  self.canSend.set_lmv_close],
            [HRC.GET_FMV_OPEN,  "Fuel MV\nOpen",  self.canSend.set_fmv_open],
            [HRC.GET_FMV_CLOSE, "Fuel MV\nClose", self.canSend.set_fmv_close],
            [HRC.GET_IGNITION,  "Ignition\nTime", self.canSend.set_ignition],
        ]
        self.Commands_Timing.add_command(label="Update timing", command=self.TimingSettingsPopUp)
        self.Commands_Timing.add_command(label="Request timing", command=self.canSend.getDefaultTiming)
        self.canSend.getDefaultTiming()

        # Misc
        commands = [
            dict(label="Ping",               command=self.canSend.ping),
            dict(label="Zero PTs",           command=self.canSend.zero_pts),
            dict(label="Sensor Calibration", command=self.SensorCalibPopUp),
            dict(label="Get All Sensor Calibrations", command=self.getAllSensorCalibVals),
            dict(label="Start Data Logging", command=self.canSend.start_data_logging)
        ]
        for command in commands:
            self.Commands_Misc.add_command(**command)

        app.config(menu=self.menu)

        for sensor in self.sensorList:
            for menu, status in zip(self.graphsSubmenus, sensor.GraphStatus):
                menu.add_checkbutton(label=sensor.name, variable=status)

    def run(self):  # This takes place of the init
        """ TKinter Initialization"""
        # self.pr = cProfile.Profile()
        # self.pr.enable()
        
        self.ArmTankPress = False
        self.ArmHighPress = False
        self.ArmIgnite = False

        self.root = Tk()
        self.window = []
        self.canvas  = []
        for resolution in ["1920x1080", "1920x1080+1920+0"]:

            # Generates the windows
            window = Toplevel(self.root)
            window.configure(background=black)
            window.geometry(resolution)

            # Generates associated canvasses
            canvasArgs = dict(bg=black, highlightbackground=black, highlightthickness=0)
            canvas = Canvas(window, **canvasArgs)
            canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.window.append(window)
            self.canvas.append(canvas)

        self.imageCache = ImageCache()

        self.aFont = tkFont.Font(family="Verdana", size=10, weight="bold")

        buffer = [
            ["Prop Node State",   HRC.SR_PROP,   20, 22],
            ["Engine Node State", HRC.SR_ENGINE, 20, 76],
        ]
        self.NodeStateLabels = dict()
        for name, ID, x, y in buffer:
            label = Label(self.canvas[0], text=name, fg=orange, bg=black, font=("Arial", 25))
            label.place(x=x, y=y)
            self.NodeStateLabels[ID] = label

        self.GenerateBoxes()
        self.propLinePlacement()
        self.imagePlacement()
        #self.AutoSequence()
        #self.StateReset()
        self.GenerateGraphs()
        self.GenerateBoxDebug()
        

        # self.Vent = States(self.canvas[0], Main.Vent, self.canSend)
        # self.Vent.VentAbortInstantiation()
        # self.Abort = States(self.canvas[0], Main.Abort, self.canSend)
        # self.Abort.VentAbortInstantiation()
        # Instantiates Every Valve
        for valve in Main.valves:
            self.valveList.append(Valves(self.canvas, self.canReceive, self.canSend, valve, self.boxValveGrid, self.boxWireGrid, self.Vertex_Buffer, self.imageCache))

        # Instantiates Every Sensor
        for sensor in Main.sensors:
            self.sensorList.append(Sensors(self.canvas, self.canReceive, self.canSend, sensor, self.graphs, self.boxSensorGrid, self.dictBoxGridsMain))

        # Instantiates Every Sensor
        for controller in Main.Controllers:
            self.controllerList.append(Controller(self.canvas, self.canReceive, self.canSend, controller, self.boxEngineControllerGrid))

        # Instantiates Every State (buttons)
        self.stateList = []
        for state in Main.States:
            self.stateList.append(States(self.canvas, self.canReceive, self.canSend, state, self.boxButtonGrid, self))

        self.Menus(self.canvas[0], self.window[0])
        self.Menus(self.canvas[1], self.window[1])

        self.time = Label(self.canvas[0], fg="Orange", bg=black,
                          text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), font=("Verdana", 17))
        self.time.place(relx=.85, rely=0.01)
        self.hexshaLabel = Label(self.canvas[0], fg="Orange", bg=black,
                          text=self.hexsha, font=("Verdana", 17))
        self.hexshaLabel.place(relx=.85, rely=0.01+0.04)

        self.PingLabels = {}
        self.PingLabels[HRC.SR_ENGINE] = Label(self.canvas[0], fg="Orange", bg=black,
                          text="Last Engine Ping:", font=("Verdana", 17))
        self.PingLabels[HRC.SR_ENGINE].place(relx=.65, rely=0.01)

        self.PingLabels[HRC.SR_PROP] = Label(self.canvas[0], fg="Orange", bg=black,
                          text="Last Prop Ping:", font=("Verdana", 17))
        self.PingLabels[HRC.SR_PROP].place(relx=.65, rely=0.01+0.04)

        self.PingLabelCMap = mpl.colormaps.get_cmap("RdYlGn")

        self.ManualOverride()
        # self.ManualOverridePhoto = self.imageCache("GUI Images/ManualOverrideDisabledButton.png")
        # self.ManualOverrideButton = Button(self.canvas[0], image=self.ManualOverridePhoto, fg='red', bg='black',
        #                                    bd=5)
        # self.ManualOverrideButton.place(relx=.7, rely=0.2)
        # self.ManualOverrideButton.bind('<Double-1>', self.ManualOverride)  # bind double left clicks

        

        # RefreshLabel() Refreshes the Readings
        self.lastPingTime = datetime.datetime.now().timestamp()
        self.canSend.ping()
        self.MainRefresh()

        """ Runs GUI Loop"""
        self.window[0].attributes("-fullscreen",
                                      True)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen

        def kill(event):
            self.window[0].destroy()
            # self.pr.disable()
            # print("Profile done, collecting stats.")
            # s = io.StringIO()
            # ps = pstats.Stats(self.pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
            # ps.print_stats(100)
            # for line in s.getvalue().split('\n'):
            #     print(line)

        self.window[0].bind("<Escape>", kill)  # binds escape key to killing the window
        self.window[0].bind("<F11>",
                                lambda event: self.window[0].attributes("-fullscreen",
                                                                            True))  # switches from zoomed to fullscreen
        self.window[0].bind("<F12>",
                                lambda event: self.window[0].attributes("-fullscreen",
                                                                            False))  # switches from fullscreen to zoomed

        self.window[1].attributes("-fullscreen",
                                        False)  # "zoomed" is fullscreen except taskbars on startup, "fullscreen" is no taskbars true fullscreen
        self.window[1].bind("<Escape>", lambda
            event: self.window[1].destroy())  # binds escape key to killing the window
        self.window[1].bind("<F11>",
                                  lambda event: self.window[1].attributes("-fullscreen",
                                                                                True),
                                  lambda event: self.window[1].geometry(
                                      "1920x1080-1920+0"))  # switches from zoomed to fullscreen
        # self.window[1].bind("<F11>",
        #                           lambda event: self.window[1].geometry("1920x1080-1920+0"))  # switches from zoomed to fullscreen

        self.window[1].bind("<F12>",
                                  lambda event: self.window[1].attributes("-fullscreen",
                                                                                False))  # switches from fullscreen to zoomed
        self.root.withdraw()

        #self.GenerateBoxDebug()

        while True:
            # Non blocking update
            self.root.update_idletasks()
            self.root.update()
        #self.root.mainloop()
        #self.window[0].mainloop()


class Sensors:
    numOfSensors = 0

    def __init__(self, canvas, canReceive, canSend, args, graphs, boxSensorGrid, dictBoxGridsMain):
        # Sensor LUT Key, Grid Key, Grid Position, Box Position, Box Adj, Color
        # [HRC.PT_LOX_HIGH_ID,      "HiPr", (  0,   0), (1, 0), (0, 1/3), yellow],

        self.id, self.grid, self.xy0, self.xy1, self.xyoff, self.color = args

        self.canReceive = canReceive
        self.canSend = canSend
        self.canvas = canvas

        self.sensorData = [0] * 100
        self.GraphStatus = [IntVar() for g in graphs]
        self.index = 0

        self.name = HRC.SensorLUT[self.id]['name']
        self.xy0, self.xy1, self.xyoff = tuple(map(np.array, [self.xy0, self.xy1, self.xyoff]))

        # self.dataList = []
        fontTitle  = tkFont.Font(family="Verdana", size=10, weight="bold")
        fontValue1 = tkFont.Font(family="Verdana", size=12)
        fontValue2 = tkFont.Font(family="Verdana", size=9)

        ### 1st Display
        pt = np.array(self.xy0)
        adj = TransformBox(pt, (1/2,0), (0,1/2))
        tf = dictBoxGridsMain[self.grid] * adj
        
        # self.label corresponds with the main screen box labels, as their titles.
        self.label = RenderableText(Renderable(self.canvas[0], tf, -self.xyoff),
            font=fontTitle, fg=self.color, text=self.name)
        
        # self.ReadingLabel is the corresponding value for this box.
        self.ReadingLabel = RenderableText(Renderable(self.canvas[0], tf, self.xyoff),
            font=fontValue1, fg=orange, formatter=lambda v: "%.1f psi"%float(v))

        # Draws the background box
        pts = np.array([[-1, -1], [-1, 1], [1,1], [1,-1], [-1,-1]])
        tf = tf * TransformBox((0,0), (6/7,0), (0,1/3))
        self.canvas[0].create_line(*tf(pts).tolist(), fill=self.color, width=1, capstyle='projecting', joinstyle='miter')

        
        ### 2nd Display
        #pt = np.array([Sensors.numOfSensors % 2, Sensors.numOfSensors // 2])
        pt = np.array(self.xy1)
        adj = TransformBox(pt, (1/5,0), (0,1))
        tf = boxSensorGrid * adj

        # self.label2 is the sensor title in the SENSORS box.
        self.label2 = RenderableText(Renderable(self.canvas[1], tf, (-1, 0)),
            font=fontTitle, fg=self.color, text=self.name)
        
        # self.ConvReadingLabel2 is the corresponding value for this box.
        self.ConvReadingLabel2 = RenderableText(Renderable(self.canvas[1], tf, (1, 0)),
            font=fontValue2, fg=orange, formatter=lambda v: "%.1f psi"%float(v))

        # Draws the background box
        pts = np.array([[-1, -1], [-1, 1], [1,1], [1,-1], [-1,-1]])
        tf = tf * TransformBox((0,0), (1,0), (0,1/3))
        self.canvas[1].create_line(*tf(pts).tolist(), fill=self.color, width=1, capstyle='projecting', joinstyle='miter')

        Sensors.numOfSensors += 1

    # Updates the reading
    # Gets called by the PropulsionFrame class
    def Refresh(self, LabelRefresh):
        value = random.randint(1, 100)
        if CanStatus:
            value = self.canReceive.Sensor_Val[self.id]
        self.sensorData = self.sensorData[1:] + self.sensorData[:1]
        self.sensorData[-1] = value
        self.index += 1
        if LabelRefresh:
            # The first call are to the main display boxes,
            # the second call is to the Sensors box.
            #self.ReadingLabel.config(fg=orange, text=str(value) + " psi")  # Updates the label with the updated value
            #self.ConvReadingLabel2.config(fg=orange, text=str(value) + " psi")
            #self.RawReadingLabel2.config(text=str(self.canReceive.Sensors[self.idRaw]))

            self.ReadingLabel.updateFromValue(value)
            self.ConvReadingLabel2.updateFromValue(value)

            self.ReadingLabel.render()
            self.ConvReadingLabel2.render()

class Valves:
    numOfValves = 0
    gui_state_offset = 4096

    def imgFromState(self):
        status = self.StatusStates[self.status] 
        enable = self.EnableStates[self.enable]
        select = '-'.join([self.photo_name, status, enable])
        return self.imageCache("Valve Buttons/%s.png"%select, resize=(72,72))

    def __init__(self, canvas, canReceive, canSend, args, boxValveGrid, boxWireGrid, Vertex_Buffer, imageCache):
        # State LUT Key, VBuffer Index, color
        # [HRC.HV_ID,    4, yellow],

        self.id, self.index, self.color = args

        self.canReceive = canReceive
        self.canSend = canSend
        self.imageCache = imageCache
        self.canvas = canvas
        self.state = False
        self.nick = HRC.ToggleLUT[self.id]['nick']
        self.photo_name = self.nick.replace(' ','')
        self.status = 69  # Keeps track of valve actuation state

        self.commandID = 1

        fontTitle = tkFont.Font(family="Verdana", size=10, weight="bold")
        fontValue = tkFont.Font(family="Verdana", size=9)

        # LP and FP do not have stale states.
        # Do those valves still exist?
        lut = HRC.ToggleLUT[self.id]
        self.StatusStates = {k:v for k,v in zip(lut['states'], lut['statestr'])}
        self.StatusStates[lut['states'][0]+self.gui_state_offset] = "FireCommanded"
        self.StatusStates[lut['states'][1]+self.gui_state_offset] = "Stale"
        self.EnableStates = {i:e for i,e in enumerate(["EnableOff", "EnableOn", "EnableStale"])}

        # Precache valve photos
        #for status in self.StatusStates:
        #    for enable in self.EnableStates:
        #        self.status, self.enable = status, enable
        #        self.imgFromState()

        self.status, self.enable = max(self.StatusStates), 2
        self.photo = self.imgFromState()

        # Displays a button on a vertex in the propline diagram.
        self.Button = RenderableImage(Renderable(self.canvas[0], boxWireGrid, Vertex_Buffer[self.index]),
            img=self.photo)
        self.Button.Button.bind('<Double-1>', self.ValveActuation)

        # Displays valve info on the 2nd display
        pt = np.array([Valves.numOfValves % 2, Valves.numOfValves // 2])
        adj = TransformBox(pt, (1/6,0), (0,1/6))
        tf = boxValveGrid * adj

        self.label2 = RenderableText(Renderable(self.canvas[1], tf, (-1, 0)),
            font=fontTitle, fg=self.color, text=self.nick)
        self.StatusLabel2 = RenderableText(Renderable(self.canvas[1], tf, ( 1,-1)),
            font=fontValue, fg=orange, text="N/A Status")
        self.VoltageLabel2 = RenderableText(Renderable(self.canvas[1], tf, ( 1, 1)),
            font=fontValue, fg=orange, text="N/A Volts")

        # Draws the background box
        pts = np.array([[-1, -1], [-1, 1], [1,1], [1,-1], [-1,-1]])
        self.canvas[1].create_line(*tf(pts).tolist(), fill=self.color, width=1, capstyle='projecting', joinstyle='miter')
        
        Valves.numOfValves += 1

    def ValveActuation(self, event):
        # Request to toggle state
        fptr = {
            HRC.IGN1_ID: [ self.canSend.ign1_off,  self.canSend.ign1_on],
            HRC.IGN2_ID: [ self.canSend.ign2_off,  self.canSend.ign2_on],
              HRC.HP_ID: [ self.canSend.hp_close,  self.canSend.hp_open],
              HRC.HV_ID: [ self.canSend.hv_close,  self.canSend.hv_open],
             HRC.FMV_ID: [self.canSend.fmv_close, self.canSend.fmv_open],
             HRC.LMV_ID: [self.canSend.lmv_close, self.canSend.lmv_open],
              HRC.LV_ID: [ self.canSend.lv_close,  self.canSend.lv_open],
             HRC.LDV_ID: [self.canSend.ldv_close, self.canSend.ldv_open],
             HRC.LDR_ID: [self.canSend.ldr_close, self.canSend.ldr_open],
              HRC.FV_ID: [ self.canSend.fv_close,  self.canSend.fv_open],
             HRC.FDV_ID: [self.canSend.fdv_close, self.canSend.fdv_open],
             HRC.FDR_ID: [self.canSend.fdr_close, self.canSend.fdr_open],
        }

        # Reverses the state-function mapping
        states = HRC.ToggleLUT[self.id]['states']
        smap = {k:v for k,v in zip(states, reversed(states))}
        target = smap[self.status]
        self.enable = states.index(target)

        print(self.nick, self.status, self.StatusStates[self.status], "Calling:", fptr[self.id][self.enable].__name__)
        fptr[self.id][self.enable]()

        self.refresh_valve()

    def refresh_valve(self):
        # if self.id in can_receive.node_state and self.status is not can_receive.node_state[self.id]:
        #     self.status = can_receive.node_state[self.id]
        if CanStatus:
            self.status = self.canReceive.States[self.id]
            # self.VoltageLabel2.update(text=self.canReceive.Sensors[self.sensorID])

            self.StatusLabel2.update(text=self.StatusStates[self.status])
            self.Button.update(img=self.imgFromState())

            self.VoltageLabel2.render()
            self.StatusLabel2.render()
            self.Button.render()

            


class States:

    # Parent is the Parent Frame
    # args is the data in the States array.
    def __init__(self, canvas, canReceive, canSend, args, boxButtonGrid, gui, prevState=None):
        # [ State Name, State ID , commandID, commandOFF , commandON, IfItsAnArmState, StateNumber]
        #["Active",              2, 1,  3,  5, False, 1],
        #self.stateName, self.stateID, self.commandID, self.commandOFF, self.commandON, \
        #    self.isArmState, self.StateNumber = args
        self.stateID, self.stateName, self.pos, self.size, self.is_a_state_command = args
        
        self.gui = gui
        self.canvas = canvas
        self.state = False
        self.prevState = prevState
        self.canSend = canSend
        self.canReceive = canReceive
        self.relXCor = 0
        self.relYCor = 0
        self.relHeight = 1
        self.relWidth = 1
        self.bgColor = "black"
        self.fontSize = ("Verdana", 10)
        self.boxButtonGrid = boxButtonGrid
        self.aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        
        if self.stateName in ["Vent", "Abort"]:
            self.aFont = tkFont.Font(family="Verdana", size=26)

        self.Button = RenderableTextButton(Renderable(self.canvas[0], boxButtonGrid, self.pos),
            font=self.aFont, fg=red, bg=black, text=self.stateName, size=self.size)
        
        self.Button.Button.bind('<Double-1>', self.onClick)
        

    def refresh(self):
        states = set([self.canReceive.rocketState[key] for key in HRC.ToggleKeys])

        if self.is_a_state_command:
            if self.stateID not in states:
                self.Button.update(fg = red)
            elif len(states) == 1:
                self.Button.update(fg = green)
            else:
                self.Button.update(fg = yellow)
        else:
            lut = {
                HRC.TANK_PRESS + 4096: self.gui.ArmTankPress,
                HRC.HIGH_PRESS + 4096: self.gui.ArmHighPress,
                HRC.IGNITE + 4096:     self.gui.ArmIgnite,
            }
            if lut[self.stateID]:
                self.Button.update(fg = green)
            else:
                self.Button.update(fg = red)
         
        self.Button.render()

    def tankPressArm(self):
        self.gui.ArmTankPress = True

    def highPressArm(self):
        self.gui.ArmHighPress = True

    def igniteArm(self):
        self.gui.ArmIgnite = True

    def tankPress(self):
        if self.gui.ArmTankPress:
            self.canSend.tank_press()
            self.gui.ArmTankPress = False

    def highPress(self):
        if self.gui.ArmHighPress:
            self.canSend.high_press()
            self.gui.ArmHighPress = False

    def ignite(self):
        if self.gui.ArmIgnite:
            self.canSend.ignite()
            self.gui.ArmIgnite = False

    def onClick(self, event):
        self.refresh()

        fptr = {
            HRC.ABORT             :self.canSend.abort,
            HRC.VENT              :self.canSend.vent,
            HRC.FIRE              :self.canSend.fire,
            HRC.TANK_PRESS        :self.tankPress,
            HRC.TANK_PRESS + 4096 :self.tankPressArm,
            HRC.HIGH_PRESS        :self.highPress,
            HRC.HIGH_PRESS + 4096 :self.highPressArm,
            HRC.STANDBY           :self.canSend.standby,
            HRC.IGNITE            :self.ignite,
            HRC.IGNITE + 4096     :self.igniteArm,
            HRC.TEST              :self.canSend.test,
        }

        fptr[self.stateID]()

    # The Main state buttons get made here
    def MainStateInstantiation(self):
        self.aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        self.relXCor = 0.0125
        self.relHeight = 7/ len(Main.States)/10
        self.relYCor = 1 - (self.relHeight * 1.15) * (len(Main.States) - self.StateNumber + 1) - .025
        print("MainStateInstantiation relYCor", self.relYCor, self.relYCor*1080)
        self.relWidth = 0.125
        self.bgColor = "black"
        self.isVentAbort = False
        # Goes to logic function when button is pressed
        self.button = Button(self.canvas[0], text=self.stateName, fg='red', bg='black', bd=5,
                             command=lambda: self.Logic(), font=20)  # , font = self.fontSize)
        self.button.place(relx=self.relXCor, rely=self.relYCor, relwidth=self.relWidth, relheight=self.relHeight)

    # The Vent and abort buttons are made here
    def VentAbortInstantiation(self):
        self.relXCor = self.stateID #self.args[1]
        self.relYCor = 0.85
        self.relHeight = .1
        self.relWidth = 1 / 10
        self.bgColor = darkGrey
        self.fontSize = ("Verdana", 26)
        self.isVentAbort = True
        self.button = Button(self.canvas[0], text=self.stateName, command=lambda: self.StateActuation(), fg='red',
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
                #GUI.StateReset()
                print("poop")
            self.state = False
        else:
            self.button.config(fg='green')
            self.state = True
        #self.canSend.state_StateActuation(self.commandID, self.state, self.commandOFF, self.commandON)


class Controller:

    def __init__(self, canvas, canReceive, canSend, args, boxEngineControllerGrid):
        #["Tank Controller HiPress", 2, False, black],
        self.name, self.id, self.isAPropTank, self.color = args
        self.canReceive = canReceive
        self.canSend = canSend
        self.canvas = canvas
        
        aFont = tkFont.Font(family="Verdana", size=10, weight="bold")
        font2 = ("Verdana", 9)

        self.Times = dict()

        buffer = [
            [HRC.SEND_LMV_OPEN,  "LOX MV\nOpen",    blue,    0, 0],
            [HRC.SEND_LMV_CLOSE, "LOX MV\nClose",   blue,    0, 1],
            [HRC.SEND_FMV_OPEN,  "Fuel MV\nOpen",   red,     1, 0],
            [HRC.SEND_FMV_CLOSE, "Fuel MV\nClose",  red,     1, 1],
            [HRC.SEND_IGNITION,  "Ignition\nTime",  green, 1/2, 2],
        ]
        
        for ID, text, color, x, y in buffer:
            pt = np.array([x, y])
            adj = TransformBox(pt, (1/3,0), (0,1/6))
            tf = boxEngineControllerGrid * adj
            
            self.Times[ID] = []
            self.Times[ID].append(RenderableText(Renderable(self.canvas[1], tf, (0, -1)),
                font=aFont, fg=color, text=text))

            fmt = lambda v: '%.4f ms'%(v*1000)
            self.Times[ID].append(RenderableText(Renderable(self.canvas[1], tf, (0, 1)),
                font=font2, fg=orange, formatter=fmt))

            # Draws the background box
            pts = np.array([[-1, -1], [-1, 1], [1,1], [1,-1], [-1,-1]])
            canvas[1].create_line(*tf(pts).tolist(), fill=color, width=1, capstyle='projecting', joinstyle='miter')

    def Refresh(self):
        for ID in HRC.TimingLUT.keys():
            #self.Times[ID][1].config(text=text)
            self.Times[ID][1].updateFromValue(self.canReceive.timingLUT_micros[ID])
            self.Times[ID][1].render()

"""
Starts Code
"""

# # This code is initializing the bus variable with the channel and bustype.
# # noinspection PyTypeChecker

CanStatus = False
try:
    import can  # /////////////////////////////////////////////////////////////////////////
    #from CanReceive import CanSend, CanReceive
    from canio_HRC import CanSend, CanReceive
    CanStatus = True

except AttributeError:
    CanStatus = False
except ModuleNotFoundError:
    pass

if CanStatus:

    #busargs = dict(channel='virtual', bustype='virtual')
    busargs = dict(channel='can0', bustype='socketcan')
    
    canReceive = CanReceive(**busargs)
    canSend = CanSend(canReceive, **busargs)

hexsha = "<githash>"
try:
    import git
    repo = git.Repo(search_parent_directories=True)
    print(repo.head.object.hexsha)
    print(repo.head.object.message)
    hexsha = repo.head.object.hexsha[:8]
except Exception as e:
    print(e)
hexsha = "Git hash: " + hexsha

import cProfile, pstats, io

GUI = Main(canReceive, canSend, hexsha)
# GUI.run()
GUIThread = Thread(target=GUI.run)
GUIThread.daemon = True

#
GUIThread.start()
if CanStatus:
    canReceive_thread = Thread(target=canReceive.run)
    canReceive_thread.daemon = True
    canReceive_thread.start()
