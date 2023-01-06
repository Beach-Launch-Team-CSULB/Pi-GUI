import math
import matplotlib.pyplot as plt

" Pressurant Properties"
N2GasConstant = 296.8  # J/kg-k
ATPTemp = 288.15  # K
Gamma = 1.4

" Water Properties "
WaterDensity = 999  # kg/m3

" Propellant Tank "
OptimalTankPress = 150 * 6895  # Pa
TankPress = OptimalTankPress
TankVolume = 0.004  # m^3
PropVolume = 0.0035  # m^3
UllageVolume = TankVolume - PropVolume  # m^3
ullageGasMass = OptimalTankPress / N2GasConstant / ATPTemp * UllageVolume  # kg
PropDensity = WaterDensity

" Pressurant Tank "
COPVPressure = 2000 * 6895  # psi
COPVVolume = 5  # m^3
COPVGasMass = COPVPressure / N2GasConstant / ATPTemp * COPVVolume  # kg

" Solenoid Valve "
InFlowDiameter = 0.02 * 0.0254  # m
InFlowCdA = InFlowDiameter ** 2 / 4 * math.pi  # m^2
valveOpen = False  # Is the Valve Open

" Out Flow Orifice"
Cd = 0.6  # Discharge Coefficient of the out flow orifice
OrificeDiameter = 0.125 * 0.0254  # m
OrificeArea = OrificeDiameter ** 2 / 4 * math.pi  # m2

" PID "
Kp = -15
Kd = 0
Ki = 0
SizeDerivativeArray = 3
SizeIntegralArray = 30
pastNArr = [0] * SizeDerivativeArray
pastNDpArr = [0] * SizeIntegralArray
Integral = 0

" Data Arrays "
TankPressArray = []
PIDSumArray = []
derivativeArray = []
ErrorArray = []
IntegralArray = []

" Simulation Variables "
Time = 0
TimeDelta = 0.01
i = 0
prevPressure = TankPress


def CurrTankPress(UllageGasMass, UllageVolume, Temp):
    gasDensity = UllageGasMass / UllageVolume
    Pressure = gasDensity * N2GasConstant * Temp
    return Pressure


def ChokedMassFlow(UpstreamPressure):
    massFlow = UpstreamPressure * InFlowCdA * (
            Gamma / N2GasConstant / ATPTemp * (2 / (Gamma + 1)) ** ((Gamma + 1) / (Gamma - 1))) ** (1 / 2)
    return massFlow


def compressibleMassFlow(UpstreamPressure):
    mDot = Cd * OrificeArea * math.sqrt(2 * UpstreamPressure * WaterDensity)
    return mDot

# CurrPressure = CurrTankPress(ullageGasMass, UllageVolume, ATPTemp)  # Tank Pressure
# while (CurrPressure - prevPressure)/TimeDelta/6895 < 99:
#     InFlowDiameter += 0.00000001
#     InFlowCdA = InFlowDiameter ** 2 / 4 * math.pi  # m^2
#     print((InFlowCdA / math.pi * 4) ** (1 / 2) / 0.0254)
#
#     ullageGasMass2 = ullageGasMass + ChokedMassFlow(COPVPressure) * TimeDelta
#     CurrPressure = CurrTankPress(ullageGasMass2, UllageVolume, ATPTemp)  # Tank Pressure
# print((InFlowCdA/math.pi*4)**(1/2)/0.0254)
while PropVolume > 0:  # While there is still propellant in the tank

    CurrPressure = CurrTankPress(ullageGasMass, UllageVolume, ATPTemp)  # Tank Pressure

    " PID Stuff"
    Error = (OptimalTankPress - CurrPressure) / 6895
    Derivative = (CurrPressure - pastNArr[i % SizeDerivativeArray]) / 6895 / TimeDelta / SizeDerivativeArray
    pastNArr[i % SizeDerivativeArray] = CurrPressure
    pastNDpArr[i % SizeIntegralArray] = Error
    Integral = 0
    for Dp in pastNDpArr:
        Integral += Dp * TimeDelta
    if i < SizeIntegralArray:
        Integral = Integral / (i + 1)
    else:
        Integral = Integral / SizeIntegralArray
    pidSum = Kp * Error + Kd * Derivative + Ki * Integral

    if pidSum > 1:
        valveOpen = False
    elif pidSum < -1:
        valveOpen = True

    if valveOpen:
        ullageGasMass += ChokedMassFlow(COPVPressure) * TimeDelta
        COPVGasMass -= ChokedMassFlow(COPVPressure) * TimeDelta
        COPVPressure = CurrTankPress(COPVGasMass, COPVVolume, ATPTemp)
    propQDot = compressibleMassFlow(CurrPressure)/PropDensity
    UllageVolume += propQDot * TimeDelta
    PropVolume -= propQDot*TimeDelta
    CurrPressure = CurrTankPress(ullageGasMass, UllageVolume, ATPTemp)
    print((CurrPressure - prevPressure)/TimeDelta/6895)
    prevPressure = CurrPressure

    TankPressArray.append(CurrPressure/6895)
    PIDSumArray.append(pidSum)
    i += 1
    Time += TimeDelta

plt.plot(TankPressArray,color="black")
plt.plot(PIDSumArray,color="red")

plt.show()



