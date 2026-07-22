# PlotBridge 핀맵 (test_lcd / test_wifi verified)

## LCD (Adafruit_ST7789, 240×280, rotation 0, font size 2)

| LCD | 신호 | ESP32-C3 GPIO |
|---|---|---|
| GND | 접지 | GND |
| VCC | 전원 | 3.3V |
| SCL | SPI 클록 | GPIO4 |
| SDA | SPI 데이터 | GPIO6 |
| RST | 리셋 | GPIO1 |
| DC | Data/Command | GPIO3 |
| CS | 칩 선택 | GPIO2 |
| BL | 백라이트 | GPIO5 (PWM) |

## UART (MAX3232 RS232-TTL → Plotter)

| 기능 | GPIO | 비고 |
|---|---|---|
| TX | GPIO0 | ESP32 TX → MAX3232 TTL RX |
| RX | GPIO7 | ESP32 RX ← MAX3232 TTL TX (선택) |

## LCD 상태

| 상태 | 화면 메시지 |
|---|---|
| 부팅 | PlotBridge v1.0 / Booting... |
| WiFi 연결 중 | WiFi Setup... / Connecting... |
| 연결됨 | Connected / IP: x.x.x.x / SSID |
| 수신 중 | Receiving... |
| idle | Idle |
