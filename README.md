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
The Automated Pulse Sensing Tool incorporates multiple hardware components that work together to give the tool its utility. The following is what was used:     
     
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
The Automated Pulse Sensing Tool needs software to move step motors through Arduino and a Python program to communicate with Arduino and process motor movement. The Python program also acts as the main GUI that patients and doctors will interact with. Therefore, in the Hardware/Arduino folder, the "Motor_Movement.ino" is used to move the motors and in the Software GUI folder, "APST_GUI.py" is the main python program.     
     
The APST_GUI.py was designed and implemented using Tkinter, a package in the standard Python interface GUI toolkit. As shown in diagram below, the GUI consists of 4 main parts: 

![label](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/1106bd83-472a-4207-bcf6-bb4885bace6d)

1. Camera - shows users a live feed of the camera and its detection of the pulse point.   
     
2. Options - controls motors manually with arrows and step selection, controls initiation of scan, and displays connection information regarding the pulse sensors, motors, and camera.  
   
3. Graph - displays the graph of the pulse that was taken.    
   
4. Information - allows users to enter additional information about the graph including name, date, and description (optional). This section also includes the Upload button that is necessary to send data via Firebase to the cloud.    
   

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
In order to run the program successfully, ensure the pulse sensor, arduino, and camera are all connected via USB and the computer recongizes them.
 
The two modes that are available are Manual and Automatic. Manual is selected by default.    

 * ### Manual 
Manual mode is intended for doctors to use as they are given the choice to manually move the motors and start scan when desired. The following steps are the sequence that doctors can follow:
     
1. The motor movement is initiated through the Options menu shown below. The sensor can be moved on the X and Z axis by through the Sensor movement arrows. The base, where the patients hand would lay, can also be moved on the Y axis through the Base movement arrows. Lastly, the doctors can manually control the steps that the motors can take for a given click of the arrow. By adjusting the Steps slider, each movement can be shortened or lengthened.      
          
![op](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/3f8427ec-a958-49d3-9566-4a1b7b5ed9b6)      
     
2. After a desired location is reached, the doctor can activate the detection algorithm, through the "Detect" button in the Camera section, to determine if the location of the pulse point is in the blue circle; this blue circle displays the exact point where the sensor will read. The "Stop" button is used to freeze the frame so that the doctor may have a chance to click on the point that the sensor should move to. Clicking the point activates the motor movement to have the sensor move directly beneath the selected pulse point.       
     
![1](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/8e33864a-cfa2-4696-87d3-e983259f9440)        
      

3. When ready to scan, the "Scan" button in the Options menu should be pressed. A seperate screen will pop up to indicate the scan is taking place. When finished, the "Stop" button should then be pressed to stop the scan. To see a more detailed version of the recorded graph, the "Open Graph" button in the graph section can be pressed. To "cut" or record a subsection of the graph, the mouse's left click is used to select start point and right click to select end point.
      
![g5](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/956422ad-716f-4c8b-82a9-406ccc4ea8ad)
       
![g2](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/7231f721-8171-490c-84c2-4a7b8fdc48fe)
     
5.  Lastly, information about the patient can be entered in text area and uploaded by pressing the Upload button.    
     
![u5](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/6c2e573e-1401-4894-9b03-9cc71fee144b)
   

* ### Automatic
Automatic mode is intended for patients to use and includes user-friendly instructions that patients should read carefully. 

1. When the Automatic button is pressed in the Options section, a seperate instruction screen will appear for users to read. These instructions include different warnings and proper hand form for an accurate scan.    

![1](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/bfa68db8-5e1d-45ad-8478-ce273fc280b5)     
         
![2](https://github.com/Tylereck81/Automated-Pulse-Sensing-Tool-/assets/68008817/47e711e4-57dd-4913-9034-ab0a4878e674)      

2. After the instructions have been read, the "Finish" button will be enabled to press which starts the automation process. The tool will automatically detect the pulse point, select the pulse point, move motors to that point, and scan for 30 seconds. When finished, the patient will be prompted to enter information and then press the "Upload" button as shown in the Manual section. 






