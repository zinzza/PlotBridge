// ponytail: Phase 1-5 — boot + LCD + WiFi + button + TCP bridge
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <SPIFFS.h>
#include "DisplayBackend.h"

DisplayBackend display;
WiFiServer server(9100);

void setup() {
    pinMode(8,OUTPUT); pinMode(9,INPUT_PULLUP);
    for(int i=0;i<3;i++){digitalWrite(8,LOW);delay(200);digitalWrite(8,HIGH);delay(200);}
    for(int d=0;d<=255;d+=5)analogWrite(5,d),delay(15);

    // Display before WiFi so the user sees the boot screen.
    display.begin();
    display.showScreen("PlotBridge v1.0","Connecting WiFi...");
    display.releaseBus();

    SPIFFS.begin(true);
    WiFiManager wm; wm.autoConnect("PlotBridge");

    display.begin();
    IPAddress ip=WiFi.localIP();
    display.showScreen("Connected",("IP: "+ip.toString()).c_str(),WiFi.SSID().c_str());

    Serial1.begin(9600,SERIAL_8N1,7,0);
    server.begin();
    digitalWrite(8,LOW);
}

void loop(){
    static unsigned long btnPress=0;
    if(digitalRead(9)==LOW){
        if(!btnPress)btnPress=millis();
        if(millis()-btnPress>10000){
            display.showScreen("WiFi Reset");
            digitalWrite(8,LOW);
            delay(500);
            WiFiManager wm;
            wm.resetSettings();
            SPIFFS.format();
            ESP.restart();
        }
        return;
    }
    btnPress=0;

    static WiFiClient client;
    static uint32_t lastRx=0;
    static uint32_t receivedBytes=0;
    if(!client||!client.connected()){
        client=server.accept();
        if(client){lastRx=millis();receivedBytes=0;display.showScreen("Receiving...");}
    }else{
        while(client.available()){
            char c=client.read();Serial1.write(c);receivedBytes++;
            lastRx=millis();
        }
        if(millis()-lastRx>3000){
            char completeInfo[32];
            snprintf(completeInfo,sizeof(completeInfo),"Bytes: %lu",static_cast<unsigned long>(receivedBytes));
            display.showScreen("Complete",completeInfo);delay(1000);
            Serial1.flush();
            client.stop();
            IPAddress ip=WiFi.localIP();
            display.showScreen("Connected",("IP: "+ip.toString()).c_str(),WiFi.SSID().c_str());
        }
    }
}
