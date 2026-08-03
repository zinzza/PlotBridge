# PlotBridge

WiFi 미지원 플로터를 WiFi로. ESP32-C3 Super Mini가 받아서 Serial로 전달.

## LCD 핀맵 (확정)

```
GND → GND
VCC → 3.3V
SCL → GPIO4
SDA → GPIO6
RST → GPIO1
DC  → GPIO3
CS  → GPIO2
BL  → GPIO5
```

LCD: ST7789 240×280 1.69"

## 디스플레이 버전 빌드

공통 네트워크, 버튼, UART, TCP 로직은 `PlotBridge.ino`에 유지하고 LCD/OLED 출력만 `DisplayBackend.h`에서 분리한다.

빌드할 디스플레이는 `PlotBridgeConfig.h`의 한 줄로 선택한다.

```cpp
#define DISPLAY_TYPE DISPLAY_LCD   // ST7789 LCD
// #define DISPLAY_TYPE DISPLAY_OLED  // SSD1306 SPI OLED
```

OLED 버전으로 빌드할 때는 위 두 줄의 주석을 반대로 바꾼다. 기본값은 LCD이며, OLED는 128×64 해상도에 맞춰 작은 글꼴로 표시한다.

## UART 핀

플로터 통신용 `Serial1`은 `9600-8-N-1`로 설정되어 있다.

```cpp
Serial1.begin(9600, SERIAL_8N1, 7, 0);
```

ESP32-C3 기준 GPIO7은 RX, GPIO0은 TX이다. MAX3232 모듈의 TTL RX는 GPIO0(TX)에, TTL TX는 GPIO7(RX)에 연결한다.
