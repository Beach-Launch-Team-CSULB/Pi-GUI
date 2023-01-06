import math
gravity = 32.174*12 #in/s

#Optimal
LOxMdot = 0.94 #lb/s
LOxDensity = 66.83/12**3 #lb/in^3
FuelMdot = 0.75 #lb/s
FuelDensity = 52.6425/12**3 #lb/in^3

OFRatio = LOxMdot/FuelMdot
InjectionAreaLOx = 0.0281 #in^2
InjectionAreaFuel = 0.262 #in^2
delP= 55 #psi
ChamberPressure = 300 #psi

CdLOx = LOxMdot/(InjectionAreaLOx*math.sqrt(2*LOxDensity*delP*gravity))
CdFuel = FuelMdot/(InjectionAreaFuel*math.sqrt(2*FuelDensity*delP*gravity))

delPperc = delP/ChamberPressure


#Increased Chamber Pressure
ChamberPressure = 400 #psi
LOxMdot = 1.38842 #lb/s
FuelMdot = 1.10807 #lb/s

delPLOx = (LOxMdot/CdLOx/InjectionAreaLOx)**2*(1/(2*LOxDensity*gravity))
delPFuel = (FuelMdot/CdFuel/InjectionAreaFuel)**2*(1/(2*FuelDensity*gravity))


print(OFRatio)




#Bang Test Calcs
OrificeSize = .125 #in
orificeArea = OrificeSize**2*math.pi/4
TankPressure = 150 #psig
WaterDensity = 62.4/12**3 #lb/in^3
Cd = 1
mdot = Cd*orificeArea*math.sqrt(2*WaterDensity*TankPressure*gravity)

while mdot*20/WaterDensity > 213:
    Cd -= 0.01
    mdot = Cd * orificeArea * math.sqrt(2 * WaterDensity * TankPressure * gravity)

