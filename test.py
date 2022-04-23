from email import message
from select import select
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from re import A
from turtle import left, right
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
from matplotlib.backend_bases import MouseButton
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
old_pos =[0,0,0]
Move =""
Step = 50
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

global ax, ax2

global start,end



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
            time.sleep(0.5)
            # data = arduino.readline()
            # print(data)

    
def start_scan(val):
    global Pressure_graph
    global Pulse_graph
    global STOP_SCAN

    print('Scan Started')

    Measure["X"]=[]
    Measure["Pressure"] =[] 
    Measure["Pulse"] = []
    Pressure_graph = [] 
    Pulse_graph = []

    #Set stop flag to false
    STOP_SCAN = 0

    #Make a thread for the sensor to read
    SCAN_T = Thread(target = sensor_read, daemon = True)
    SCAN_T.start()

    plot_sensor_data()

def stop_scan(val): 
    global ani
    global plt
    global Pressure_graph
    global Pulse_graph

    Pressure_graph = [] 
    Pulse_graph = []

    #Set stop flag to true
    global STOP_SCAN
    STOP_SCAN = 1
    plt.close()

    figure = plt.Figure(figsize = (6,5), dpi = 100)
    ax2 = figure.add_subplot(111) 
    bar1 = FigureCanvasTkAgg(figure, right_frame)
    bar1.get_tk_widget().place(x = 25, y = 20)

    x = Measure["X"]
    Pressure = Measure["Pressure"] 
    Pulse = Measure["Pulse"]

    ax2.plot(x, Pulse, label ='Pulse')
    ax2.plot(x, Pressure, label ='Pressure')
    bar1.draw()
    
    # plt.savefig('test1.png')
    # show_figure()
    # plt.close()



def sensor_read():
    global sensor_port
    global STOP_SCAN
    global Pressure_graph
    global Pulse_graph

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
    displaynumber  = 1000
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

            
            if len(Pressure_graph) < displaynumber: 
                Pressure_graph.append(Pressure) 
            else: 
                Pressure_graph[0:displaynumber-1] = Pressure_graph[1:displaynumber] 
                Pressure_graph[displaynumber-1] = Pressure

            if len(Pulse_graph) < displaynumber: 
                Pulse_graph.append(Pulse) 
            else: 
                Pulse_graph[0:displaynumber-1] = Pulse_graph[1:displaynumber] 
                Pulse_graph[displaynumber-1] = Pulse
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
    global ax
    ax = plt.subplot(111)
    def animate(i):
        # x = Measure["X"]
        # Pressure = Measure["Pressure"] 
        # Pulse = Measure["Pulse"]

        
        x = np.arange(0, len(Pressure_graph))
        # Pressure = Pressure_graph 
        # Pulse = Pulse_graph

        Pressure = deepcopy(Pressure_graph)
        Pulse = deepcopy(Pulse_graph)

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
    global start, end
    if len(nameinfo.get('1.0',tk.END)) == 1 or len(descriptioninfo.get('1.0',tk.END)) == 1:
        messagebox.showinfo("Error", "Please Enter Name and Description for Scan Before Uploading")
    else: 
        Name = nameinfo.get('1.0', 'end-1c')
        Description = descriptioninfo.get('1.0', 'end-1c')

        file = open(Name+".txt", "a")
        file.write("Name: "+ Name+"\n\n")
        file.write("Description: " + Description+"\n\n")
        file.write("Pulse Data Set: \n") 
        for i in range(start,end): 
            file.write(str(Measure["X"][i])+" : "+ str(Measure["Pulse"][i])+"\n")
        file.write("\n\n")

        file.write("Pressure Data Set: \n") 
        for i in range(start,end): 
            file.write(str(Measure["X"][i])+" : "+str(Measure["Pressure"][i])+"\n")
        
        file.close()

        nameinfo.delete('1.0', tk.END)
        descriptioninfo.delete('1.0', tk.END)
        print("Scan uploaded")

def scale(i):
    global g
    global Step
    g.set(int(scale.get()))
    Step = int(g.get())
    Step_Value.config(text=str(int(scale.get())))

def finish_edit_scan(val):
    global start,end
    print("Start: ", start) 
    print("End: ", end)

    global plt
    plt.close()

    figure = plt.Figure(figsize = (6,5), dpi = 100)
    ax2 = figure.add_subplot(111) 
    bar1 = FigureCanvasTkAgg(figure, right_frame)
    bar1.get_tk_widget().place(x = 25, y = 20)

    x = Measure["X"][start:end]
    Pressure = Measure["Pressure"][start:end]
    Pulse = Measure["Pulse"][start:end]

    ax2.plot(x, Pulse, label ='Pulse')
    ax2.plot(x, Pressure, label ='Pressure')
    bar1.draw()


def open_scan():
    Plot, Axis = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    global start, end
    

    x = Measure["X"]
    Pulse = Measure["Pulse"]
    global line2
    line1, = Axis.plot(x, Pulse)

    start = 0 
    end = len(Measure["X"]) 

    global removeflag
    global doubleclick
    doubleclick = 0 
    removeflag = 0
    def onclick(event):
        global start
        global end
        x = event.xdata 
        y = event.ydata
        global line2
        global removeflag
        global doubleclick
    
        if event.inaxes:
            if y>1:
                if event.button is MouseButton.LEFT:
                    start = int(x)
                    end = 0
                    if removeflag:
                        line2.remove()
                        Plot.canvas.draw_idle()
                        removeflag= 0

                    if not doubleclick:
                        line2 = Axis.axvspan(start, start+1, color='red', alpha=0.5)
                        Plot.canvas.draw_idle()
                        doubleclick = 1
                    else: 
                        line2.remove()
                        Plot.canvas.draw_idle()
                        line2 = Axis.axvspan(start, start+1, color='red', alpha=0.5)
                        Plot.canvas.draw_idle()


                elif event.button is MouseButton.RIGHT:
                    end = int(x)
                    line2.remove()
                    Plot.canvas.draw_idle()
                    doubleclick = 0

                if start!=0 and end!=0:
                    line2 = Axis.axvspan(start, end, color='red', alpha=0.5)
                    Plot.canvas.draw_idle()
                    removeflag = 1

    plt.connect('button_press_event', onclick)
    

    
    slider_color = 'White'
    axis_position = plt.axes([0.2, 0.1, 0.65, 0.03],
                            facecolor = slider_color)
    slider_position = Slider(axis_position,
                            'Pos', 1, len(x)-1000)
    
    

    # update() function to change the graph when the
    # slider is in use
    def update(val):
        pos = slider_position.val
        index = int(pos)
        
        if(index+1000<len(Pulse)):
            max = 0 
            min = 1000
            for i in range(index, index+1000): 
                if Measure["Pulse"][i] >max: 
                    max = Measure["Pulse"][i]
                if Measure["Pulse"][i] < min: 
                    min = Measure["Pulse"][i]
        
            Axis.axis([pos, pos+1000, min-10, max+10])
            Plot.canvas.draw_idle()
        else:
            max = 0 
            min = 1000
            for i in range(index, len(x)): 
                if Measure["Pulse"][i] >max: 
                    max = Measure["Pulse"][i]
                if Measure["Pulse"][i] < min: 
                    min = Measure["Pulse"][i]
            
            Axis.axis([pos, pos+1000, min-10, max+10])
            Plot.canvas.draw_idle()

    axcut1 = plt.axes([0.9, 0.00001, 0.1, 0.1])
    bcut1 = b(axcut1, 'Finish')
    bcut1.on_clicked(finish_edit_scan)

    slider_position.on_changed(update)
    plt.show()




root = tk.Tk()
root.title('Automated Pulse Sensing Tool')

window_height = 700
window_width = 1000

g = tk.IntVar()
g.set(50)
Step = int(g.get())

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
scale.place(x=150, y=183)

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

# figure_frame = tk.Frame(right_frame, height = 500, width = 600)
# figure_frame.place(x = 25, y =20)
# figure_frame.bind("<Button-1>", open_scan)

# load = Image.open("test1.png")
# render = ImageTk.PhotoImage(load)
# img =tk.Label(right_frame, image = render)
# img.place(x = 4, y = 5)

figure = plt.Figure(figsize = (6,5), dpi = 100)
ax2 = figure.add_subplot(111) 
bar1 = FigureCanvasTkAgg(figure, right_frame)
bar1.get_tk_widget().place(x = 25, y = 20)

x = Measure["X"]
Pressure = Measure["Pressure"] 
Pulse = Measure["Pulse"]

ax2.plot(x, Pulse, label ='Pulse')
ax2.plot(x, Pressure, label ='Pressure')

OpenGraph = ttk.Button(right_frame, text = "Open Graph", style="Accentbutton",command = open_scan)
OpenGraph.place(x = 500, y = 530)


Scan_Label = tk.Label(right_frame, text = "Scan Information",fg = "black", bg = "grey", font = ("Arial", 15) )
Scan_Label.place(x = 25, y = 530)

Name_Label = tk.Label(right_frame, text = "Name",fg = "black", bg = "grey", font = ("Arial", 13) )
Name_Label.place(x = 130, y = 565)

nameinfo = tk.Text(right_frame, height = 1,width = 73, bg = "white", fg = "black", insertbackground="black")
nameinfo.place(x = 180, y = 570)

Description_Label = tk.Label(right_frame, text = "Description",fg = "black", bg = "grey", font = ("Arial", 13) )
Description_Label.place(x = 88, y = 595)

descriptioninfo = tk.Text(right_frame, height = 6,width = 73, bg = "white", fg = "black", insertbackground="black")
descriptioninfo.place(x =180, y = 595)

Upload = ttk.Button(right_frame, text = "Upload", style="Accentbutton",command = upload_scan)
Upload.place(x = 30, y = 660)




def main(): 
    # t1 = Thread(target = arduino_move, daemon=True)
    # t1.start()
    t2 = Thread(target = connect_sensor, daemon = True)
    t2.start() 

    root.mainloop()

if __name__ == "__main__": 
    main()