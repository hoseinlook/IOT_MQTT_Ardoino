#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include "RfidDictionaryView.h"
#include "Servo.h"

// room/office settings
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");


int lights_on_time = -1;
int lights_off_time = -1;
int trigger = D0;
int echo = D1;
int distance6 = 45;
int led_5 = D2;
int lightMes = 100;
bool distance = false;

const char* BASE_ROOM_TOPIC = "login/rooms/1";
const char* OFFICE_TIME_TOPIC = "office";
const char* LIGHT_RESULT_TOPIC = "light/rooms/1";


// Update these with values suitable for your network.
const char* ssid = "Redmi";
const char* password = "12345678";
const char* mqtt_server = "192.168.246.119";

WiFiClient espClient;
bool tagSelected = false;
int startBlock = 18;  
RfidDictionaryView rfidDict(D4, D3, startBlock);

int servo_pin = D8;
bool isUserEntered;
Servo myservo;
int angle = 0;  

PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(200)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.flush();
}

void handleLight(char* input, int inputLength){
  StaticJsonDocument<128> doc;

  DeserializationError error = deserializeJson(doc, input, inputLength);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }

  int lightMes = doc["lightMes"]; 

  

  Serial.printf("light : %d", lightMes);
}

void handleServo() {
  // move from 180 to 0 degrees with a negative angle of 5
        for(angle = 180; angle>=1; angle-=5)
        {                                
          myservo.write(angle);
          delay(5);                       
        } 
}

void handleSetting(char* input, int inputLength){
  StaticJsonDocument<128> doc;

  DeserializationError error = deserializeJson(doc, input, inputLength);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }

  lights_on_time = doc["lightsOnTime"]; 
  lights_off_time = doc["lightsOffTime"];

  Serial.printf(" time: %d to %d \n", lights_on_time,lights_off_time);
  Serial.printf(" light: %d  \n", lightMes);

}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.printf("Message arrived [%s]\n", topic);
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  char* jsonBody = (char*) payload;

  if(!strcmp(topic,OFFICE_TIME_TOPIC)){
    handleSetting(jsonBody, length);
  }else if(!strcmp(topic,LIGHT_RESULT_TOPIC)){
    handleLight(jsonBody, length);
  }
}


void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.println("MQTT connection...");
    // Create a random client ID
    String clientId = "user1";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // ... and resubscribe
      client.subscribe(OFFICE_TIME_TOPIC);
      client.subscribe(LIGHT_RESULT_TOPIC);
    } else {
      Serial.printf("failed, rc=%d \n try again in 5 seconds", client.state());
      Serial.flush();
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void publishLoginCMD(char* card){
  StaticJsonDocument<128> doc;
  doc["card"] = card;
  serializeJson(doc, msg);
  client.publish(BASE_ROOM_TOPIC, msg);
}


void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  setup_wifi();
  pinMode(led_5, OUTPUT);
  pinMode(trigger, OUTPUT);
  pinMode(echo, INPUT);
  myservo.attach(servo_pin);
  timeClient.begin();
  timeClient.setTimeOffset(12600);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  do {
      long wave_duration;
      long point_distance;
      digitalWrite(trigger, LOW);  
      delayMicroseconds(2); 
      digitalWrite(trigger, HIGH);
      delayMicroseconds(10); 
      digitalWrite(trigger, LOW);
      wave_duration = pulseIn(echo, HIGH);
      // Serial.print("wave_duration :   ");
      // Serial.println(wave_duration);
      point_distance = (wave_duration/2) / 29.1;
      // Serial.print("point_distance :   ")  ;
      // Serial.println(point_distance);
      if (point_distance < distance6)
      {
        
        distance = true;
      }
      delay(20);
    } while (!distance);

  int ldr_result = 0;
  int map_result = 0;  
  ldr_result = analogRead(A0);
  map_result = map(ldr_result, 0, 1023, 0, 100);
  Serial.printf("   LDR %d .\n\n", map_result);


  byte tagId[4] = {0, 0, 0, 0};
  do {
      // returns true if a Mifare tag is detected
      tagSelected = rfidDict.detectTag(tagId);
      delay(5);
    } while (!tagSelected);
    Serial.printf("- TAG DETECTED, ID = %02X %02X %02X %02X \n", tagId[0], tagId[1], tagId[2], tagId[3]);
    Serial.printf("  space available for dictionary: %d bytes.\n\n", rfidDict.getMaxSpaceInTag());
  if (isUserEntered) {
    publishLoginCMD("m");
    isUserEntered = false;
     handleServo();
     digitalWrite(led_5, LOW);    
  }else {
    publishLoginCMD("m");
    isUserEntered = true;
    int currentHour = timeClient.getHours();
    if (currentHour > lights_on_time && currentHour < lights_off_time ) {
      //digitalWrite(led_5, HIGH);
      handleServo();
    }
    //digitalWrite(led_5, HIGH);
    analogWrite(led_5, lightMes);
    Serial.print("sending");
    handleServo();
  }
  tagSelected = false;
  distance = false;
}