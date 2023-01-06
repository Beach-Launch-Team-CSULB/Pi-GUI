import matplotlib.pyplot as plt
import math

PressureNeeded = 50
PressureCurr = 10
PressureCurr1 = 10
sinePressure = 10

Tolerance = 1
ProportionalTerm = 0.005

PressureArr = []
FlowRateArr = []
Error = PressureNeeded - PressureCurr
ErrorStart = PressureNeeded - PressureCurr
Error1 = PressureNeeded - PressureCurr1

holeArea = 3.1415*(1/8)**2/4


while abs(Error) > Tolerance:
    PressureArr.append(PressureCurr)
    FlowRateArr.append(PressureCurr1)
    PercChange = (PressureNeeded-PressureCurr)*0.005
    PressureCurr += Error*(math.sin(Error/ErrorStart*math.pi)+1)*ProportionalTerm
    PressureCurr1 += Error1*PercChange
    Error = PressureNeeded - PressureCurr
    Error1 = PressureNeeded - PressureCurr1

    
plt.plot(PressureArr)
plt.plot(FlowRateArr)

#plt.ylabel('flowrate')
plt.show()
