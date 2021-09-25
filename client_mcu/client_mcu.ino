#include <WiFi.h>

const char* WIFI_SSID = "HUAWEI-2.4G-M6xZ";
const char* WIFI_PASS = "HT7KU2Xv";

const char* SERVER_ADDRESS = "192.168.100.76";
const int SERVER_PORT = 12345;

void setup() {
  Serial.begin(115200);

  Serial.print("Connecting to: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while ( WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }

  Serial.print("Local IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  Serial.print("Connecting to: ");
  Serial.println(SERVER_ADDRESS);

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
