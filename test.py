from select import select
import tkinter as tk
from tkinter import ttk
from re import A
from turtle import left
from serial import Serial
import usb.core 
import usb.util
import sys
import time 
import serial.tools.list_ports 
from threading import *
from matplotlib.widgets import Slider
from copy import deepcopy
from matplotlib.ft2font import HORIZONTAL
import matplotlib.pyplot as plt
import csv 
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button as b
from PIL import Image, ImageTk
import cv2 
import numpy as np

global ani
arduino_port = 'COM3'
ARDUINO_CONNECT = 0
SENSOR_CONNECT = 0
STOP_SCAN = 0

is_on = True
mode = "Manual"

current_pos = [0,0,0]
Move =""
Step = 10
MAX_X = 250
MAX_Y = 250
MAX_Z = 300

Measure = { 
    "X":[], 
    "Pressure":[],
    "Pulse":[]
}

Pressure_graph = [] 
Pulse_graph = []



#change the current_pos to str '0,0,0'
def change_to_str(str): 
    new_str = ""
    num = "0123456789"
    for i in range(len(str)): 
        if str[i] in num: 
            new_str+=str[i]
        if str[i] == ",":
            new_str+=","
    return new_str


def move_Up(): 
    global Move
    #global current_pos
    if current_pos[2]>=0: 
        current_pos[2]+=Step
        if current_pos[2]>=MAX_Z:
            current_pos[2] = MAX_Z

    else:
        current_pos[2] = 0
    
        
def move_Down():
    global Move
   # global current_pos
    if(current_pos[2]>=0): 
        current_pos[2]-=Step
        if current_pos[2] <0: 
            current_pos[2] = 0
    else:
        current_pos[2] = 0
    

def move_Left():
    global Move
    #global current_pos
    if(current_pos[0]>=0): 
        current_pos[0]-=Step
        if current_pos[0] < 0: 
            current_pos[0] = 0
    else:
        current_pos[0] = 0
    

def move_Right():
    global Move
   # global current_pos
    if current_pos[0]>=0: 
        current_pos[0]+=Step
        if current_pos[0]>=MAX_X:
            current_pos[0] = MAX_X

    else:
        current_pos[0] = 0


def arduino_move(): 
    global arduino_port
    arduino = Serial(port=arduino_port, baudrate= 115200, timeout = .1)

    while True: 
        global old_pos
        global current_pos
        if old_pos != current_pos:
            num = change_to_str(str(current_pos))
            num = "("+ num +")"
            old_pos = deepcopy(current_pos)
            print(num)
            arduino.write(num.encode())
            #time.sleep(0.5)
            # data = arduino.readline()
            # print(data)

    
def start_scan(val):
    print('Scan Started')

    Measure["X"]=[]
    Measure["Pressure"] =[] 
    Measure["Pulse"] = []
    Pressure_graph = [] 
    Pulse_graph = []

    #Set stop flag to false
    global STOP_SCAN
    STOP_SCAN = 0
    plt.cla()
    #Make a thread for the sensor to read
    global SCAN_T 
    SCAN_T = Thread(target = sensor_read, daemon = True)
    SCAN_T.start()

    plot_sensor_data()

def stop_scan(val): 
    global ani
    global plt
    #Set stop flag to true
    global STOP_SCAN
    STOP_SCAN = 1

    ani.pause()
    plt.close()

    figure = plt.Figure(figsize = (6,5), dpi = 100)
    ax1 = figure.add_subplot(111) 
    bar1 = FigureCanvasTkAgg(figure, right_frame)
    bar1.get_tk_widget().place(x = 25, y = 20)

    x = Measure["X"]
    Pressure = Measure["Pressure"] 
    Pulse = Measure["Pulse"]

    ax1.plot(x, Pulse, label ='Pulse')
    ax1.plot(x, Pressure, label ='Pressure')
    bar1.draw()
    
    # plt.savefig('test1.png')
    # show_figure()
    # plt.close()



def sensor_read():
    global sensor_port
    global STOP_SCAN
    global READING
    sensor = Serial(port= 'COM5', 
    baudrate = 256000, 
    parity = serial.PARITY_NONE,
    bytesize = 8, stopbits=serial.STOPBITS_ONE)
    sensor.write([0xF0, 0x2F, 0x01, 0x32])
    # sensor.write([0xF0, 0x2F, 0x01, 0x34]) # Set the pressure value to zero

    #SENSOR DATA- first 4 values stay the same 
    #[0xF0,0x1F,0x06,0x32,JYL,JYM,MBL,MBH,CHECK] 
    #JYL - Low byte of pressure 
    #JYH - High byte of pressure 
    #MBL - Low byte of pulse wave 
    #MBH - High byte of pulse wave 
    #CHECK - Low byte of (JYL+JYH+MBL+MBH)

    n =[]
    X = 0 
    Pressure = 0 
    Pulse = 0
    while True: 
        serialString = sensor.read()
        temp = int.from_bytes(serialString, byteorder=sys.byteorder)
        n.append(temp)
        if len(n) == 9:

            Pressure = n[5]<<8|n[4]
            Pulse = int(((n[7]<<8)|n[6])/25)
            Measure["X"].append(X) 
            Measure["Pressure"].append(Pressure)
            Measure["Pulse"].append(Pulse)

            if len(Pressure_graph) < 100: 
                Pressure_graph.append(Pressure) 
            else: 
                Pressure_graph[0:99] = Pressure_graph[1:100] 
                Pressure_graph[99] = Pressure

            if len(Pulse_graph) < 100: 
                Pulse_graph.append(Pulse) 
            else: 
                Pulse_graph[0:99] = Pulse_graph[1:100] 
                Pulse_graph[99] = Pulse
            X+=1
            n=[]        
        if STOP_SCAN:
            break

    # while True: 
    #     serialString = sensor.readline() 
    #     print(int(serialString))
    #     if STOP_SCAN: 
    #         break 

    sensor.write([0xF0, 0x2F, 0x01, 0x33])
    print('Scan Ended')

def plot_sensor_data(): 

    global plt
    ax = plt.subplot(111)
    def animate(i):
        x = Measure["X"]
        Pressure = Measure["Pressure"] 
        Pulse = Measure["Pulse"]

        ax.cla()

        ax.plot(x, Pulse, label ='Pulse')
        ax.plot(x, Pressure, label ='Pressure')

        ax.legend(loc = "upper left")

    # Position of the button 
    axcut1 = plt.axes([0.9, 0.00001, 0.1, 0.1])
    bcut1 = b(axcut1, 'Stop')
    bcut1.on_clicked(stop_scan)

    global ani
    ani = FuncAnimation(plt.gcf(),animate, interval=1)
    plt.show()



#always check if sensor is connected
def connect_sensor():
    global SENSOR_CONNECT 
    global ARDUINO_CONNECT 
    global sensor_port 
    global arduino_port
    while True: 
        SENSOR_CONNECT = 0
        ARDUINO_CONNECT = 0
        ports = serial.tools.list_ports.comports()
        for p in ports: 
            #print(p.vid, p.pid)
            # VID = str(p.hwid)[12:16]
            # PID = str(p.hwid)[17:21]
            # if VID == "10C4" and PID == "EA60": #sensor PID and VID
            #     SENSOR_CONNECT = 1
            # if VID == "0403" and PID == "6001": #arduino PID and VID
            #     ARDUINO_CONNECT = 1

            VID = p.vid 
            PID = p.pid 

            if VID == 4292 and PID == 60000: #sensor PID and VID
                SENSOR_CONNECT = 1
                sensor_port = p[0] #get the COM 
            if VID == 1027 and PID == 24577: #arduino PID and VID
                ARDUINO_CONNECT = 1
                arduino_port = p[0] #get the COM 

        #checks if sensor is connected 
        if SENSOR_CONNECT: 
            Sensor_Connect_Status.config(text = "Connected")
            Scan_B["state"] = "normal" 
        else: 
            Sensor_Connect_Status.config(text = "Disconnected")
            Scan_B["state"] = "disabled" 

        #if arduino is not connected we disable the movement buttons
        if ARDUINO_CONNECT: 
            Arduino_Connect_Status.config(text = "Connected")
            Up["state"] = "normal"
            Down["state"] = "normal"
            Left["state"] = "normal"
            Right["state"] = "normal"
        else: 
            Arduino_Connect_Status.config(text = "Disconnected")
            Up["state"] = "disabled"
            Down["state"] = "disabled"
            Left["state"] = "disabled"
            Right["state"] = "disabled"

# def show_figure():
#     load= Image.open("test1.png")
#     render = ImageTk.PhotoImage(load)
#     img.configure(image = render)
#     img.image = render

def show_frames():
   global is_on
   t = int(is_on)
   retval, frame = cap.read()
   left = np.split(frame, 2,axis = 1)
   cv2image= cv2.cvtColor(left[t],cv2.COLOR_BGR2RGB)
   img2 = Image.fromarray(cv2image)
   # Convert image to PhotoImage
   imgtk = ImageTk.PhotoImage(image = img2)
   Cam_View.imgtk = imgtk
   Cam_View.configure(image=imgtk)
   # Repeat after an interval to capture continiously
   Cam_View.after(20, show_frames)

def switch_camera(): 
    global is_on

    if is_on: 
        is_on = False
    else: 
        is_on = True

def upload_scan(): 
    nameinfo.delete('1.0', tk.END)
    descriptioninfo.delete('1.0', tk.END)
    print("Scan uploaded")

def scale(i):
    global g
    g.set(int(scale.get()))
    Step_Value.config(text=str(int(scale.get())))
    
root = tk.Tk()
root.title('Automated Pulse Sensing Tool')

window_height = 700
window_width = 1000

g = tk.IntVar()
g.set(50)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

style = ttk.Style(root)
root.tk.call('source', 'GUI_Design/azure dark.tcl')
style.theme_use('azure')


frame1 = ttk.LabelFrame(root, text="Camera", width=320, height=240)
frame1.place(x=20, y=12)
black_border = tk.Frame(frame1, width = 305, height = 190,bg = "white")
black_border.place(x=5, y=5)
Cam_View = tk.Label(frame1, width = 290, height = 175)
Cam_View.place(x=10, y = 10)
cap = cv2.VideoCapture(0)
show_frames()
switch = ttk.Checkbutton(frame1, text='Switch Camera', style='Switch',command = switch_camera)
switch.place(x=90, y=200)
is_on = False


frame2 = ttk.LabelFrame(root, text='Options', width=320, height=320)
frame2.place(x=20, y=270)

Mode_label = tk.Label(frame2, text='Mode') 
Mode_label.place(x=40, y = 40)
Manual = tk.Radiobutton(frame2, text="Manual", variable = mode, indicatoron = False, value = "Manual", width = 10, selectcolor="#007FFF")
Manual.invoke()
Automatic = tk.Radiobutton(frame2, text="Automatic", variable = mode, indicatoron = False, value = "Automatic", width = 10,  selectcolor="#007FFF")
Manual.place(x = 120, y = 40)
Automatic.place(x = 200, y = 40)

Move_label = tk.Label(frame2, text='Movement') 
Move_label.place(x=20, y = 110)
Up = tk.Button(frame2, text = "^", command = move_Up) 
Down = tk.Button(frame2, text = "v", command = move_Down)
Left = tk.Button(frame2, text = "<", command = move_Left)
Right = tk.Button(frame2, text = ">", command = move_Right)
ix = 20
iy = 20
Up.place(x = 170+ix, y = 60+iy)
Left.place(x = 140+ix, y = 90+iy)
Right.place(x= 200+ix, y = 90+iy)
Down.place(x = 170+ix, y = 120+iy)


Step_Label = tk.Label(frame2, text = "Steps")
Step_Label.place(x= 50, y = 180)

scale = ttk.Scale(frame2, from_=0, to=100, variable=g, command=scale)
scale.place(x=150, y=180)

Step_Value  = tk.Label(frame2, text= str(int(g.get())))
Step_Value.place(x = 250, y = 180)



Sensor_Connect_Label = tk.Label(frame2, text = "Pulse Sensor: ")
Arduino_Connect_Label = tk.Label(frame2, text = "Motors: ")
Sensor_Connect_Status = tk.Label(frame2, text = "Not Connected")
Arduino_Connect_Status = tk.Label(frame2, text = "Not Connected")
Sensor_Connect_Label.place(x = 10, y = 230)
Arduino_Connect_Label.place(x = 10, y = 250)
Sensor_Connect_Status.place(x = 100, y = 230)
Arduino_Connect_Status.place(x = 100, y = 250)

Scan_B = ttk.Button(frame2, text='Scan', style='Accentbutton', command = lambda: start_scan(1))
Scan_B.place(x=185, y=235)







right_frame = tk.Frame(root, width = 650, height = 700, bg = "grey")
right_frame.place(x = 350, y = 0)

# load = Image.open("test1.png")
# render = ImageTk.PhotoImage(load)
# img =tk.Label(right_frame, image = render)
# img.place(x = 4, y = 5)

figure = plt.Figure(figsize = (6,5), dpi = 100)
ax1 = figure.add_subplot(111) 
bar1 = FigureCanvasTkAgg(figure, right_frame)
bar1.get_tk_widget().place(x = 25, y = 20)

x = Measure["X"]
Pressure = Measure["Pressure"] 
Pulse = Measure["Pulse"]

ax1.plot(x, Pulse, label ='Pulse')
ax1.plot(x, Pressure, label ='Pressure')


Scan_Label = tk.Label(right_frame, text = "Scan Information",fg = "black", bg = "grey", font = ("Arial", 15) )
Scan_Label.place(x = 25, y = 530)

Name_Label = tk.Label(right_frame, text = "Name",fg = "black", bg = "grey", font = ("Arial", 13) )
Name_Label.place(x = 25, y = 555)

nameinfo = tk.Text(right_frame, height = 1,width = 78, bg = "white", fg = "black", insertbackground="black")
nameinfo.place(x = 150, y = 560)

Description_Label = tk.Label(right_frame, text = "Description",fg = "black", bg = "grey", font = ("Arial", 13) )
Description_Label.place(x = 25, y = 585)

descriptioninfo = tk.Text(right_frame, height = 6,width = 78, bg = "white", fg = "black", insertbackground="black")
descriptioninfo.place(x =150, y = 590)

Upload = ttk.Button(right_frame, text = "Upload", style="Accentbutton",command = upload_scan)
Upload.place(x = 30, y = 650)




def main(): 
    # t1 = Thread(target = arduino_move, daemon=True)
    # t1.start()
    t2 = Thread(target = connect_sensor, daemon = True)
    t2.start() 

    root.mainloop()

if __name__ == "__main__": 
    main()