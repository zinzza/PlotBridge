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

모듈 핀 표기가 `VCC`, `GND`, `RX`, `TX`인 경우의 연결이다. `RX`와 `TX`는 모듈의 TTL 측 신호 핀으로 해석한다.

| MAX3232 모듈 핀 | ESP32-C3 연결 | 방향/비고 |
|---|---|---|
| VCC | 3.3V | 모듈이 3.3V 전원을 지원하는지 확인 |
| GND | GND | ESP32와 공통 접지 |
| RX | GPIO0 (TX) | ESP32 TX → 모듈 RX |
| TX | GPIO7 (RX) | 모듈 TX → ESP32 RX (수신 선택) |

현재 펌웨어 UART 설정은 `9600-8-N-1`, flow control 없음이다. 모듈이 3.3V 전원을 지원하는지 확인한 뒤 VCC를 연결한다. RS-232 측 커넥터는 플로터의 RX/TX/GND와 연결하며, 모듈의 TTL 핀에 RS-232 신호를 직접 연결하지 않는다.

## LCD 상태

| 상태 | 화면 메시지 |
|---|---|
| 부팅 | PlotBridge v1.0 / Booting... |
| WiFi 연결 중 | WiFi Setup... / Connecting... |
| 연결됨 | Connected / IP: x.x.x.x / SSID |
| 수신 중 | Receiving... |
| idle | Idle |
