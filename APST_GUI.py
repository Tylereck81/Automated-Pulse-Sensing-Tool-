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
import serial.tools.list_ports

current_pos = [0,0,0]
old_pos =[0,0,0]
MAX_X = 100
MAX_Y = 100
MAX_Z = 100
global STOP_SCAN
STOP_SCAN = 0


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
    #global current_pos
    if current_pos[2]>=0: 
        current_pos[2]+=10
        if current_pos[2]>=MAX_Z:
            current_pos[2] = MAX_Z

    else:
        current_pos[2] = 0
    
    #print(current_pos)
        
def move_Down():
   # global current_pos
    if(current_pos[2]>=0): 
        current_pos[2]-=10
        if current_pos[2] <0: 
            current_pos[2] = 0
    else:
        current_pos[2] = 0
    
    #print(current_pos)

def move_Left():
    #global current_pos
    if(current_pos[0]>=0): 
        current_pos[0]-=10
        if current_pos[0] < 0: 
            current_pos[0] = 0
    else:
        current_pos[0] = 0
    
    #print(current_pos)

def move_Right():
   # global current_pos
    if current_pos[0]>=0: 
        current_pos[0]+=10
        if current_pos[0]>=MAX_X:
            current_pos[0] = MAX_X

    else:
        current_pos[0] = 0
    
    #print(current_pos)


def arduino_move(): 
    #Connect to Arduino and send the position to move to 
    arduino = Serial(port='COM3', baudrate= 115200, timeout = .1)

    #only does movement when there is a difference in position (when button is pressed)
    while True: 
        global old_pos
        global current_pos
        if old_pos != current_pos:
            num = change_to_str(str(current_pos))
            old_pos = deepcopy(current_pos)
            print(num)
            arduino.write(bytes(num,'utf-8'))
            time.sleep(0.05)
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

def stop_scan(): 

    #Set stop flag to true
    global STOP_SCAN
    STOP_SCAN = 1



def sensor_read():
    sensor = Serial(port='COM5', baudrate = 256000, bytesize = 8, timeout = 2,stopbits=serial.STOPBITS_ONE)
    sensor.write([0xF0, 0x2F, 0x01, 0x32])

    # while True: 
    #     serialString = sensor.readline() 
    #     n =[] 
    #     for i in serialString: 
    #         n.append(i)
    #         if len(n) == 9: 
    #             print(n)
    #             n=[]
    #     if STOP_SCAN: 
    #         break

    global STOP_SCAN
    while True: 
        serialString = sensor.readline() 
        print(serialString)
        if STOP_SCAN: 
            break 

    sensor.write([0xF0, 0x2F, 0x01, 0x33])
    print('Scan Ended')




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


def main(): 
    #t1 = Thread(target = arduino_move, daemon=True)
    #t1.start()
    root.mainloop()

if __name__ == "__main__": 
    main()
