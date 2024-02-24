# Automated Pulse Sensing Tool
![APST_mainpic](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/7db9e12f-c4e8-4ade-9551-36984de9ae41) 

2021-2022 NDHU Undergraduate Project  
Group Members: Tyler Edwardo Eck  
Advisor: 顏士淨 (Shi-Jim Yen)  

## Introduction 
Automated Pulse Sensing Tool is a tool that allows users to measure their pulse with ease. With the simple push of a button, this tool will detect the pulse location on a person's wrist, move the sensor to that location, and record the TCM (Tradional Chinese Medicine) pulse readings. Finally, the results will be automatically uploaded to the cloud for remote doctors to observe.    

This project, including both the hardware and software, was exclusively developed and submitted as my final entry for the 2021 NDHU Undergraduate Project.      

Within the repository, you will find both the documentations for the project, including the presentations, poster, and research report, and the two main programs used together to control the tool. 

## Hardware 
The Automated Pulser Sensing Tool incorporates multiple hardware components that work together to give the tool its utlity. The following is what was used:     
     
### Creality CR10s 3D printer   
The recycled 3D printer was used as the main base for my project. It provides a main hand-rest area for patients with all the necessary motors and stop switches connected in an X,Y, and Z plane.     
<img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/7021c40f-edfb-4a27-9f45-f3bce4c0ff46" width="400" height="600">    

### HK-2019 Cylindrical Pusle Sensor 
This 200Hz pulse sensor measures both pulse and pressure for TCM pulse points.    
<img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/1999c11e-f49c-4a39-a711-4329ad45e313" width="400" height="600"> 

### StereoLabs ZED dual camera 
The camera was specifically chosen for its high frame rate and long-range 3D sensing.    
<img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/e9a5c995-fe23-446f-9f2c-9255a442313e" width="400" height="400"> 

### 3D-printed Component 
This 3D printed component was designed to mount the camera and sensors together for the motors to move.    
<img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/23438978-40ca-4a7b-ac9e-bb2a0250a925" width="700" height="600"> 

### Final Tool 
The completed hardware with all the subcomponents mentioned above is shown below.  
<img src="https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/7c66a8c6-3b81-4ec7-ac36-a21e7a821091" width="400" height="600"> 
    
## Software 
   
## Setup
The Automated Pulse Sensing Tool requires both the necessary software configurations and the physical tool available in order to sucessfully record and upload data. However, because the physical tool is property of the NDHU AI Lab, I can only include the software configurations to run the main python GUI program.    

In order to run the programs locally, follow the necessary steps below:    

1.  Download and install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) - Python 3.5 or 3.6
     
2.   Create an environment and download the necessary packages below using "conda install".   
     * Numpy 
     * Matplotlib
     * Tk - Tkinter 
     * Pillow - Image, ImageTk
     * OpenCv
     * Serial 
     * Mediapipe 
     * Pyrebase
   
3. Download and install [Arduino IDE](https://www.arduino.cc/en/software)
4. Download USB Driver for the HK2019 Pulse and Pressure Sensor - instructions and website found in "USB-- READ ME--" file in project. 
5. Upload "Motor_Movement" file to the Arduino Board using Arduino IDE. 
6. Run the main "APST_GUI" python file.

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




