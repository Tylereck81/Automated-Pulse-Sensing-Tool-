# Automated Pulse Sensing Tool

2021-2022 NDHU Undergraduate Project  
Group Members: Tyler Edwardo Eck  
Advisor: 顏士淨 (Shi-Jim Yen)  

## Introduction 
Automated Pulse Sensing Tool is a tool that allows for users to measure their pulse with ease. Both the hardware and software were exclusively developed for the purpose of the NDHU Undergraduate Project.    

Within the repository, you will find both the documentations for the project, including the presentations, poster, and research report, and the two main programs used together to control the tool. 

## Setup
In order to run the programs locally, follow the necessary steps below.

1.  Download and install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) - Python 3.5 or 3.6
     
3.  Create an environment and download the necessary packages below. 
    * Numpy 
    * Matplotlib
    * Tk - Tkinter 
    * Pillow - Image, ImageTk
    * OpenCv
    * Serial 
    * Mediapipe 
    * Pyrebase
   
4. Download and install [Arduino IDE](https://www.arduino.cc/en/software)
5. Download USB Driver HK2019 Pulse and Pressure Sensor - instructions and website found in "USB-- READ ME--" file in project. 
6. Upload "Motor_Movement" file to the Arduino Board using Arduino IDE. 
7. Run the main "APST_GUI" python file.

## Instructions
In order to run the program, make sure the pulse sensor, arduino, and camera are all connected via USB and the computer recongizes them. 

