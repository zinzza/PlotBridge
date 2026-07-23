// ponytail: force SPIFFS format for WiFiManager persistence
#include <WiFi.h>
#include <WiFiManager.h>
#include <SPIFFS.h>

void setup() {
    SPIFFS.begin(true); // ponytail: format if needed
    pinMode(8, OUTPUT);
    for (int i = 0; i < 3; i++) { digitalWrite(8, LOW); delay(200); digitalWrite(8, HIGH); delay(200); }
    for (int d = 0; d <= 255; d += 5) { analogWrite(5, d); delay(15); }
    for (int i = 0; i < 5; i++) { digitalWrite(8, LOW); delay(100); digitalWrite(8, HIGH); delay(100); }
    WiFiManager wm;
    Serial.begin(115200);Serial.println("autoConnect..."); // ponytail: debug
    wm.autoConnect("PlotBridge");
    Serial.println("done");
    digitalWrite(8, LOW);
}
void loop() {}
