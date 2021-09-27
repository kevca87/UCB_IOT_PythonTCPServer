#include <WiFi.h>

const int ECHO_PIN = 4;
const int TRIGGER_PIN = 5;
 
const int LED_RED_PIN = 13;
const int LED_YELLOW_PIN = 0;
const int LED_GREEN_PIN = 4;
 
//This allows extense the number of LEDs

const String leds_names[3] = {"red","yellow","green"};
const int leds_pins[3] = {LED_RED_PIN, LED_YELLOW_PIN, LED_GREEN_PIN};

const char* WIFI_SSID = "HUAWEI-2.4G-M6xZ";
const char* WIFI_PASS = "HT7KU2Xv";

const char* SERVER_ADDRESS = "192.168.100.76";
const int SERVER_PORT = 12345;

void sendLedsDict(WiFiClient client)
{
  Serial.println("Enter sendLedsDict");
  String message = "{";
  //ERROR HERE
  for (int i=0;i<3;i++)
  {
    message = message + leds_names[i] +":"+String(leds_pins[i]);
    if (i<2)
      message = message+",";
  }
  message = message + "}";
  Serial.println(message);
  client.println(message);
}
void sendClosingConnection(WiFiClient client)
{
  client.println("closing connection");
}



IPAddress connectLocalWiFi(const char* ssid,const char* password)
{
  Serial.print("Connecting to: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while ( WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  return WiFi.localIP();
}

long readUltrasonicDistance(int triggerPin, int echoPin){
  pinMode(triggerPin, OUTPUT);  // Clear the trigger
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  // Sets the trigger pin to HIGH state for 10 microseconds
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  // Reads the echo pin, and returns the sound wave travel time in microseconds
  return pulseIn(echoPin, HIGH);
}

int sendDistance(WiFiClient client){
  // measure the ping time in cm
  int distance = 0.01723 * readUltrasonicDistance(TRIGGER_PIN,  ECHO_PIN);
  client.println(distance);
  return distance;
}

WiFiClient client;

void setup() {
  Serial.begin(115200);
  IPAddress ipClient = connectLocalWiFi(WIFI_SSID,WIFI_PASS);
  Serial.print("Client (MCU) IP Address: ");
  Serial.println(ipClient);
  Serial.print("Connecting to address: ");
  Serial.println(SERVER_ADDRESS);
  Serial.print("In port: ");
  Serial.println(SERVER_PORT);
  while (client.connect(SERVER_ADDRESS, SERVER_PORT) != 1) {
    Serial.println("Connection failed");
    delay(10000);
  }
}

void loop() {
  if (client.available())
  {
    String line = client.readStringUntil('\n');
    Serial.println(line);
    Serial.println(line.length());
    if (line == "get_leds_dict")
    {
      sendLedsDict(client);
    }
    else if (line == "get_distance")
    {
      sendDistance(client);
    }
    if (line == "close")
    {
      sendClosingConnection(client);
      client.stop();
    }
  }
  if (!client.connected())
  {
    client.stop();
    Serial.println("MCU Disconnected");
    Serial.print("Reconnect? [y/n]:");
    String ans = Serial.readStringUntil('\n');
    if (ans == "y")
    {
      while (client.connect(SERVER_ADDRESS, SERVER_PORT) != 1) {
        Serial.println("Connection failed");
        delay(10000);
      }
    }
    else
    {
      delay(5000);
    }
  }
}
