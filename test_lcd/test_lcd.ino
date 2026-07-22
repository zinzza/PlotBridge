#include <Adafruit_GFX.h>    
#include <Adafruit_ST7789.h> 
#include <SPI.h>

// [핵심] 핀을 3개만 넣어 하드웨어 SPI 가속을 활성화합니다.
Adafruit_ST7789 tft = Adafruit_ST7789(2, 3, 1); // CS, DC, RST 핀

void setup(void) {
  tft.init(240, 280); 
  // SPI 속도를 40MHz로 설정하여 가속 극대화
  //tft.setSPISpeed(40000000); 
}

void loop() {
  // 이제 화면이 팍팍 바뀝니다.
//   tft.fillScreen(ST77XX_RED);
//   delay(500);
//   tft.fillScreen(ST77XX_BLUE);
//   delay(500);
   tft.fillScreen(ST77XX_GREEN);
  tft.println("Black Eagles!");
  delay(500);
}