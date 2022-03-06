#Tyler Eck 
#Automated Pulse Sensing Tool 
#3rd Year Undergraduate Project 

from tkinter import * 
from serial import Serial
import time 

#Main Page 
root = Tk()

myLabel = Label(root, text = "Hello World") 

myLabel.pack()


root.mainloop()


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


