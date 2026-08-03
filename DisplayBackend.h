#pragma once

#include "PlotBridgeConfig.h"

#if DISPLAY_TYPE == DISPLAY_LCD
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#elif DISPLAY_TYPE == DISPLAY_OLED
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#elif DISPLAY_TYPE == DISPLAY_OLED_4PIN
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>
#else
#error "DISPLAY_TYPE must be DISPLAY_LCD, DISPLAY_OLED, or DISPLAY_OLED_4PIN"
#endif

class DisplayBackend {
public:
    void begin() {
#if DISPLAY_TYPE == DISPLAY_LCD
        if (!lcd) {
            lcd = new Adafruit_ST7789(2, 3, 6, 4, 1);
        }
        lcd->init(240, 280);
        //lcd->init(76, 284);
        lcd->setRotation(0);
#elif DISPLAY_TYPE == DISPLAY_OLED
        if (!oledReady) {
            oledReady = oled.begin(SSD1306_SWITCHCAPVCC);
            if (!oledReady) {
                while (true) {
                    delay(1000);
                }
            }
        }
#else
        if (!oledReady) {
            Wire.begin(6, 4);
            oledReady = oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
            if (!oledReady) {
                while (true) {
                    delay(1000);
                }
            }
        }
#endif
        screenReady = false;
    }

    void releaseBus() {
#if DISPLAY_TYPE == DISPLAY_LCD
        SPI.end();
#endif
    }

    void showScreen(const char* line1, const char* line2 = "", const char* line3 = "") {
#if DISPLAY_TYPE == DISPLAY_LCD
        if (!lcd) {
            return;
        }
        if (!screenReady) {
            lcd->fillScreen(0xF7BE);
            lcd->drawRect(0, 0, 240, 280, 0x0000);
            screenReady = true;
        } else {
            lcd->fillRect(2, 2, 236, 106, 0xF7BE);
        }
        lcd->setTextColor(0x0000, 0xF7BE);
        lcd->setTextSize(2);
        lcd->setCursor(10, 10);
        lcd->println(line1);
        if (line2[0]) {
            lcd->setCursor(10, 45);
            lcd->println(line2);
        }
        if (line3[0]) {
            lcd->setCursor(10, 80);
            lcd->println(line3);
        }
#elif DISPLAY_TYPE == DISPLAY_OLED
        if (!oledReady) {
            return;
        }
        oled.clearDisplay();
        oled.setTextColor(SSD1306_WHITE);
        oled.setTextSize(1);
        oled.setCursor(0, 0);
        oled.println(line1);
        if (line2[0]) {
            oled.setCursor(0, 16);
            oled.println(line2);
        }
        if (line3[0]) {
            oled.setCursor(0, 32);
            oled.println(line3);
        }
        oled.display();
#else
        if (!oledReady) {
            return;
        }
        oled.clearDisplay();
        oled.setTextColor(SSD1306_WHITE);
        oled.setTextSize(1);
        oled.setCursor(0, 0);
        oled.println(line1);
        if (line2[0]) {
            oled.setCursor(0, 8);
            oled.println(line2);
        }
        if (line3[0]) {
            oled.setCursor(0, 16);
            oled.println(line3);
        }
        oled.display();
#endif
    }

private:
#if DISPLAY_TYPE == DISPLAY_LCD
    Adafruit_ST7789* lcd = nullptr;
#elif DISPLAY_TYPE == DISPLAY_OLED
    Adafruit_SSD1306 oled{128, 64, 6, 4, 3, 1, 2};
    bool oledReady = false;
#else
    Adafruit_SSD1306 oled{128, 32, &Wire, -1};
    bool oledReady = false;
#endif
    bool screenReady = false;
};
