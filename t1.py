# from matplotlib import pyplot as plt 
# plt.rcParams['backend'] = 'TkAgg' 
# plt.rcParams["figure.figsize"] = [7.50, 3.50] 
# plt.rcParams["figure.autolayout"] = True 
# # Function to print mouse click event coordinates 
# def onclick(event): 
#     print([event.xdata, event.ydata]) 
#     # Create a figure and a set of subplots 
# fig, ax = plt.subplots() 
# # Plot a line in the range of 10 
# ax.plot(range(10)) 
# # Bind the button_press_event with the onclick() method 
# fig.canvas.mpl_connect('button_press_event', onclick)
# # Display the plot 
# plt.show()

from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(0.0, 1.0, 0.01)
s = np.sin(2 * np.pi * t)
fig, ax = plt.subplots()
ax.plot(t, s)


def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y
    if event.inaxes:
        ax = event.inaxes  # the axes instance
        print('data coords %f %f' % (event.xdata, event.ydata))


def on_click(event):
    if event.button is MouseButton.LEFT:
        print('disconnecting callback')
        plt.disconnect(binding_id)


binding_id = plt.connect('motion_notify_event', on_move)
plt.connect('button_press_event', on_click)

plt.show()