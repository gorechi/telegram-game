import matplotlib.pyplot as plt
author__ = 'GHajba'

x_axis = [x for x in range(-20,21)]
y_axis = [x**0.2 for x in x_axis]

plt.plot(x_axis, y_axis)
plt.show()
