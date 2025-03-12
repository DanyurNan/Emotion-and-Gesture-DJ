
#include <MPU6050_light.h>
#include <Wire.h>
#include <WiFi.h>


//constants for wifi connection
const char* ssid = *********;
const char* password = **********;
WiFiServer server(10000);

const int thres = 220;

struct __attribute__((packed)) Data {
  int16_t seq;
  int32_t distance;
  float voltage;
  char text[50];
} data;

//declares all sensors
MPU6050 mpu[6] {
  MPU6050(Wire),
  MPU6050(Wire),
  MPU6050(Wire),
  MPU6050(Wire),
  MPU6050(Wire),
  MPU6050(Wire),
};

//lists the pins that each sensor connects to
const int AD0pin[6] = {23, 19, 18, 17, 16, 15};

//sets up each sensor to detect movement, indicates if a chip is connected or not
void set_sensors() {
  Serial.println("Connecting six MPU6050 chips:");
  Wire.begin();
  
  for (int i=0; i<6; i++) {
    pinMode(AD0pin[i],OUTPUT);
    digitalWrite(AD0pin[i],HIGH);
  }

  for (int i=0; i<6; i++) {
    SelectMPU(i);
    if (!mpu[i].begin()) {
      Serial.print("Found MPU6050 chip #");
      int j = i + 1;
      Serial.print(j);
      Serial.println("");
    }
    else if (mpu[i].begin()) {
      Serial.print("Failed to find MPU6050 chip #");
      int j = i + 1;
      Serial.print(j);
      Serial.println("");
    }
  }
}

//initializes wifi connection and sensor setup
void setup(void) {
  Serial.begin(115200);
  set_sensors();
  Serial.println("");
  delay(100);

  //connects to the wifi connection specified at the start
  Serial.printf("Connecting to %s\n", ssid);
  Serial.printf("\nattempting to connect to WiFi network SSID '%s' password '***********' \n", ssid, password);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  server.begin();
  printWifiStatus();
  Serial.println(" listening on port 10000");
}

void loop() {
  //waits until client connects to the port
  WiFiClient client = server.available();

  //initializes arrays to track the movement of each finger and swipes
  bool pressed[6] = {0, 0, 0, 0, 0, 0};
  bool swiped[3] = {0,0,0};

  //once client is connected, the glove begins to track rotational and acceration movements of each sensor, 
  //which get sent to the client as a print statement in real time once a threshold is reached
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {

      //uses the sensor on the palm to detect swipe sensors
      SelectMPU(5);
      mpu[5].update();

      //detects a swipe to the right
      if (mpu[5].getAccX() > 0.3){
        if (!swiped[0]){
          client.printf("swipe right");
          swiped[0] = 1;
        }
        else if (swiped[1]) {
          swiped[1] = 0;
        }
      }

      //detects a swipe to the left
      else if (mpu[5].getAccX() < -0.3) {
        if (swiped[0]) {
          swiped[0] = 0;
        }
        else if (!swiped[1]){
          client.printf("swipe left");
          swiped[1] = 1;
        }
      }

      //detects a swipe forward
      if (!swiped[2] && mpu[5].getAccY() < -0.3){
        client.printf("swipe forward");
        swiped[2] = 1;
      }
      else if (swiped[2] && mpu[5].getAccY() > 0.3){
        swiped[2] = 0;
      }
      
      //checks each finger for a rotational movement
      for (int i=0; i<5; i++) {
        SelectMPU(i);
        mpu[i].update();

        //if a sensor is 0 on all axes consistently, then the sensor is disconnected
        if ((mpu[i].getGyroX() == -0.00 || mpu[i].getGyroX() == -0.02) && (mpu[i].getGyroY() == -0.00 || mpu[i].getGyroY() == -0.02))
        {
          client.printf("disconnected %d\n", i);
          delay(1000);
        }
        
        //detects a finger rotation using the gyroscope acceleration detection
        //if the rotation speed is above a threshold, the finger number is sent to the client
        //no more information is sent to the client until the finger stops moving
        if (!pressed[i] && mpu[i].getGyroY()-mpu[5].getGyroX() > thres){
          client.printf("press %d\n", i);
          pressed[i] = 1;
        }
        else if (pressed[i] && mpu[i].getGyroY()-mpu[5].getGyroX() < 0)
        {
          pressed[i] = 0;
        }
        
        //checks for any messages to the server requesting a reset to the sensors
        //important if any sensors are disconnected
        //if true the sensors are set up again
        if (client.available()) {
          char c = client.read();
          if (c == 'r')
          {
            set_sensors();
          }
        }
      }
    }

    //if the client disconnects, the server waits again for the client to reconnect
    client.stop();
    Serial.println("Client disconnected");
  }
}
    
//prints any information regarding wifi connection
void printWifiStatus() {
  Serial.print("\nSSID: ");
  Serial.println(WiFi.SSID());

  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

//helper to select each sensor to check for movement
void SelectMPU(int selection) {
  for (int i=0; i<6; i++) {
    if(i == selection) {
      digitalWrite(AD0pin[i],LOW);
    }
    else {
      digitalWrite(AD0pin[i],HIGH);
    }
  }
}