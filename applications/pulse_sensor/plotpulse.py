import matplotlib.pyplot as plt

import csv

f = open("pulse.csv")

next(f)

x = []; y = []

for row in csv.reader(f):
     x.append(row[0])
     y.append(row[1])

f.close()

plt.plot(x, y)
plt.show()

