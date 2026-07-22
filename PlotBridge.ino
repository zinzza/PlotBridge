// ponytail: Phase 1-5 — boot + LCD + WiFi + button + TCP bridge
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <SPIFFS.h>

Adafruit_ST7789 tft(2,3,6,4,1);
WiFiServer server(9100);

void showScreen(const char* l1, const char* l2="", const char* l3=""){
    tft.fillScreen(0xF7BE); tft.drawRect(0,0,280,240,0x0000);
    tft.setTextColor(0x0000,0xF7BE); tft.setTextSize(2);
    tft.setCursor(10,10); tft.println(l1);
    if(l2[0]){tft.setCursor(10,45);tft.println(l2);}
    if(l3[0]){tft.setCursor(10,80);tft.println(l3);}
}

void setup() {
    pinMode(8,OUTPUT); pinMode(9,INPUT_PULLUP);
    for(int i=0;i<3;i++){digitalWrite(8,LOW);delay(200);digitalWrite(8,HIGH);delay(200);}
    for(int d=0;d<=255;d+=5)analogWrite(5,d),delay(15);

    Serial.begin(115200);delay(200);
    Serial.println("PlotBridge v1.0");

    // ponytail: WiFi first — SPI takes pins WiFi needs
    SPIFFS.begin(true);
    tft.init(240,280);tft.setRotation(0);
    showScreen("PlotBridge v1.0","Booting...");
    showScreen("WiFi Setup...","Connecting..."); // ponytail: wifi state
    WiFiManager wm; wm.setConnectTimeout(10); wm.autoConnect("PlotBridge");
    IPAddress ip=WiFi.localIP();
    showScreen("Connected",("IP: "+ip.toString()).c_str(),WiFi.SSID().c_str());

    Serial1.begin(9600,SERIAL_8N1,7,0);
    server.begin();
    digitalWrite(8,LOW);
}

void loop(){
    static unsigned long btnPress=0;
    if(digitalRead(9)==LOW){
        if(!btnPress)btnPress=millis();
        if(millis()-btnPress>10000){SPIFFS.format();ESP.restart();}
        return;
    }
    btnPress=0;

    static WiFiClient client;
    static uint32_t lastRx=0;
    if(!client||!client.connected()){
        client=server.available();
        if(client){lastRx=millis();showScreen("Receiving...");}
    }else{
        while(client.available()){Serial1.write(client.read());lastRx=millis();}
        if(millis()-lastRx>3000){client.stop();showScreen("Idle");}
    }
}
