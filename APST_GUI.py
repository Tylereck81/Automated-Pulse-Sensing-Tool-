#Tyler Eck 
#Automated Pulse Sensing Tool 
#3rd Year Undergraduate Project 

from tkinter import * 
from serial import Serial
import time 
import serial.tools.list_ports 

current_pos = [0,0,0]
MAX_X = 100; 
MAX_Y = 100; 
MAX_Z = 100;

#Main Page 
root = Tk()


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


Up= Button(root, text = "Up",padx = 10, pady = 10, command = move_Up)
Down= Button(root, text = "Down",padx = 10, pady = 10, command = move_Down)
Left= Button(root, text = "Left",padx = 10, pady = 10, command = move_Left)
Right= Button(root, text = "Right",padx = 10, pady = 10, command = move_Right)

Up.grid(row = 0, column = 3)
Down.grid(row =4, column = 3)
Left.grid(row = 2, column = 0)
Right.grid(row = 2, column = 4)




#Connect to Arduino 
arduino = Serial(port='COM3', baudrate= 115200, timeout = .1) 
def write_read(x): 
    arduino.write(bytes(x,'utf-8'))
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 
while True: 
    num = input("Enter a number: ")
    value = write_read(num) 
    print(value)

root.mainloop()
