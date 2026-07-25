# PlotBridge 회로도

## 전체 연결도

```text
                        3.3V ─────────────────────────────┐
                        GND ─────────────────────────┐    │
                                                      │    │
         ┌──────────────────────────────────────────────┐  │    │
         │               ESP32-C3 Super Mini            │  │    │
         │                                              │  │    │
         │  GPIO2  ─── CS   ─── LCD ST7789 ─── VCC ─────┘    │
         │  GPIO3  ─── DC       240×280         GND ──────────┘
         │  GPIO6  ─── SDA/MOSI
         │  GPIO4  ─── SCL/SCLK
         │  GPIO1  ─── RST
         │  GPIO5  ─── BL (PWM)
         │
         │  GPIO0  ─── RX (TTL) ─── MAX3232 ─── RS-232 TX ─── Plotter RX
         │  GPIO7  ─── TX (TTL)       │
         │  GND    ─── GND            │── RS-232 RX ─── Plotter TX (선택)
         │  3.3V   ─── VCC            │── RS-232 GND ── Plotter GND
         │
         │  GPIO8  ─── LED (LOW=ON, 내장)
         │  GPIO9  ─── BOOT 버튼 (INPUT_PULLUP, 10s=WiFi Reset)
         │
         └──────────────────────────────────────────────┘
```

## 연결 테이블

### LCD (Adafruit ST7789, 240×280, Rotation 0)

| LCD 핀 | 신호 | ESP32-C3 GPIO |
|---|---|---|
| GND | 접지 | GND |
| VCC | 전원 | 3.3V |
| CS | SPI 칩 선택 | GPIO2 |
| DC | Data/Command | GPIO3 |
| SDA | SPI MOSI | GPIO6 |
| SCL | SPI 클록 | GPIO4 |
| RST | 리셋 | GPIO1 |
| BL | 백라이트 (PWM) | GPIO5 |

### UART (MAX3232 RS-232 ↔ TTL 모듈)

| MAX3232 모듈 핀 | ESP32-C3 연결 | 방향 |
|---|---|---|
| VCC | 3.3V | 전원 |
| GND | GND | 공통 접지 |
| RX | GPIO0 | ESP32 TX → 모듈 RX |
| TX | GPIO7 | 모듈 TX → ESP32 RX (선택) |

### MAX3232 ↔ 플로터 (RS-232 측)

RS-232 연결은 **교차 연결**이다.

| MAX3232 RS-232 측 | 플로터 |
|---|---|
| RS-232 TX | 플로터 RX |
| RS-232 RX | 플로터 TX (선택) |
| RS-232 GND | 플로터 GND |

### 기타

| ESP32-C3 GPIO | 대상 | 동작 |
|---|---|---|
| GPIO8 | 내장 LED | `LOW` = ON |
| GPIO9 | BOOT 버튼 | `INPUT_PULLUP`, 10초 long-press = WiFi 설정 초기화 |

## 설정

| 항목 | 값 |
|---|---|
| UART | 9600-8-N-1 (Serial1) |
| Flow Control | 사용하지 않음 |
| TCP 포트 | 9100 |
| WiFi | WiFiManager `autoConnect("PlotBridge")` |

## 주의사항

1. MAX3232 모듈이 **3.3V VCC**를 지원하는지 확인 후 전원을 연결한다.
2. MAX3232의 TTL 측 핀에 RS-232 신호를 직접 연결하지 않는다.
3. ESP32 GPIO를 플로터 RS-232 포트에 직접 연결하지 않는다. 반드시 MAX3232를 경유한다.
4. ESP32-C3는 3.3V 로직이므로 5V TTL 모듈을 사용할 경우 레벨 변환이 필요하다.
