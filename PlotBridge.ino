// ponytail: Phase 1-5 — boot + LCD + WiFi + button + TCP bridge
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <SPIFFS.h>

Adafruit_ST7789* tft = nullptr; // ponytail: heap-alloc → no static SPI init
WiFiServer server(9100);
static bool screenReady = false;

void showScreen(const char* l1, const char* l2="", const char* l3=""){
    if(!screenReady){
        tft->fillScreen(0xF7BE); tft->drawRect(0,0,280,240,0x0000);
        screenReady=true;
    }else{
        tft->fillRect(2,2,276,106,0xF7BE);
    }
    tft->setTextColor(0x0000,0xF7BE); tft->setTextSize(2);
    tft->setCursor(10,10); tft->println(l1);
    if(l2[0]){tft->setCursor(10,45);tft->println(l2);}
    if(l3[0]){tft->setCursor(10,80);tft->println(l3);}
}

void showRx(uint32_t n){ // ponytail: fast byte counter — text overwrite, no fill
    tft->setTextColor(0xF7BE,0xF7BE); tft->setCursor(10,45); tft->print("                "); // erase
    tft->setTextColor(0x0000,0xF7BE); tft->setCursor(10,45); tft->printf("Bytes: %lu", static_cast<unsigned long>(n));
}

void setup() {
    pinMode(8,OUTPUT); pinMode(9,INPUT_PULLUP);
    for(int i=0;i<3;i++){digitalWrite(8,LOW);delay(200);digitalWrite(8,HIGH);delay(200);}
    for(int d=0;d<=255;d+=5)analogWrite(5,d),delay(15);

    // ponytail: LCD before WiFi so user sees boot screen
    tft = new Adafruit_ST7789(2,3,6,4,1);
    tft->init(240,280);tft->setRotation(0);
    showScreen("PlotBridge v1.0","Connecting WiFi...");
    SPI.end(); // ponytail: release SPI pins for WiFi AP

    SPIFFS.begin(true);
    WiFiManager wm; wm.autoConnect("PlotBridge");

    tft->init(240,280);tft->setRotation(0);
    screenReady=false;
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
        if(millis()-btnPress>10000){
            showScreen("WiFi Reset");
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
        if(client){lastRx=millis();receivedBytes=0;showScreen("Receiving...");}
    }else{
        while(client.available()){
            char c=client.read();Serial1.write(c);receivedBytes++;
            lastRx=millis();
        }
        if(millis()-lastRx>3000){
            char completeInfo[32];
            snprintf(completeInfo,sizeof(completeInfo),"Bytes: %lu",static_cast<unsigned long>(receivedBytes));
            showScreen("Complete",completeInfo);delay(1000);
            Serial1.flush();
            client.stop();
            IPAddress ip=WiFi.localIP();
            showScreen("Connected",("IP: "+ip.toString()).c_str(),WiFi.SSID().c_str());
        }
    }
}
