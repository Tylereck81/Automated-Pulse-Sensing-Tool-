#Tyler Eck 
#Automated Pulse Sensing Tool 
#3rd Year Undergraduate Project 

from tkinter import * 
from serial import Serial
import time 
import serial.tools.list_ports 
from threading import *

current_pos = [0,0,0]
MAX_X = 100
MAX_Y = 100
MAX_Z = 100

#Main Page 
root = Tk()

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
    if current_pos[2]>=0: 
        current_pos[2]+=10
        if current_pos[2]>=MAX_Z:
            current_pos[2] = MAX_Z

    else:
        current_pos[2] = 0
    
    print(current_pos)
        
def move_Down():
    if(current_pos[2]>=0): 
        current_pos[2]-=10
        if current_pos[2] <0: 
            current_pos[2] = 0
    else:
        current_pos[2] = 0
    
    print(current_pos)

def move_Left():
    if(current_pos[0]>=0): 
        current_pos[0]-=10
        if current_pos[0] < 0: 
            current_pos[0] = 0
    else:
        current_pos[0] = 0
    
    print(current_pos)

def move_Right():
    if current_pos[0]>=0: 
        current_pos[0]+=10
        if current_pos[0]>=MAX_X:
            current_pos[0] = MAX_X

    else:
        current_pos[0] = 0
    
    print(current_pos)


def threading(): 
    t1 = Thread(target = arduino_listen, daemon=True)
    t1.start()

def arduino_listen(): 
    #Connect to Arduino 
    arduino = Serial(port='COM3', baudrate= 115200, timeout = .1) 
    def write_read(x): 
        print(x)
        arduino.write(bytes(x,'utf-8'))
        time.sleep(0.05) 
        data = arduino.readline() 
        return data 
    while True: 
        time.sleep(1)
        num = change_to_str(str(current_pos))
        value = write_read(num)
    
run = True
Up= Button(root, text = "Up",padx = 10, pady = 10, command = move_Up)
Down= Button(root, text = "Down",padx = 10, pady = 10, command = move_Down)
Left= Button(root, text = "Left",padx = 10, pady = 10, command = move_Left)
Right= Button(root, text = "Right",padx = 10, pady = 10, command = move_Right)

Up.grid(row = 0, column = 3)
Down.grid(row =4, column = 3)
Left.grid(row = 2, column = 0)
Right.grid(row = 2, column = 4)

threading()
root.mainloop()
run = False 