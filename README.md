# Automated Pulse Sensing Tool

2021-2022 NDHU Undergraduate Project  
Group Members: Tyler Edwardo Eck  
Advisor: 顏士淨 (Shi-Jim Yen)  

## Introduction 
Automated Pulse Sensing Tool is a tool that allows for users to measure their pulse with ease. Both the hardware and software were exclusively developed for the purpose of the NDHU Undergraduate Project.    

Within the repository, you will find both the documentations for the project, including the presentations, poster, and research report, and the two main programs used together to control the tool. 

## Setup
In order to run the programs locally, follow the necessary steps below:

1.  Download and install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) - Python 3.5 or 3.6
     
3.  Create an environment and download the necessary packages below using "conda install".
    * Numpy 
    * Matplotlib
    * Tk - Tkinter 
    * Pillow - Image, ImageTk
    * OpenCv
    * Serial 
    * Mediapipe 
    * Pyrebase
   
4. Download and install [Arduino IDE](https://www.arduino.cc/en/software)
5. Download USB Driver for the HK2019 Pulse and Pressure Sensor - instructions and website found in "USB-- READ ME--" file in project. 
6. Upload "Motor_Movement" file to the Arduino Board using Arduino IDE. 
7. Run the main "APST_GUI" python file.

If all steps were properly executed, the main GUI screen will appear as shown below.

<p align="center">
  <img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/blob/main/Software-GUI/automatic_mode_instructions/s2.png">
</p>


## Instructions
In order to run the program, make sure the pulse sensor, arduino, and camera are all connected via USB and the computer recongizes them.   
  
The two modes that are available are Manual and Automatic. Manual is selected by default. 

 * ### Manual 
     - Intended mode for the doctor. The detect button should first be used to activate the detection algorithm when hand is placed in camera view. The stop button is to freeze the frame so that the user may have a chance to select the point. Clicking the point activates the motor movement to have the sensor move directly beneath the selected pulse point. Sensor Arrow Motors, shown in the Options section, should then be used to move motors down to point manually. When ready to scan, the Scan button should then be pressed. A screen, recording and graphing live data pulse points, will pop up to indicate the scan is taking place. When finished, the Stop button should then be pressed to stop the scan. Edit Graph button can be pressed to select a subset of the graph; left click to select start point and right click to select end point. Lastly, information about the patient can be entered in text area and uploaded by pressing the Upload button. 


* ### Automatic
     - Intended mode for patient. When the Automatic button is pressed in the Options section, a user-friendly instruction screen will pop up for users to read. After instructions have been read, the finish button will be enabled to press. Automation will start 5 seconds after the Finish button is pressed. The tool will automatically detect the pulse point, select the pulse point, move motors to that point, and scan for 30 seconds. When finished, the user will have to press the Stop Scan button and enter information to be uploaded. 




