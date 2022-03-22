#include <SpeedyStepper.h>

//X Stepper
const int STEP_PIN_X = 54; 
const int DIR_PIN_X = 55;
const int ENABLE_PIN_X = 38; 
const int MIN_PIN_X = 3;
const int MAX_PIN_X = 2;
SpeedyStepper x_stepper;

//Y Stepper  
const int STEP_PIN_Y = 60;
const int DIR_PIN_Y = 61; 
const int ENABLE_PIN_Y = 56; 
const int MIN_PIN_Y = 14;
const int MAX_PIN_Y = 15;
SpeedyStepper y_stepper;

//Z Stepper 
const int STEP_PIN_Z = 46;
const int DIR_PIN_Z = 48;
const int ENABLE_PIN_Z = 62; 
const int MIN_PIN_Z = 18;
const int MAX_PIN_Z = 19;
SpeedyStepper z_stepper;


//Max Millimeter(mm) values that can be applied (300,280,245)
const int MAX_X_VALUE = 280; 
const int MAX_Y_VALUE = 280; 
const int MAX_Z_VALUE = 245; 

//MIDDLE FOR SENSOR: 150,140,245 


//void move_stepper(int x,int y, int z){ 
//    x_stepper.moveToPositionInSteps(-x);
//    y_stepper.moveToPositionInSteps(-y);
//    z_stepper.moveToPositionInSteps(-z);
//}
//
//void move_home(){ 
//  x_stepper.moveToHomeInSteps(-1,600,100000,MIN_PIN_X);
//  y_stepper.moveToHomeInSteps(-1,600,100000,MIN_PIN_Y);
//  z_stepper.moveToHomeInSteps(1,600,100000,MIN_PIN_Z);
//}


void mm_move_stepper(int x,int y, int z){ 
  if(x>MAX_X_VALUE){
   x = MAX_X_VALUE;
  }
  if(y>MAX_Y_VALUE){ 
    y = MAX_Y_VALUE;
  }
  if(z>MAX_Z_VALUE){ 
    z = MAX_Z_VALUE;
  }
  z_stepper.moveToPositionInMillimeters(z);
  x_stepper.moveToPositionInMillimeters(-x);
  y_stepper.moveToPositionInMillimeters(-y);
  

}

void mm_move_home(){
  x_stepper.moveToHomeInMillimeters(-1,5,100000,MIN_PIN_X);
  y_stepper.moveToHomeInMillimeters(-1,5,100000,MIN_PIN_Y);
  z_stepper.moveToHomeInMillimeters(1,5,100000,MIN_PIN_Z);
  
}

int x1; 
int y1; 
int z1; 

int Position[3];
void setup() {
  Serial.begin(115200); //communication
  Serial.setTimeout(1); 



  //Sets Enable pins to Low 
  pinMode(ENABLE_PIN_X,OUTPUT); 
  digitalWrite(ENABLE_PIN_X,LOW);
  x_stepper.connectToPins(STEP_PIN_X, DIR_PIN_X);  //connects step and direction pins X

  pinMode(ENABLE_PIN_Y,OUTPUT); 
  digitalWrite(ENABLE_PIN_Y,LOW);
  y_stepper.connectToPins(STEP_PIN_Y, DIR_PIN_Y);  //connects step and direction pins Y

  
  pinMode(ENABLE_PIN_Z,OUTPUT); 
  digitalWrite(ENABLE_PIN_Z,LOW);
  z_stepper.connectToPins(STEP_PIN_Z, DIR_PIN_Z);  //connects step and direction pins Z

  x_stepper.setStepsPerMillimeter(85);
  x_stepper.setSpeedInMillimetersPerSecond(30);
  x_stepper.setAccelerationInMillimetersPerSecondPerSecond(30); 
  
  y_stepper.setStepsPerMillimeter(85);
  y_stepper.setSpeedInMillimetersPerSecond(30);
  y_stepper.setAccelerationInMillimetersPerSecondPerSecond(30); 

  z_stepper.setStepsPerMillimeter(400);
  z_stepper.setSpeedInMillimetersPerSecond(30);
  z_stepper.setAccelerationInMillimetersPerSecondPerSecond(30); 
  
//  x_stepper.setSpeedInStepsPerSecond(5000); 
//  x_stepper.setAccelerationInStepsPerSecondPerSecond(5000);
//  y_stepper.setSpeedInStepsPerSecond(5000); 
//  y_stepper.setAccelerationInStepsPerSecondPerSecond(5000);
//  z_stepper.setSpeedInStepsPerSecond(5000); 
//  z_stepper.setAccelerationInStepsPerSecondPerSecond(5000);

//  mm_move_home();
//  //mm_move_stepper(300,280,345); //MAX S
//  mm_move_stepper(150,140,172); //HALF 
//  mm_move_home(); 

mm_move_home();

}

bool newData = false;
char t[15]={'\0'};
int c = 0;
void recieve(){ 
  char endMarker =')';
  char begMarker='(';
  char rc; 
  while(Serial.available() > 0 && newData == false){ 
    rc = Serial.read(); 

    if(rc!= endMarker){
      if(rc!=begMarker){
        t[c] = rc; 
        c++; 
      }
    }
    else{ 
      t[c] = '\0';
      c = 0; 
      newData = true;
    }
  }
}

void showData(){ 
  if(newData == true){
    Serial.println(t);
    newData = false;
  }
}


void loop() {
  
 recieve(); 
 showData();
 
  int c = 0; 
  int Posi = 0;
  int i = 0;
  while(c!=3){ 
    String temp =""; 
    while(t[i]!=','){
      temp+=t[i];
      i++; 
     }
     i++;
     Position[Posi] = temp.toInt();
     Posi++;
     c++;
  }


  mm_move_stepper(Position[0],Position[1],Position[2]); 
  
}
