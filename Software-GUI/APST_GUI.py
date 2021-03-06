#Tyler Eck 
#410821337 
#Undergraudate Project - Main GUI 
#Automated Pulse Sensing Tool 

#################################### Libraries ####################################

#TKINTER 
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from copy import deepcopy
from PIL import Image, ImageTk
import cv2 
import numpy as np

#ARDUINO SERIAL 
from serial import Serial
import usb.core 
import usb.util
import sys
import serial.tools.list_ports 

#LIVE PLOTTING - MATPLOTLIB
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button as b


#HAND RECOGNITION
import mediapipe as mp
import time
from slope import getValue, find_m, getValueWithM
from math import dist

#Firebase
import pyrebase
config = {
    "apiKey": "AIzaSyB_RREgqDSu0hWWt3eWH4lqSz-aTAN4mFs",
    "authDomain": "automated-pulse-sensing-tool.firebaseapp.com",
    "databaseURL": "https://automated-pulse-sensing-tool-default-rtdb.firebaseio.com/",
    "projectId": "automated-pulse-sensing-tool",
    "storageBucket": "automated-pulse-sensing-tool.appspot.com",
    "serviceAccount":"firebase_authentication.json"
}

firebase_storage = pyrebase.initialize_app(config) 
storage = firebase_storage.storage()

#################################### DECLARATIONS ####################################
global ani
global clicked_X 
global clicked_Y
global CLICKED 
global AUTO_START
global DETECT_COUNT 
global FINAL_CUNX
global FINAL_CUNY
global ANA 
global SCAN_AUTO_START
ARDUINO_CONNECT = 0
SENSOR_CONNECT = 0
STOP_SCAN = 0
DETECTION = 0
STOP_FRAME = 0
clicked_X = 0 
clicked_Y = 0
CLICKED = 0
AUTO_START = 0
DETECT_COUNT = 0
ANA = 0
SCAN_AUTO_START = 0
is_on = False
mode = "Manual"
arduino_port = 'COM3'
Step = 50
MAX_X = 250
MAX_Y = 250
MAX_Z = 272

#Initial start points so camera can view hand 
current_pos = np.array([0,0,0])
current_pos[0] = 135
current_pos[1] = 100 
current_pos[2] = 272


#Use for the MAIN data 
Measure = { 
    "X":[], 
    "Pressure":[],
    "Pulse":[]
}

#Used for temporary live plotting of data
Pressure_graph = [] 
Pulse_graph = []
Plot_X =[] 
global ax, ax2

global start,end

#Hand and Pulse Point Detection Setup
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
N1= 1
FINAL_CUNX = 0 
FINAL_CUNY = 0

#################################### FUNCTIONS ####################################

#Movement for the Sensor
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

def move_Right():
    global current_pos
    if current_pos[0]-Step <= 0:
        current_pos[0] = 0
    else: 
        current_pos[0] -= Step
    write()
    

def move_Left():
    global current_pos
    if current_pos[0]+Step >=MAX_X: 
        current_pos[0] = MAX_X
    else:
        current_pos[0] +=Step
    write()


#Movement for the Base
def move_base_Up():
    global current_pos
    if current_pos[1]+Step >=MAX_Y: 
        current_pos[1] = MAX_Y
    else:
        current_pos[1] +=Step
    write() 

def move_base_Down():
    global current_pos
    if current_pos[1]-Step <= 0:
        current_pos[1] = 0
    else: 
        current_pos[1] -= Step
    write()


#Write to the arduino the current position to move
def write():
    global current_pos
    num = str(current_pos[0])+","+str(current_pos[1])+","+str(current_pos[2])
    num = "("+ num +")"
    print(num)
    arduino.write(num.encode())


#Start scanning by setting everything to null and plotting data
def start_scan(val):
    global Pressure_graph
    global Pulse_graph
    global Plot_X
    global STOP_SCAN

    print('Scan Started')

    Measure["X"]=[]
    Measure["Pressure"] =[] 
    Measure["Pulse"] = []
    Pressure_graph = [] 
    Pulse_graph = []
    Plot_X = []

    #Set stop flag to false
    STOP_SCAN = 0

    #Make a thread for the sensor to read
    SCAN_T = threading.Thread(target = sensor_read, daemon = True)
    SCAN_T.start()

    plot_sensor_data()


#If user presses Stop Scan button then plot will be displayed in main area
def stop_scan(val): 
    global ani
    global plt
    global Pressure_graph
    global Pulse_graph
    global Plot_X
    global start,end
    global ax2
    start = 0 
    end = len(Measure["X"])

    Pressure_graph = [] 
    Pulse_graph = []
    Plot_X = []

    #Set stop flag to true
    global STOP_SCAN
    STOP_SCAN = 1
    plt.close()

    #Plotting in Main Window
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


#reading values from sensor
def sensor_read():
    global sensor_port
    global STOP_SCAN
    global Pressure_graph
    global Pulse_graph
    global Plot_X
    global SCAN_AUTO_START
    global plt

    sensor = Serial(port= 'COM5', 
    baudrate = 256000, 
    parity = serial.PARITY_NONE,
    bytesize = 8, stopbits=serial.STOPBITS_ONE)
    sensor.write([0xF0, 0x2F, 0x01, 0x32])

    # Set the pressure value to zero
    # sensor.write([0xF0, 0x2F, 0x01, 0x34]) 

    #SENSOR DATA- first 4 values stay the same 
    #[0xF0,0x1F,0x06,0x32,JYL,JYM,MBL,MBH,CHECK] 
    #JYL - Low byte of pressure 
    #JYH - High byte of pressure 
    #MBL - Low byte of pulse wave 
    #MBH - High byte of pulse wave 
    #CHECK - Low byte of (JYL+JYH+MBL+MBH)

    n =[] 
    Pressure = 0 
    Pulse = 0
    displaynumber  = 1000 #200Hz = 5 secs of data
    start_time = time.time()

    while True: 
        serialString = sensor.read()
        temp = int.from_bytes(serialString, byteorder=sys.byteorder)
        n.append(temp)
        if len(n) == 9:
            current_time = time.time()
            plot_time = current_time - start_time
            Pressure = n[5]<<8|n[4]
            Pulse = int(((n[7]<<8)|n[6])/25)
            Measure["X"].append(plot_time) 
            Measure["Pressure"].append(Pressure)
            Measure["Pulse"].append(Pulse)

            if len(Plot_X) < displaynumber: 
                Plot_X.append(plot_time) 
            else: 
                Plot_X[0:displaynumber-1] = Plot_X[1:displaynumber] 
                Plot_X[displaynumber-1] = plot_time

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
            
            #Automatic Mode
            if SCAN_AUTO_START: 
                if plot_time >=30:
                    #moves motors up so person can move hand
                    current_pos[2] = 272
                    write()
                    SCAN_AUTO_START = 0
                    break

            
            n=[]        
        if STOP_SCAN:
            #moves motors up so person can move hand
            current_pos[2] = 272
            write()
            break

    sensor.write([0xF0, 0x2F, 0x01, 0x33])
    print('Scan Ended')


#live animation of plotting sensor data as its being read
def plot_sensor_data():
    global plt
    global ax
    ax = plt.subplot(111)
    global ani

    def animate(f):
        x = deepcopy(Plot_X)
        Pressure = deepcopy(Pressure_graph)
        Pulse = deepcopy(Pulse_graph)

        ax.cla()
        
        ax.plot(x, Pulse, label ='Pulse')
        ax.plot(x, Pressure, label ='Pressure')

        ax.legend(loc = "upper left")

    axcut1 = plt.axes([0.9, 0.00001, 0.1, 0.1])
    bcut1 = b(axcut1, 'Stop')
    bcut1.on_clicked(stop_scan)

    ani = FuncAnimation(plt.gcf(),animate, interval=1)
    plt.show()



#always check if sensors and arduino are connected
def connect_sensor():
    global SENSOR_CONNECT 
    global ARDUINO_CONNECT 
    global sensor_port 
    global arduino_port
    global arduino
    while True: 
        SENSOR_CONNECT = 0
        ARDUINO_CONNECT = 0
        ports = serial.tools.list_ports.comports()
        for p in ports: 
            VID = p.vid 
            PID = p.pid 

            if VID == 4292 and PID == 60000: #sensor PID and VID
                SENSOR_CONNECT = 1
                sensor_port = p[0] #get the COM 
            if VID == 1027 and PID == 24577: #arduino PID and VID
                ARDUINO_CONNECT = 1
                arduino_port = p[0] #get the COM
                
                arduino = Serial(port=arduino_port, baudrate= 115200, timeout = .1)

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
        
        
#Upload scan function 
def upload_scan():
    global start, end, ax2
    global plt
    global Measure
    if len(nameinfo.get('1.0',tk.END)) == 1 or len(descriptioninfo.get('1.0',tk.END)) == 1:
        messagebox.showinfo("Error", "Please Enter Name and Description for Scan Before Uploading")
    else: 
        Name = nameinfo.get('1.0', 'end-1c')
        Description = descriptioninfo.get('1.0', 'end-1c')

        file = open(Name+"_PulseInfo.txt", "a")
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
        figure = plt.Figure(figsize = (6,5), dpi = 100)
        ax2 = figure.add_subplot(111)
        x = Measure["X"][start:end]
        Pressure = Measure["Pressure"][start:end]
        Pulse = Measure["Pulse"][start:end]
        ax2.plot(x, Pulse, label ='Pulse')
        ax2.plot(x, Pressure, label ='Pressure') 

        
        figure.savefig(Name+".png")

        nameinfo.delete('1.0', tk.END)
        descriptioninfo.delete('1.0', tk.END)
        
        #Upload Scan to Firebase
        path_icloud_image = "Patients/"+Name+"/"+Name+".png"
        path_icloud_file = "Patients/"+Name+"/"+Name+"_PulseInfo.txt"
        path_of_image = Name+".png"
        path_of_file = Name+"_PulseInfo.txt"

        storage.child(path_icloud_file).put(path_of_file)
        storage.child(path_icloud_image).put(path_of_image)
        print("Scan uploaded")

        #Reset data back to 0 for new scan
        start = 0 
        end = 0 
        Measure["X"] = [] 
        Measure["Pulse"] = [] 
        Measure["Pressure"] = []

        #Resets the main figure
        figure = plt.Figure(figsize = (6,5), dpi = 100)
        ax2 = figure.add_subplot(111) 
        bar1 = FigureCanvasTkAgg(figure, right_frame)
        bar1.get_tk_widget().place(x = 25, y = 20)
        x = Measure["X"]
        Pressure = Measure["Pressure"] 
        Pulse = Measure["Pulse"]
        ax2.plot(x, Pulse, label ='Pulse')
        ax2.plot(x, Pressure, label ='Pressure')




#Used to increase/decrease the steps for movement 
def scale(i):
    global g
    global Step
    g.set(int(scale.get()))
    Step = int(g.get())
    Step_Value.config(text=str(int(scale.get())))


#Pressed when user finishes editting scan
def finish_edit_scan(val):
    global start,end

    global plt
    plt.close()

    figure = plt.Figure(figsize = (6,5), dpi = 100)
    ax2 = figure.add_subplot(111) 
    bar1 = FigureCanvasTkAgg(figure, right_frame)
    bar1.get_tk_widget().place(x = 25, y = 20)

    #find the closest value in list to the start and end value 
    s = min(Measure["X"], key=lambda x:abs(x-start))
    e = min(Measure["X"], key=lambda x:abs(x-end))

    #find index of that closest value 
    start = Measure["X"].index(s)
    end = Measure["X"].index(e)

    x = Measure["X"][start:end]
    Pressure = Measure["Pressure"][start:end]
    Pulse = Measure["Pulse"][start:end]

    ax2.plot(x, Pulse, label ='Pulse')
    ax2.plot(x, Pressure, label ='Pressure')
    bar1.draw()

#Allows user to edit scan
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
                    start = float(x)
                    end = 0
                    if removeflag:
                        line2.remove()
                        Plot.canvas.draw_idle()
                        removeflag= 0

                    if not doubleclick:
                        line2 = Axis.axvspan(start, start+0.0001, color='red', alpha=0.5)
                        Plot.canvas.draw_idle()
                        doubleclick = 1
                    else: 
                        line2.remove()
                        Plot.canvas.draw_idle()
                        line2 = Axis.axvspan(start, start+0.0001, color='red', alpha=0.5)
                        Plot.canvas.draw_idle()


                elif event.button is MouseButton.RIGHT:
                    end = float(x)
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
                            'Pos', 0, (len(x)-1001)) #last value minus 5 seconds because only 5 seconds can show

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
        
            Axis.axis([x[index], x[index+1000], min-10, max+10])
            Plot.canvas.draw_idle()
        else:
            max = 0 
            min = 1000
            for i in range(index, len(x)): 
                if Measure["Pulse"][i] >max: 
                    max = Measure["Pulse"][i]
                if Measure["Pulse"][i] < min: 
                    min = Measure["Pulse"][i]
            
            Axis.axis([x[index], x[index+1000], min-10, max+10])
            Plot.canvas.draw_idle()

    #Finished Button for finish editting
    axcut1 = plt.axes([0.9, 0.00001, 0.1, 0.1])
    bcut1 = b(axcut1, 'Finish')
    bcut1.on_clicked(finish_edit_scan)

    slider_position.on_changed(update)
    plt.show()

#main camera function used to show live camera feed
def show_frames():
    global is_on
    global N1
    global DETECTION
    global STOP_FRAME
    global clicked_X
    global clicked_Y
    global AUTO_START
    global FINAL_CUNX
    global FINAL_CUNY
    global DETECT_COUNT
    global ANA 
    global plt

    if is_on: 
        retval, frame = cap.read()
       
        if retval:
            img = np.split(frame, 2,axis = 1)
            img = img[0] #Left Camera 
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            result = hands.process(imgRGB)
            
            imgHeight = img.shape[0]
            imgWidth = img.shape[1]
            total = 0.0

            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if DETECTION: 
                if result.multi_hand_landmarks:
                    for handLms in result.multi_hand_landmarks: 

                        #Gets the 11 handlandmarks used to calculate the pulse point
                        originx = 0 
                        originy = 0
                        bigFinger4_X = 0 
                        bigFinger4_Y = 0
                        bigFinger3_X = 0 
                        bigFinger3_Y = 0
                        secFinger5_X = 0 
                        secFinger5_Y = 0
                        thirdFinger9_X = 0 
                        thirdFinger9_Y = 0
                        fourthFinger13_X = 0 
                        fourthFinger13_Y = 0
                        fifthFinger17_X = 0 
                        fifthFinger17_Y = 0

                        for i, lm in enumerate(handLms.landmark):
                            xPos = round(lm.x * imgWidth)
                            yPos = round(lm.y * imgHeight)
                            if i == 0:
                                originx = xPos
                                originy = yPos
                            if i == 3:
                                bigFinger3_X = xPos
                                bigFinger3_Y = yPos
                            if i == 4:
                                bigFinger4_X = xPos
                                bigFinger4_Y = yPos
                            if i == 5:
                                secFinger5_X = xPos
                                secFinger5_Y = yPos
                            if i == 6:
                                if (secFinger5_X-xPos) != 0:
                                    total += getValueWithM(xPos, yPos, -1* (secFinger5_Y-yPos)/(secFinger5_X-xPos),img)
                                else:
                                    total += getValueWithM(xPos, yPos, infinity,img)
                                print("key: ", i, ", total: ", total)
                            if i == 9:
                                thirdFinger9_X = xPos 
                                thirdFinger9_Y = yPos
                            if i == 10:
                                if (thirdFinger9_X-xPos) != 0:
                                    total += getValueWithM(xPos, yPos, -1* (thirdFinger9_Y-yPos)/(thirdFinger9_X-xPos),img)
                                else:
                                    total += getValueWithM(xPos, yPos, infinity,img)
                                print("key: ", i, ", total: ", total)
                            if i == 13:
                                fourthFinger13_X = xPos 
                                fourthFinger13_Y = yPos
                            if i == 14:
                                if (fourthFinger13_X-xPos) != 0:
                                    total += getValueWithM(xPos, yPos, -1* (fourthFinger13_Y-yPos)/(fourthFinger13_X-xPos),img)
                                else:
                                    total += getValueWithM(xPos, yPos, infinity,img)
                                print("key: ", i, ", total: ", total)
                            if i == 17:
                                fifthFinger17_X = xPos 
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
                            m = find_m(originx, originy+ round(img.shape[0]/6) , img)
                            if m:
                                cun = total * 1/5
                                # guan = total * 1/2
                                # chi = total * 33/40
                                cunx = cun / ((m*m+1)**(0.5))
                                cuny = round(m * cunx)
                                cunx = round(cunx)
                                # guanx = guan / ((m*m+1)**(0.5))
                                # guany = round(m * guanx)
                                # guanx = round(guanx)
                                # chix = chi / ((m*m+1)**(0.5))
                                # chiy = round(m * chix)
                                # chix = round(chix)
                                if m < 0:
                                    cunx = originx + cunx
                                    cuny = originy - cuny
                                    # guanx = originx + guanx
                                    # guany = originy - guany
                                    # chix = originx + chix
                                    # chiy = originy - chiy
                                if m > 0:
                                    cunx = originx - cunx
                                    cuny = originy + cuny
                                    # guanx = originx - guanx
                                    # guany = originy + guany
                                    # chix = originx - chix
                                    # chiy = originy + chiy
                                shift = dist((bigFinger4_X, bigFinger4_Y), (bigFinger3_X, bigFinger3_Y))/2
                                shift_m = -1 / m
                                shift_x = 0
                                shift_y = 0
                                shift_x = round(shift / ((shift_m*shift_m+1)**(0.5)))
                                shift_y = round(shift_m * shift_x)
                                cv2.circle(img, (cunx, cuny), 5, (255,0,0), cv2.FILLED)
                                # cv2.circle(img, (guanx, guany), 5, (255,0,0), cv2.FILLED)
                                # cv2.circle(img, (chix, chiy), 5, (255,0,0), cv2.FILLED)
                                if bigFinger4_X - originx >= 0:
                                    cv2.circle(img, (cunx + shift_x, cuny - shift_y), 5, (255,0,0), cv2.FILLED)
                                    # cv2.circle(img, (guanx + shift_x, guany - shift_y), 5, (255,0,0), cv2.FILLED)
                                    # cv2.circle(img, (chix + shift_x, chiy - shift_y), 5, (255,0,0), cv2.FILLED)
                                else:
                                    cv2.circle(img, (cunx - shift_x, cuny - shift_y), 5, (255,0,0), cv2.FILLED)
                                    # cv2.circle(img, (guanx - shift_x, guany - shift_y), 5, (255,0,0), cv2.FILLED)
                                    # cv2.circle(img, (chix - shift_x, chiy - shift_y), 5, (255,0,0), cv2.FILLED)
                                FINAL_CUNX = cunx 
                                FINAL_CUNY = cuny

                                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS, handLmsStyle, handConStyle)
            #Draws the sensor circle 
            circle_pos_w = int(imgWidth/2 + 4) + 45
            circle_pos_h = int(imgHeight/2 + 7) - 3
            circle_radius = 10
            cv2.circle(img, (circle_pos_w ,circle_pos_h), circle_radius, (0,0,255), 2)

            #displays clicked point one time
            if N1 == 0:
                cv2.circle(img, (clicked_X,clicked_Y), 5, (255,0,0), cv2.FILLED)
                N1 = 1

            if STOP_FRAME: #if its on manual mode 
                is_on = False
                clicked_Y = 0
                clicked_X = 0
                waitThread = threading.Thread(target = select_point, args = (img,))
                waitThread.start()
                # move_to_distance(circle_pos_w, circle_pos_h, cun_x, cun_y)
                STOP_FRAME = False
            
            if AUTO_START: #if its on automatic mode
                print("DETECTION TIMER START")
                waitThread2 = threading.Thread(target = detect_countdown)
                waitThread2.start()
                AUTO_START = 0

            if DETECT_COUNT: #we've stopped the detection and will move to the location 
                AUTO_START = 0
                DETECT_COUNT = 0
                move_to_distance(circle_pos_w, circle_pos_h, FINAL_CUNX, FINAL_CUNY)

            if ANA: 
                auto_scan()
                ANA = 0
            

            #write frame of camera in Tkinter frame
            img2 = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image = img2)
            Cam_View.imgtk = imgtk
            Cam_View.configure(image=imgtk)
            Cam_View.after(20, show_frames)

    else:
        Cam_View.after(20, show_frames)

#Used to switch camera on and off 
def switch_camera(): 
    global is_on
    if is_on: 
        is_on = False
    else: 
        is_on = True

#Used to switch detection on and off
def detect(): 
    global DETECTION
    if DETECTION == False:
        DETECTION = True
    else: 
        DETECTION = False


######################  MANUAL MODE: User stops frame and selects point  ######################
def stop_frame(): 
    global STOP_FRAME 
    global N1
    STOP_FRAME = 1
    N1 = 1

def leftclick(event):
    global clicked_X 
    global clicked_Y 
    global CLICKED 
    clicked_X = event.x +190
    clicked_Y = event.y +100
    CLICKED = 1
    root.unbind('<Button-1>')

def select_point(img):
    global clicked_X 
    global clicked_Y
    global CLICKED 
    global is_on
    global N1 
    global DETECTION 
    DETECTION = 0
    root.bind("<Button-1>", leftclick)
    while not CLICKED:
        if clicked_X!= 0 and clicked_Y!=0:  
            print('{},{}'.format(clicked_X,clicked_Y))
            CLICKED = 1
    CLICKED = 0
    is_on = True
    N1 = 0
    mid_x = int(img.shape[1]/2 + 4) + 45
    mid_y = int(img.shape[0]/2 + 7) - 3
    move_to_distance(mid_x, mid_y, clicked_X, clicked_Y)
    

######################  AUTOMATIC MODE: User waits for detection, movement, and scanning  ######################

#countdown after instructions 
def count_down():
    global DETECTION 
    global AUTO_START
    start_time = time.time()
    while True:
        current_time = time.time()
        if  current_time - start_time >= 5:
            print("INSTRUCTION TIMER END ")
            DETECTION = True
            AUTO_START = True 
            break

#countdown for detection
def detect_countdown():
    global DETECTION
    global DETECT_COUNT
    start_time = time.time()
    while True:
        current_time = time.time()
        if  current_time - start_time >= 5:
            print("DETECTION TIMER END")
            DETECTION = False
            DETECT_COUNT = True
            break

#moves motors from (x1,y1) to (x2,y2) for both Automatic and Manual
def move_to_distance(x1,y1,x2,y2):
    global FINAL_CUNX 
    global FINAL_CUNY
    move_x = abs(x1-x2) 
    move_y = abs(y1-y2) 

    add_x = int(round(float((move_x+20)/10)))
    move_x+=add_x

    add_y = int(round(float((move_y+20)/10)))
    move_y+=add_y

    #Direction of movement 
    if x1>x2: 
        if y1<y2: 
            current_pos[0] += move_x
            current_pos[1] += move_y 
        else: 
            current_pos[0] += move_x
            current_pos[1] -= move_y 
    else:
        if y1<y2:
             current_pos[0] -= move_x
             current_pos[1] += move_y
        else: 
            current_pos[0] -= move_x
            current_pos[1] -= move_y

    #BOUND CHECKING
    if current_pos[0] < 0: 
        current_pos[0] = 0
    if current_pos[0] > MAX_X: 
        current_pos[0] = MAX_X
    if current_pos[1] < 0: 
        current_pos[1] = 0
    if current_pos[1] > MAX_Y: 
        current_pos[1] = MAX_Y
    
    print(x1, y1, x2, y2)
    print(move_x, move_y)
    write()

    #WE HAVE PROPER X and Y, now we need Z for automatic mode 
    if MODE.get() == "Automatic":
        print("FINISHED MOVING ")
        FINAL_CUNX = 0 
        FINAL_CUNY = 0 
        time.sleep(3)
        movement = threading.Thread(target = auto_movement)
        movement.start()


#used to move to appropriate Z - avoid too much pressure 
def auto_movement(): 
    global ANA 
    #First move the z to a reasonable position 
    current_pos[2] = 25
    write()
    time.sleep(8)
    while True: 
        check_p = check_pulse_value() 
        if check_p:
            ANA = 1
            print("ENDS ALL MOVEMENT")
            break
        else:
            if current_pos[2]-2 < 0: 
                current_pos[2] = 0 
            else: 
                current_pos[2]-=2
            write()


#takes temporary sensor data to determine if right Z value is reached
def check_pulse_value(): 
    check_pulse = 0
    x = 0

    global sensor_port
    sensor = Serial(port= 'COM5', 
    baudrate = 256000, 
    parity = serial.PARITY_NONE,
    bytesize = 8, stopbits=serial.STOPBITS_ONE)
    sensor.write([0xF0, 0x2F, 0x01, 0x32])

    n =[] 
    start_time = time.time()
    current_time = 0

    while True: 
        serialString = sensor.read()
        temp = int.from_bytes(serialString, byteorder=sys.byteorder)
        n.append(temp)
        if len(n) == 9:
            current_time = time.time()
            # Pressure = n[5]<<8|n[4]
            Pulse = int(((n[7]<<8)|n[6])/25)
            check_pulse+= Pulse
            n=[]
            x +=1        
        
        if current_time - start_time >=2:
            break

    sensor.write([0xF0, 0x2F, 0x01, 0x33])

    avg = check_pulse/x
    print(avg)
    if avg<=90: 
        return False 
    else: 
        return True

#starts autoscan when right Z place is reached
def auto_scan():
    global SCAN_AUTO_START
    SCAN_AUTO_START = 1
    start_scan(1)


#Selection between Automatic or Manual
def select_mode(): 
    m = MODE.get()
    global is_on
    global DETECTION
    global clicked_X
    global clicked_Y
    global AUTO_START
    global SCAN_AUTO_START
    if m == "Manual": #enable buttons and set all flags to 0 
        Up["state"] = "normal"
        Down["state"] = "normal"
        Left["state"] = "normal"
        Right["state"] = "normal" 
        Scan_B["state"] = "normal"
        Base_Up["state"] = "normal"
        Base_Down["state"] = "normal"
        Detect_B["state"] = "normal"
        Stop_Frame["state"] = "normal"
        OpenGraph["state"] = "normal"
        AUTO_START = 0
        SCAN_AUTO_START = 0


        clicked_X = 0
        clicked_Y = 0
        #Go back to original position
        current_pos[1] = 100 
        current_pos[2] = 272
        current_pos[0] = 135
        write()
    else:
        Up["state"] = "disabled"
        Down["state"] = "disabled"
        Left["state"] = "disabled"
        Right["state"] = "disabled" 
        Scan_B["state"] = "disabled"
        Base_Up["state"] = "disabled"
        Base_Down["state"] = "disabled"
        Detect_B["state"] = "disabled"
        Stop_Frame["state"] = "disabled"
        OpenGraph["state"] = "disabled"

        #Go back to original position
        current_pos[1] = 100 
        current_pos[2] = 272
        current_pos[0] = 135
        write()

        #User manual pops up
        top = tk.Toplevel() 
        x = root.winfo_x()
        y = root.winfo_y()
        top.geometry("+%d+%d" %(x+100,y+10))
        top.title("User Guide") 
    
        
        global page
        page = 0

        def next():
           global page
           if page == 0:
               Back["state"] = "normal"
           page+=1

           if page ==6:
               Next["state"] = "disabled"
               Finish["state"] = "normal"

           global next_im
           next_im = ImageTk.PhotoImage(Image.open('./automatic_mode_instructions/'+str(page)+'.png'))
           main_label.configure(image = next_im)
           top.update()
            
        def back():
            global page
            if page == 6: 
                Next["state"] = "normal"
                Finish["state"] = "disabled"
            page-=1
            if page == 0: 
                Back["state"] = "disabled"

            global prev_im
            prev_im = ImageTk.PhotoImage(Image.open('./automatic_mode_instructions/'+str(page)+'.png'))
            main_label.configure(image = prev_im)
            top.update()
        
        def finish(): 
            print("INSTRUCTION TIMER START")
            t2 = threading.Thread(target = count_down)
            t2.start()
            top.destroy()
        

        global beg_ins
        Start = Image.open('./automatic_mode_instructions/0.png')
        beg_ins = ImageTk.PhotoImage(Start)

        main_label = tk.Label(top, image = beg_ins)
        main_label.pack()
    

        Next = tk.Button(top, text = "Next", height = 2, width = 6 , command= next)
        Next.pack(side = "right") 

        Back = tk.Button(top, text = "Back", height = 2, width = 6 , command = back)
        Back.pack(side = "left")
        if page == 0:
            Back["state"] = "disabled"
        
        Finish = tk.Button(top, text = "Finish",height = 2, width = 6 , command= finish)
        Finish.pack()
        if page == 0:
            Finish["state"] = "disabled"


#################################### MAIN TKINTER WINDOW DECLARATIONS ####################################
root = tk.Tk()
root.title('Automated Pulse Sensing Tool')

window_height = 700
window_width = 1000

#Used for step selection
g = tk.IntVar()
g.set(50)
Step = int(g.get())

#Window and Design Setup 
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
style = ttk.Style(root)
root.tk.call('source', 'GUI_Design/azure dark.tcl')
style.theme_use('azure')


#############  Live Camera Feed Area #############

frame1 = ttk.LabelFrame(root, text="Camera", width=320, height=255)
frame1.place(x=20, y=12)
black_border = tk.Frame(frame1, width = 305, height = 190,bg = "white")
black_border.place(x=5, y=5)
Cam_View = tk.Label(frame1, width = 290, height = 175)
Cam_View.place(x=10, y = 10)
cap = cv2.VideoCapture(0)
show_frames()

switch = ttk.Checkbutton(frame1, style='Switch',command = switch_camera)
switch.place(x=140, y=205)
switch.invoke()

Stop_Frame = ttk.Button(frame1, text = "Stop", style='Accentbutton', command = stop_frame)
Stop_Frame.place(x = 10, y = 200)
Detect_B = ttk.Button(frame1, text = "Detect", style='Accentbutton', command = detect)
Detect_B.place(x = 220, y = 200)




#############  Options/Configuration Area #############
frame2 = ttk.LabelFrame(root, text='Options', width=320, height=320)
frame2.place(x=20, y=290)

Mode_label = tk.Label(frame2, text='Mode') 
Mode_label.place(x=40, y = 40)
MODE = tk.StringVar()
Manual = tk.Radiobutton(frame2, text="Manual", variable = MODE, indicatoron = False, value = "Manual", width = 10, selectcolor="#007FFF", command = select_mode)
Manual.invoke()
Automatic = tk.Radiobutton(frame2, text="Automatic", variable = MODE, indicatoron = False, value = "Automatic", width = 10,  selectcolor="#007FFF", command = select_mode)
Manual.place(x = 120, y = 40)
Automatic.place(x = 200, y = 40)

Move_label = tk.Label(frame2, text='Movement') 
Move_label.place(x=20, y = 110)
Up = tk.Button(frame2, text = "??", command = move_Up) 
Down = tk.Button(frame2, text = "v", command = move_Down)
Left = tk.Button(frame2, text = "<", command = move_Left)
Right = tk.Button(frame2, text = ">", command = move_Right)
Sensor_Move_Label = tk.Label(frame2, text="Sensor")

Base_Up = tk.Button(frame2, text = "??", command = move_base_Up) 
Base_Down = tk.Button(frame2, text = "v", command = move_base_Down)
Base_Move_Label = tk.Label(frame2, text="Base")
ix = -20
iy = 20
Up.place(x = 170+ix, y = 60+iy)
Left.place(x = 140+ix, y = 90+iy)
Right.place(x= 200+ix, y = 90+iy)
Down.place(x = 170+ix, y = 120+iy)
Sensor_Move_Label.place(x = 159+ix, y =90+iy+2)

Base_Up.place(x = 170+ix+90-4, y = 60+iy+5)
Base_Down.place(x = 170+ix+90-4, y = 120+iy-5)
Base_Move_Label.place(x = 170+ix+83-4, y = 90+iy+2)

global arduino 

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


#############  Graph Display Area #############
right_frame = tk.Frame(root, width = 650, height = 700, bg = "grey")
right_frame.place(x = 350, y = 0)

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


#############  Information Input Area #############

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



#################################### MAIN ####################################
def main():
    
    #Always running to check if sensors and arduinos are connected
    t2 = threading.Thread(target = connect_sensor, daemon = True)
    t2.start() 


    root.mainloop()

if __name__ == "__main__": 
    main()