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
    
    #print(current_pos)
        
def move_Down():
    if(current_pos[2]>=0): 
        current_pos[2]-=10
        if current_pos[2] <0: 
            current_pos[2] = 0
    else:
        current_pos[2] = 0
    
    #print(current_pos)

def move_Left():
    if(current_pos[0]>=0): 
        current_pos[0]-=10
        if current_pos[0] < 0: 
            current_pos[0] = 0
    else:
        current_pos[0] = 0
    
    #print(current_pos)

def move_Right():
    if current_pos[0]>=0: 
        current_pos[0]+=10
        if current_pos[0]>=MAX_X:
            current_pos[0] = MAX_X

    else:
        current_pos[0] = 0
    
    #print(current_pos)

#moves the position based on which button was pressed and then creates
# a thread to connect to the arduino and move the motor 
def threading(n): 
    if n == 1: # move up
        move_Up()
    elif n == 2: #move down
        move_Down()
    elif n == 3: #move left 
        move_Left()
    elif n == 4: #move right
        move_Right()
    
    t1 = Thread(target = arduino_move, daemon=True)
    t1.start()


def arduino_move(): 
    #Connect to Arduino and send the position to move to 
    arduino = Serial(port='COM3', baudrate= 115200, timeout = .1) 
    num = change_to_str(str(current_pos))
    arduino.write(bytes(num,'utf-8'))
    time.sleep(0.05)


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

#Buttons for Manual movement of motors
Up = Button(root, text = "Up",padx = 10, pady = 10, command = lambda: threading(1))
Down = Button(root, text = "Down",padx = 10, pady = 10, command = lambda: threading(2))
Left = Button(root, text = "Left",padx = 10, pady = 10, command = lambda: threading(3))
Right = Button(root, text = "Right",padx = 10, pady = 10, command = lambda: threading(4))

Automatic_Button.grid(row = 1, column = 1)
Manual_Button.grid(row = 1, column = 2)
Up.grid(row = 2, column = 2)
Down.grid(row =4, column = 2)
Left.grid(row = 3, column = 1)
Right.grid(row = 3, column = 3)

root.mainloop()