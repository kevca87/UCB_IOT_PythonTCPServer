#include <WiFi.h>

const char* WIFI_SSID = "HUAWEI-2.4G-M6xZ";
const char* WIFI_PASS = "HT7KU2Xv";

const char* SERVER_ADDRESS = "192.168.100.76";
const int SERVER_PORT = 12345;


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

void setup() {
  Serial.begin(115200);
  IPAddress ipClient = connectLocalWiFi(WIFI_SSID,WIFI_PASS);
  Serial.print("Client (MCU) IP Address: ");
  Serial.println(ipClient);
}

void loop() {
  Serial.print("Connecting to address: ");
  Serial.println(SERVER_ADDRESS);
  Serial.print("In port: ");
  Serial.println(SERVER_PORT);

  WiFiClient client;

  if (!client.connect(SERVER_ADDRESS, SERVER_PORT)) {
    Serial.println("Connection failed");
    delay(10000);
    return;
  }

  client.println("GET TIME");

  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 10000) {
      Serial.println("Server didn't answer");
      client.stop();
      delay(10000);
      return;
    }
    delay(10);
  }

  if (client.available() > 0) {
    String line = client.readStringUntil('\n');
    Serial.println(line);
  }
  
  Serial.println("Closing Connection");

  client.stop();
  delay(10000);
}
