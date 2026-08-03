#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// 핀맵 (Docs/pinmap.md 기준)
// SCL=GPIO4, SDA/MOSI=GPIO6, RST=GPIO1, DC=GPIO3, CS=GPIO2
#define OLED_MOSI  6
#define OLED_CLK   4
#define OLED_DC    3
#define OLED_CS    2
#define OLED_RST   1

// Software SPI: SSD1306(가로, 세로, MOSI, CLK, DC, RST, CS)
Adafruit_SSD1306 display(128, 64, OLED_MOSI, OLED_CLK, OLED_DC, OLED_RST, OLED_CS);

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n=== SSD1306 OLED 128x64 Test ===");

  // SSD1306_SWITCHCAPVCC = 내부 charge-pump로 3.3V→7.5V 생성
  if (!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println("SSD1306 초기화 실패! 배선을 확인하세요.");
    while (1) delay(100);
  }
  Serial.println("SSD1306 초기화 성공!");

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // 부팅 화면
  display.setCursor(0, 0);
  display.println("OLED Test");
  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);
  display.setCursor(0, 16);
  display.println("128x64 Mono");
  display.setCursor(0, 28);
  display.println("SPI Mode OK");
  display.display();
  delay(2000);
}

void loop() {
  // 1. 전체 화면 채우기 + 텍스트
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.println("Hello!");
  display.setTextSize(1);
  display.setCursor(10, 40);
  display.print("Millis: ");
  display.print(millis() / 1000);
  display.println("s");
  display.display();
  delay(1500);

  // 2. 사각형 프레임 테두리
  display.clearDisplay();
  for (int i = 0; i < 8; i++) {
    display.drawRect(i, i, 128 - i * 2, 64 - i * 2, SSD1306_WHITE);
  }
  display.setCursor(35, 27);
  display.setTextSize(1);
  display.println("Rect Test");
  display.display();
  delay(1500);

  // 3. 원 그리기
  display.clearDisplay();
  display.drawCircle(64, 32, 28, SSD1306_WHITE);
  display.drawCircle(64, 32, 20, SSD1306_WHITE);
  display.drawCircle(64, 32, 12, SSD1306_WHITE);
  display.setCursor(38, 29);
  display.println("Circle");
  display.display();
  delay(1500);

  // 4. 대각선 + 삼각형
  display.clearDisplay();
  display.drawLine(0, 0, 127, 63, SSD1306_WHITE);
  display.drawLine(127, 0, 0, 63, SSD1306_WHITE);
  display.fillTriangle(64, 8, 20, 55, 108, 55, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK);
  display.setCursor(48, 20);
  display.println("X");
  display.setTextColor(SSD1306_WHITE);
  display.display();
  delay(1500);

  // 5. 작은 폰트 전체 출력
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("ABCDEFGHIJKLMNOPQRSTU");
  display.println("VWXYZ 0123456789!@#$%");
  display.println("abcdefghijklmnopqrstu");
  display.println("vwxyz The quick brown fox");
  display.println("jumps over the lazy dog.");
  display.drawLine(0, 56, 127, 56, SSD1306_WHITE);
  display.setCursor(0, 57);
  display.println("Font/Line Test OK");
  display.display();
  delay(2000);
}