#Tyler Eck 
#Automated Pulse Sensing Tool 
#3rd Year Undergraduate Project 

from tkinter import *
from serial import Serial
import usb.core 
import usb.util
import sys
import time 
import serial.tools.list_ports 
from threading import *
from copy import deepcopy
import matplotlib.pyplot as plt
import csv 
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)



current_pos = [0,0,0]
global Move
Move =""
Step = 10
old_pos =[0,0,0]
MAX_X = 250
MAX_Y = 250
MAX_Z = 300
global STOP_SCAN
STOP_SCAN = 0
global SENSOR_CONNECT
SENSOR_CONNECT = 0
global ARDUINO_CONNECT 
ARDUINO_CONNECT = 0
global sensor_port 
global arduino_port
arduino_port = 'COM3'
global READING
READING = 0

Measure = { 
    "X":[], 
    "Pressure":[],
    "Pulse":[]
}


#Main Page 
root = Tk()

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

def start_scan():
    print('Scan Started')

    #Set stop flag to false
    global STOP_SCAN
    STOP_SCAN = 0

    #Make a thread for the sensor to read
    global SCAN_T 
    SCAN_T = Thread(target = sensor_read, daemon = True)
    SCAN_T.start()

    plot_sensor_data()

def stop_scan(): 

    #Set stop flag to true
    global STOP_SCAN
    STOP_SCAN = 1
    plt.clf()
    Measure["X"]=[]
    Measure["Pressure"] =[] 
    Measure["Pulse"] = []




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

            Pressure = (n[5]<<8)|n[4]
            Pulse = int(((n[7]<<8)|n[6])/25)
            Measure["X"].append(X) 
            Measure["Pressure"].append(Pressure)
            Measure["Pulse"].append(Pulse)
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

    def animate(i):
        x = Measure["X"]
        Pressure = Measure["Pressure"] 
        Pulse = Measure["Pulse"]

        plt.cla()

        plt.plot(x, Pulse, label ='Pulse')
        plt.plot(x, Pressure, label ='Pressure')

        plt.legend(loc = "upper left")
        plt.tight_layout()

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
            Start_Scan_Button["state"] = "normal" 
            Stop_Scan_Button["state"] = "normal"
        else: 
            Sensor_Connect_Status.config(text = "Disconnected")
            Start_Scan_Button["state"] = "disabled" 
            Stop_Scan_Button["state"] = "disabled"

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

#Enable or Disable the buttons based on what mode
def Automatic(): 
    Up["state"] = "disabled"
    Down["state"] = "disabled"
    Left["state"] = "disabled"
    Right["state"] = "disabled"

def Manual():
    Up["state"] = "normal"
    Down["state"] = "normal"
    Left["state"] = "normal"
    Right["state"] = "normal"


#Buttons for Automatic or Manual mode 
Automatic_Button = Button(root, text = "Automatic",padx = 10, pady = 10, command = Automatic)
Manual_Button = Button(root, text = "Manual",padx = 10, pady = 10, command = Manual)

Start_Scan_Button = Button(root, text = "Start Scan",padx = 10, pady = 10, command = start_scan)
Stop_Scan_Button = Button(root, text = "Stop Scan",padx = 10, pady = 10, command = stop_scan)

#Buttons for Manual movement of motors
Up = Button(root, text = "Up",padx = 10, pady = 10, command = move_Up)
Down = Button(root, text = "Down",padx = 10, pady = 10, command = move_Down)
Left = Button(root, text = "Left",padx = 10, pady = 10, command = move_Left)
Right = Button(root, text = "Right",padx = 10, pady = 10, command = move_Right)

Automatic_Button.grid(row = 1, column = 1)
Manual_Button.grid(row = 1, column = 2)
Up.grid(row = 2, column = 2)
Down.grid(row =4, column = 2)
Left.grid(row = 3, column = 1)
Right.grid(row = 3, column = 3)
Start_Scan_Button.grid(row = 5, column = 0)
Stop_Scan_Button.grid(row = 5, column = 2)

#Label 
Sensor_Connect_Label1 = Label(root, text = "Pulse Sensor: ")
Sensor_Connect_Status = Label(root, text = "Not Connected")
Sensor_Connect_Label1.grid(row = 6, column = 1)
Sensor_Connect_Status.grid(row = 6, column = 2)

Arduino_Connect_Label1 = Label(root, text = "Motors: ")
Arduino_Connect_Status = Label(root, text = "Not Connected")
Arduino_Connect_Label1.grid(row = 7, column = 1)
Arduino_Connect_Status.grid(row = 7, column = 2)


# fig = Figure(figsize = (5,5),dpi = 100)
# a = fig.add_subplot(111)

# canvas = FigureCanvasTkAgg(fig, master = root)
# canvas.draw()
# canvas.get_tk_widget().grid(row = 10, column = 0)


def main(): 
    # t1 = Thread(target = arduino_move, daemon=True)
    # t1.start()
    t2 = Thread(target = connect_sensor, daemon = True)
    t2.start() 

    #plot_sensor_data()

    root.mainloop()

if __name__ == "__main__": 
    main()