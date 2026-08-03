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

// 플로터/프린터 아이콘 그리기
void drawPlotterLogo() {
  // --- 종이 영역 (위쪽) ---
  display.drawRect(14, 2, 100, 36, SSD1306_WHITE);  // 종이 테두리

  // 상승 추세 그래프 라인 (꺾은선)
  // 하단 왼쪽에서 시작 → 우상향
  display.drawLine(22, 32, 34, 28, SSD1306_WHITE);
  display.drawLine(34, 28, 46, 34, SSD1306_WHITE);
  display.drawLine(46, 34, 58, 22, SSD1306_WHITE);
  display.drawLine(58, 22, 70, 26, SSD1306_WHITE);
  display.drawLine(70, 26, 82, 16, SSD1306_WHITE);
  display.drawLine(82, 16, 94, 20, SSD1306_WHITE);
  display.drawLine(94, 20, 106, 10, SSD1306_WHITE);

  // 데이터 포인트 (작은 원)
  display.fillCircle(22, 32, 2, SSD1306_WHITE);
  display.fillCircle(34, 28, 2, SSD1306_WHITE);
  display.fillCircle(46, 34, 2, SSD1306_WHITE);
  display.fillCircle(58, 22, 2, SSD1306_WHITE);
  display.fillCircle(70, 26, 2, SSD1306_WHITE);
  display.fillCircle(82, 16, 2, SSD1306_WHITE);
  display.fillCircle(94, 20, 2, SSD1306_WHITE);
  display.fillCircle(106, 10, 2, SSD1306_WHITE);

  // --- 플로터 본체 (아래쪽) ---
  display.fillRoundRect(8, 42, 112, 20, 3, SSD1306_WHITE);  // 본체 (흰색)
  
  // 본체 위에 검은색 텍스트
  display.setTextColor(SSD1306_BLACK);
  display.setTextSize(1);
  display.setCursor(38, 48);
  display.println("PLOTTER");
  
  // 본체 디테일 선 (종이 배출구)
  display.drawLine(14, 44, 114, 44, SSD1306_BLACK);
  
  // 전원/상태 LED (작은 원)
  display.fillCircle(18, 52, 2, SSD1306_BLACK);
  
  // 버튼들
  display.drawRect(100, 49, 6, 4, SSD1306_BLACK);
  display.drawRect(108, 49, 6, 4, SSD1306_BLACK);
  
  display.setTextColor(SSD1306_WHITE);
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

  // 6. 플로터 아이콘
  display.clearDisplay();
  drawPlotterLogo();
  display.display();
  delay(2500);
}