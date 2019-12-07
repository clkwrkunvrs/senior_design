// Include the Arduino Stepper Library/*
#include <Stepper.h>

// Number of steps per output rotation
const int stepsPerRevolution = 100;
boolean newData = false;
//int numTimes = 0;

// Create Instance of Stepper library
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);



void setup()
{
  // set the speed at 60 rpm:
  myStepper.setSpeed(60);
  // initialize the serial port:
  Serial.begin(9600);
  
}

void loop() 
{
  //myStepper.step(-5);
  recvOneChar();
  processData();
  //releaseTrigger();
  //if(newData = false){
  //myStepper.step(100);
  //delay(500);
  //}
}
  void recvOneChar() {
  if (Serial.available() > 0) {
    newData = true;
   }
  }

  void processData(){
    if(newData == true) {
      char incomingData = Serial.read();
      Serial.println("incoming data is: " + incomingData);
      //Serial.write("incoming data is: " + incomingData);
      if(incomingData == '1'){
      Serial.println("received char. pulling trigger");
      myStepper.step(-stepsPerRevolution);
      delay(500);
     // launched = true;
      //Serial.end();
      newData = false;
      }
     else if(incomingData == '2'){
      Serial.println("releasing trigger");
      myStepper.step(+stepsPerRevolution);
     
      delay(500);
      Serial.println("trigger released");
      newData = false;
      //numTimes++;
      //if(numTimes == 3){
      //  Serial.write("done");
        //delay(500);
      //}
      
     }
     else if(incomingData == '3'){
      exit(0);
     }
      
      
  
      
    /*  pinMode(8, OUTPUT);
      pinMode(9, OUTPUT);
      pinMode(10, OUTPUT);
      pinMode(11, OUTPUT);
      //counterclockwise
      int cClkwise = 0;
      while(cClkwise > -76){
      switch (cClkwise % 4) {
      case 0:  // 1010
        digitalWrite(8, HIGH);
        digitalWrite(9, LOW);
        digitalWrite(10, HIGH);
        digitalWrite(11, LOW);
      break;
      case 1:  // 0110
        digitalWrite(8, LOW);
        digitalWrite(9, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(11, LOW);
      break;
      case 2:  //0101
        digitalWrite(8, LOW);
        digitalWrite(9, HIGH);
        digitalWrite(10, LOW);
        digitalWrite(11, HIGH);
      break;
      case 3:  //1001
        digitalWrite(8, HIGH);
        digitalWrite(9, LOW);
        digitalWrite(10, LOW);
        digitalWrite(11, HIGH);
      break;
      cClkwise--;
    }
   }
   delay(500);
   int clkwise = 0;
   while(clkwise < 50){
          switch (clkwise % 4) {
      case 0:  // 1010
        digitalWrite(8, HIGH);
        digitalWrite(9, LOW);
        digitalWrite(10, HIGH);
        digitalWrite(11, LOW);
      break;
      case 1:  // 0110
        digitalWrite(8, LOW);
        digitalWrite(9, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(11, LOW);
      break;
      case 2:  //0101
        digitalWrite(8, LOW);
        digitalWrite(9, HIGH);
        digitalWrite(10, LOW);
        digitalWrite(11, HIGH);
      break;
      case 3:  //1001
        digitalWrite(8, HIGH);
        digitalWrite(9, LOW);
        digitalWrite(10, LOW);
        digitalWrite(11, HIGH);
      break;
      cClkwise++;
    }
   }
  }*/

      //Serial.end();
      //Serial.begin(9600);

      
   // }
  }
  }

  /*void releaseTrigger(){
    if(newData){
        Serial.println("releasing trigger");
      //myStepper.step(stepsPerRevolution);
      //delay(500);
      //Serial.flush();
      myStepper.step(+stepsPerRevolution);
     
      delay(500);
      Serial.println("trigger released");
      newData = false;;
    }
  }*/
  
