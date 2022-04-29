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
import threading
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
import mediapipe as mp
import time
from slope import getValue, find_m, getValueWithM
from math import dist


global ani
arduino_port = 'COM3'
ARDUINO_CONNECT = 0
SENSOR_CONNECT = 0
STOP_SCAN = 0

is_on = True
mode = "Manual"

current_pos = np.array([0,0,0])
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


def move_Up():
    global current_pos
    if current_pos[2]+Step >=MAX_Z: 
        current_pos[2] = MAX_Z
    else:
        current_pos[2] +=Step
    write() 
        
def move_Down():
    global current_pos
    if current_pos[2]-Step <= 0:
        current_pos[2] = 0
    else: 
        current_pos[2] -= Step
    write()

def move_Left():
    global current_pos
    if current_pos[0]-Step <= 0:
        current_pos[0] = 0
    else: 
        current_pos[0] -= Step
    write()
    

def move_Right():
    global current_pos
    if current_pos[0]+Step >=MAX_X: 
        current_pos[0] = MAX_X
    else:
        current_pos[0] +=Step
    write()


def write():
    global current_pos
    num = str(current_pos[0])+","+str(current_pos[1])+","+str(current_pos[2])
    num = "("+ num +")"
    print(num)
    arduino.write(num.encode())


    
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
    SCAN_T = threading.Thread(target = sensor_read, daemon = True)
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

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils
handLmsStyle = mpDraw.DrawingSpec(color=(150, 0, 150), thickness=3)
handConStyle = mpDraw.DrawingSpec(color=(200, 200, 0), thickness=5)
preTargetStyle = (0, 0, 255)
TargetStyle = (0, 255, 0)
pTime = 0
cTime = 0
infinity = 100000 

def show_frames():
    global is_on
    t = int(is_on)
    retval, frame = cap.read()
    img = np.split(frame, 2,axis = 1)
    img = img[t]

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(imgRGB)
    
    imgHeight = img.shape[0]
    imgWidth = img.shape[1]
    total = 0.0

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#二值化
    ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks: 
            originx = 0 #腕關節
            originy = 0
            bigFinger4_X = 0 #大拇指點4
            bigFinger4_Y = 0
            bigFinger3_X = 0 #大拇指點3
            bigFinger3_Y = 0
            secFinger5_X = 0 #二拇指點5
            secFinger5_Y = 0
            thirdFinger9_X = 0 #三拇指點9
            thirdFinger9_Y = 0
            fourthFinger13_X = 0 #四拇指點13
            fourthFinger13_Y = 0
            fifthFinger17_X = 0 #五拇指點17
            fifthFinger17_Y = 0
            #xx = 0
            #yy = 0
            for i, lm in enumerate(handLms.landmark):
                xPos = round(lm.x * imgWidth)
                yPos = round(lm.y * imgHeight)
                if i == 0:
                    originx = xPos
                    originy = yPos
                #if i == 2:
                    #xx = xPos
                    #yy = yPos
                if i == 3:
                    bigFinger3_X = xPos
                    bigFinger3_Y = yPos
                    #if (xx-xPos) != 0:
                        #print("big finger:", getValueWithM(xPos, yPos, -1* (yy-yPos)/(xx-xPos),img))
                    #else:
                        #print("big finger:", getValueWithM(xPos, yPos, infinity,img))
                if i == 4:
                    bigFinger4_X = xPos
                    bigFinger4_Y = yPos
                if i == 5:
                    secFinger5_X = xPos #二拇指點5
                    secFinger5_Y = yPos
                if i == 6:
                    if (secFinger5_X-xPos) != 0:
                        total += getValueWithM(xPos, yPos, -1* (secFinger5_Y-yPos)/(secFinger5_X-xPos),img)
                    else:
                        total += getValueWithM(xPos, yPos, infinity,img)
                    print("key: ", i, ", total: ", total)
                if i == 9:
                    thirdFinger9_X = xPos #三拇指點9
                    thirdFinger9_Y = yPos
                if i == 10:
                    if (thirdFinger9_X-xPos) != 0:
                        total += getValueWithM(xPos, yPos, -1* (thirdFinger9_Y-yPos)/(thirdFinger9_X-xPos),img)
                    else:
                        total += getValueWithM(xPos, yPos, infinity,img)
                    print("key: ", i, ", total: ", total)
                if i == 13:
                    fourthFinger13_X = xPos #四拇指點13
                    fourthFinger13_Y = yPos
                if i == 14:
                    if (fourthFinger13_X-xPos) != 0:
                        total += getValueWithM(xPos, yPos, -1* (fourthFinger13_Y-yPos)/(fourthFinger13_X-xPos),img)
                    else:
                        total += getValueWithM(xPos, yPos, infinity,img)
                    print("key: ", i, ", total: ", total)
                if i == 17:
                    fifthFinger17_X = xPos #五拇指點17
                    fifthFinger17_Y = yPos
                if i == 18:
                    if (fifthFinger17_X-xPos) != 0:
                        total += getValueWithM(xPos, yPos, -1* (fifthFinger17_Y-yPos)/(fifthFinger17_X-xPos),img)
                    else:
                        total += getValueWithM(xPos, yPos, infinity,img)
                    print("key: ", i, ", total: ", total)                     
            
           
        
            if (originx!=0 and originy!=0 and bigFinger4_X!=0 and bigFinger4_Y!=0 
            and bigFinger3_X!=0 and bigFinger3_Y!=0 and secFinger5_X!=0 and secFinger5_Y!=0
            and thirdFinger9_X!=0 and thirdFinger9_Y!=0 and fourthFinger13_X!=0 and fourthFinger13_Y!=0 
            and fifthFinger17_X!=0 and fifthFinger17_Y!=0):
                # + round(img.shape[0]/20)
                total = total * (20 / 19)
                m = find_m(originx, originy+ round(img.shape[0]/6) , img)# 6是參數, 視實際拍攝圖片決定
                if m:
                    cun = total * 1/5
                    guan = total * 1/2
                    chi = total * 33/40
                    cunx = cun / ((m*m+1)**(0.5))
                    cuny = round(m * cunx)
                    cunx = round(cunx)
                    guanx = guan / ((m*m+1)**(0.5))
                    guany = round(m * guanx)
                    guanx = round(guanx)
                    chix = chi / ((m*m+1)**(0.5))
                    chiy = round(m * chix)
                    chix = round(chix)
                    if m < 0:
                        cunx = originx + cunx
                        cuny = originy - cuny
                        guanx = originx + guanx
                        guany = originy - guany
                        chix = originx + chix
                        chiy = originy - chiy
                    if m > 0:
                        cunx = originx - cunx
                        cuny = originy + cuny
                        guanx = originx - guanx
                        guany = originy + guany
                        chix = originx - chix
                        chiy = originy + chiy
                    #大拇指4和3的間距
                    shift = dist((bigFinger4_X, bigFinger4_Y), (bigFinger3_X, bigFinger3_Y))/2
                    shift_m = -1 / m
                    shift_x = 0
                    shift_y = 0
                    shift_x = round(shift / ((shift_m*shift_m+1)**(0.5)))
                    shift_y = round(shift_m * shift_x)
                    #尚未左右移動的點
                    cv2.circle(img, (cunx, cuny), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (guanx, guany), 5, preTargetStyle, cv2.FILLED)
                    cv2.circle(img, (chix, chiy), 5, preTargetStyle, cv2.FILLED)
                    # #根據比例左右移動後的點
                    if bigFinger4_X - originx >= 0:
                        cv2.circle(img, (cunx + shift_x, cuny - shift_y), 5, preTargetStyle, cv2.FILLED)
                        cv2.circle(img, (guanx + shift_x, guany - shift_y), 5, preTargetStyle, cv2.FILLED)
                        cv2.circle(img, (chix + shift_x, chiy - shift_y), 5, preTargetStyle, cv2.FILLED)
                    else:
                        cv2.circle(img, (cunx - shift_x, cuny - shift_y), 5, preTargetStyle, cv2.FILLED)
                        cv2.circle(img, (guanx - shift_x, guany - shift_y), 5, preTargetStyle, cv2.FILLED)
                        cv2.circle(img, (chix - shift_x, chiy - shift_y), 5, preTargetStyle, cv2.FILLED)
                    mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS, handLmsStyle, handConStyle)

    img2 = Image.fromarray(img)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image = img2)
    Cam_View.imgtk = imgtk
    Cam_View.configure(image=imgtk)
    # Repeat after an interval to capture continiously
    Cam_View.after(20, show_frames)




    #    cv2image= cv2.cvtColor(left[t],cv2.COLOR_BGR2RGB)
    #    img2 = Image.fromarray(cv2image)
    #    # Convert image to PhotoImage
    #    imgtk = ImageTk.PhotoImage(image = img2)
    #    Cam_View.imgtk = imgtk
    #    Cam_View.configure(image=imgtk)
    #    # Repeat after an interval to capture continiously
    #    Cam_View.after(20, show_frames)


def switch_camera(): 
    global is_on

    if is_on: 
        is_on = False
    else: 
        is_on = True


# arduino = Serial(port=arduino_port, baudrate= 115200, timeout = .1)


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
    t2 = threading.Thread(target = connect_sensor, daemon = True)
    t2.start() 

    root.mainloop()

if __name__ == "__main__": 
    main()