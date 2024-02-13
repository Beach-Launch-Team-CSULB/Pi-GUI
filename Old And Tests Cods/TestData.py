import csv
import matplotlib.pyplot as plt

data = []
valveStatus1 = []
valveStatus11 = []
valveStatus12 = []
valveStatus0 = []
raw = []

with open('CoolTerm_Capture_2022-07-08_16-48-44.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        line_count +=1
        if line_count < 395200:
            continue
        if line_count > 398200:
            continue
        if row[1] is None or row[1] == " ":
            continue
        data.append(round(float(row[1]))-150)
        raw.append(round(float(row[0])))

        if int(row[3]) == 0:
            valveStatus0.append(round(float(row[1]))-150)
            valveStatus1.append(0)
            valveStatus11.append(0)
            valveStatus12.append(0)
        elif int(row[3]) == 1:
            valveStatus1.append(round(float(row[1]))-150)
            valveStatus12.append(0)
            valveStatus11.append(0)
            valveStatus0.append(0)

        elif int(row[3]) == 11:
            valveStatus11.append(round(float(row[1]))-150)
            valveStatus0.append(0)
            valveStatus1.append(0)
            valveStatus12.append(0)
        elif int(row[3]) == 12:
            valveStatus12.append(round(float(row[1]))-150)
            valveStatus1.append(0)
            valveStatus11.append(0)
            valveStatus0.append(0)
        else:
            valveStatus12.append(0)
            valveStatus1.append(0)
            valveStatus11.append(0)
            valveStatus0.append(0)







plt.plot(data,color="black")
plt.plot(valveStatus0,color="red")
plt.plot(valveStatus1,color="black")
plt.plot(valveStatus11,color="green")
plt.plot(valveStatus12,color="blue")
plt.plot(raw,color="orange")

plt.legend(["closed", "Open", "Forced Close", "Forced Open"], loc=0)

plt.show()
