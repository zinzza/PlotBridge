# PlotBridge 구현 계획

## 1. 목표

WiFi가 없는 플로터에 ESP32-C3 Super Mini를 연결하여, 같은 네트워크의 클라이언트가 전송한 HPGL 데이터를 플로터의 Serial 입력으로 전달한다.

```text
HPGL 클라이언트 ── WiFi/TCP ──> ESP32-C3 ── Serial ──> 플로터
                                      └── LCD: 상태/네트워크 표시
```

### 1.1 1차 완료 기준

- 저장된 WiFi 설정으로 부팅 후 자동 연결한다.
- 최초 설정 시 WiFiManager 설정 포털에 진입한다.
- 네트워크에서 HPGL 원본 바이트를 받아 변경 없이 플로터 Serial로 전달한다.
- 연결 상태와 IP를 LCD에 표시한다.
- BOOT 버튼을 10초 누르면 WiFi/네트워크 설정을 삭제하고 재설정 모드로 진입한다.
- 전원 재인가와 장시간 동작에서 재현 가능한 오류 없이 동작한다.

### 1.2 현재 진행 상태

| 단계 | 상태 | 현재 결과 |
|---|---|---|
| Phase 0 — 요구사항/회로 | 진행 중 | HW44 미연결. LCD 연결 완료. UART GPIO와 HW44 전원/TTL 전압은 미확정 |
| Phase 1 — 빌드/최소 하드웨어 | 진행 중 | GPIO8 직접 제어 및 LCD 초기화 전 LED 점등 수정 빌드 컴파일 및 COM7 업로드 성공. 실기기 점등 확인 필요 |
| Phase 2 — WiFi 설정/BOOT 버튼 | 구현 완료, 실기기 검증 필요 | WiFiManager 설정 저장, BOOT GPIO9 10초 초기화 코드 구현 |
| Phase 3 — WiFi 설정 | 구현 완료, 실기기 검증 필요 | 저장 WiFi 자동 연결 또는 비밀번호 없는 WiFiManager AP 포털 |
| Phase 4 — LCD/진단 | 구현 완료, 화면 검증 필요 | 240×280 패널, 부팅/연결/수신 시작/완료 화면 구현. 수신 데이터 미리보기와 수신 중 반복 갱신은 사용하지 않음 |
| Phase 5 — TCP-to-Serial | 구현 완료, 실기기 검증 필요 | TCP 9100의 수신 바이트를 UART로 직접 전달 |

#### CLI 검증 기록

- 보드: `esp32:esp32:nologo_esp32c3_super_mini:CDCOnBoot=cdc`
- 포트: `COM7`
- 컴파일: 성공
- 업로드: 최신 빌드 COM7 업로드 성공, 플래시 Hash 검증 성공
- 실행 화면: LCD 실제 표시와 WiFi 접속은 다음 테스트에서 확인

## 2. 먼저 확정해야 할 결정

아래 항목은 구현 전에 확정한다. 현재 문서에는 합리적인 기본안을 적어 두었으며, 답변을 받으면 이 계획의 `결정 상태`와 세부 설계를 갱신한다.

| ID | 결정 항목 | 기본안 | 결정 상태 |
|---|---|---|---|
| D1 | HPGL 수신 방식 | raw TCP 서버, 포트 9100 | 확정 |
| D2 | 동시 클라이언트 | 한 번에 한 클라이언트만 허용 | 확정 |
| D3 | 플로터 Serial 핀 | GPIO0 (TX), GPIO7 (RX) | 확정 |
| D4 | Serial 전기 규격 | MAX3232 RS232-TTL 모듈 사용. ESP32 측은 TTL UART (3.3V), 플로터 측은 RS-232 | 확정 |
| D5 | Serial 통신 조건 | 9600-8-N-1, flow control 없음 | 확정 |
| D6 | 설정 순서 | WiFiManager::autoConnect() — 저장 WiFi 자동 연결, 없으면 captive portal | 확정 |
| D7 | 설정 모드 제한 시간 | WiFiManager autoConnect 내장 timeout, 사용자가 포털에서 설정할 때까지 유지 | 확정 |
| D9 | LCD 동작 | Adafruit_ST7789, 240×280, rotation 0, constructor로 핀 지정 | 확정 |
| D10 | HPGL 작업 경계 | TCP 종료 또는 마지막 수신 후 3초 동안 추가 수신이 없으면 작업 종료 | 확정 |

## 3. 권장 기본 설계

### 3.1 현재 펌웨어 구성

현재 기능은 `PlotBridge.ino` 단일 스케치에 구현되어 있다. 향후 규모가 커지면 아래 기능별 분리를 검토한다.

- `main`: 초기화와 메인 루프
- `wifi_setup`: 자동 연결과 WiFiManager 포털
- `tcp_server`: HPGL TCP 수신 및 클라이언트 수명 관리
- `plotter_serial`: UART 초기화와 송신
- `display`: Adafruit_ST7789 기반 LCD 초기화와 상태 화면 (CS=2, DC=3, RST=1, MOSI=6, SCLK=4, 240×280, rotation 0)
- `button`: BOOT 버튼 장시간 누름 감지

수신 데이터는 문자열로 파싱하지 않고 바이트 단위로 처리한다. HPGL 명령을 임의로 수정하거나 줄바꿈을 추가하지 않는다.

### 3.2 상태 머신

```text
BOOT
  └─ SPIFFS 초기화 → WiFiManager::autoConnect("PlotBridge")

WIFIMANAGER_AP
  └─ 설정 저장/연결 성공 ─> RUNNING

RUNNING
  ├─ TCP 연결 ─> STREAMING
  └─ BOOT 10초 ─> WiFi 설정 삭제 후 재부팅

STREAMING
  ├─ 수신 바이트 ─> Serial 전달
  ├─ 3초 idle ─> COMPLETE
  └─ 클라이언트 종료 ─> RUNNING
```

### 3.3 WiFi 설정 저장

부팅 시 `SPIFFS.begin(true)`를 호출한 후 `WiFiManager::autoConnect()`로 저장된 WiFi에 연결하거나 설정 포털을 연다.

### 3.4 WiFi 접속 방식

```text
부팅 → SPIFFS.begin → WiFiManager::autoConnect("PlotBridge")
  ├─ 저장된 WiFi 있음 → 자동 연결
  └─ 없음 → captive portal (AP: "PlotBridge")
```

현재 버전에서는 WPS, SmartConfig, 정적 IP 설정, Serial fallback을 구현하지 않는다. 향후 연결 안정성이나 설치 편의성 요구가 생기면 별도 검토한다.

### 3.5 HPGL 스트리밍

- TCP 서버는 `WiFiServer` 기반으로 구현한다.
- 1차 버전은 동시 접속을 거부하고 현재 작업을 보호한다.
- `client.read()`로 받은 바이트를 가능한 즉시 UART로 전달한다.
- 마지막 수신 시각을 기록하고 3초 동안 추가 수신이 없으면 작업을 종료한다.
- 현재는 플로터의 flow control을 사용하지 않고, TCP 수신 바이트를 별도 작업 버퍼 없이 UART로 직접 전달한다.
- 향후 다른 플로터에서 flow control이 필요하다고 확인되면 링 버퍼, backpressure, XON/XOFF 또는 하드웨어 handshake를 별도 프로파일로 검토한다.
- TCP ACK는 네트워크 스택이 처리하는 수신 확인과 구분한다. 플로터가 실제로 처리했다는 의미의 응답은 1차 범위에 포함하지 않는다.

LCD는 TCP 수신 시작 시 `Receiving...`을 한 번 표시하고, 마지막 TCP 수신 후 3초 idle을 전송 종료로 간주해 `Complete`와 작업별 수신 바이트 수를 먼저 표시한다. 이후 UART `flush()`를 수행한다. 수신 중에는 화면을 갱신하지 않으며, 수신 데이터도 LCD에 출력하지 않는다. 전체 화면 초기화는 초기 화면과 LCD 재초기화 후에만 수행하고, 이후 상태 변경은 텍스트 영역만 갱신한다.

## 4. 하드웨어 검증 순서

1. ESP32-C3 보드의 실제 핀맵과 USB/BOOT/LED 충돌을 확인한다.
2. Adafruit_ST7789 LCD를 백라이트 제외 상태에서 연결하고 단색/문자 표시를 확인한다.
3. 플로터의 입력 라벨과 서비스 매뉴얼로 RS-232 커넥터와 신호 방향을 확인한다.
4. HW44의 정확한 보드 핀 이름, 공급 전압, TTL 신호 전압을 실물 또는 판매자 회로도에서 확인한다.
5. ESP32 UART TX → HW44 TTL RX, HW44 RS-232 TX → 플로터 RX로 연결한다. RX도 사용할 경우 반대 방향을 교차 연결한다.
6. ESP32와 HW44의 GND를 연결하고, HW44 전원은 모듈 사양에 맞춘다. 3.3V UART 호환 여부를 반드시 확인한다.
7. 실제 플로터 연결 전에 USB-UART 또는 로직 애널라이저로 baud, idle level, 데이터 형식을 검증한다.
8. 작은 HPGL 사각형을 전송하여 펜 이동과 데이터 손실을 확인한다.

## 5. 단계별 구현 순서

### Phase 0 — 요구사항과 회로 확정

- [x] 결정 항목 정리
- [ ] 실제 플로터 모델, RS-232 커넥터 핀맵 확인
- [ ] MAX3232 전원/TTL 전압 확인
- [x] ESP32-C3 UART 및 LCD 핀 충돌 검토
- [ ] 전원/레벨시프터/공통 GND 회로 확정
- [x] Arduino-ESP32와 라이브러리 버전 고정

**산출물:** 확정 핀맵, 배선도, 설정값 표, 테스트 장비 목록

### Phase 1 — 빌드와 최소 하드웨어

- [x] Arduino CLI 프로젝트 구성
- [x] 보드 패키지와 라이브러리 의존성 고정
- [ ] 커스텀 파티션 테이블 적용 여부 확인
- [x] 부팅 화면과 펌웨어 버전 표시
- [ ] UART loopback 테스트 — MAX3232 미연결로 보류
- [x] LCD 초기화/문자/백라이트 테스트 — 실기기 확인 완료

**완료 기준:** 펌웨어가 반복 업로드되고, LCD와 UART 자체 테스트가 통과한다.

### Phase 2 — 설정 저장과 버튼

- [x] 실행 중 BOOT 버튼 10초 long-press 감지
- [x] 공장 초기화 시 WiFiManager credential 삭제 후 재설정 진입

**완료 기준:** 전원 재인가 후 WiFi 설정이 유지되고, 10초 누름으로 credential이 삭제된다.

### Phase 3 — WiFi 설정 상태 머신

- [x] WiFiManager::autoConnect("PlotBridge") — 저장 WiFi 자동 연결
- [x] 저장 WiFi 없으면 captive portal (AP: "PlotBridge", 비밀번호 없음)
- [x] 연결 성공 시 SPIFFS 자동 저장 (WiFiManager 내장)

**완료 기준:** 저장 설정, 신규 설정, 자동 연결 실패 후 포털 대기, 재부팅 복원이 모두 테스트된다.

### Phase 4 — LCD와 진단

- [x] Adafruit_ST7789, 240×280, rotation 0, constructor로 핀 지정
- [x] 화면 모델 정의: 부팅, 연결됨, 수신 중, 완료
- [x] IP와 SSID 표시
- [x] 수신 시작/완료 시에만 상태 화면 갱신
- [x] 상태 변경 시 텍스트 영역만 갱신해 전체 화면 전송 최소화
- [x] 수신 데이터 미리보기 제거
- [x] Complete 화면에 작업별 수신 바이트 수 표시

**완료 기준:** 플로터 Serial 연결 없이도 LCD를 보며 부팅, WiFiManager, WiFi 연결, IP 할당, 연결 상태를 확인할 수 있다. 실기기 확인 필요.

### Phase 5 — TCP-to-Serial 브릿지

- [x] TCP 포트 서버 구현 (port 9100, WiFiServer)
- [x] 단일 클라이언트 정책 구현 (D2)
- [ ] 링 버퍼와 UART 송신 루프 검토
- [x] 연결 종료/3초 idle timeout 처리 (D10)
- [x] 수신 바이트를 Serial1로 직접 전달
- [x] 현재 flow control 없음(9600-8-N-1)으로 동작
- [ ] raw byte 보존 테스트 — Serial1 출력 캡처 필요
- [ ] 작은/중간/연속 HPGL 작업 테스트 — MAX3232 + 플로터 실기기 필요

**완료 기준:** 알려진 HPGL 파일의 바이트 수와 플로터 수신 바이트 수가 일치하고, 실제 플롯 결과가 정상이다.

### Phase 6 — 통합 검증과 배포

- [ ] 전원 재인가 100회 테스트
- [ ] WiFi AP 재시작/신호 약화 테스트
- [ ] TCP 클라이언트 중단/재접속 테스트
- [ ] 장시간 HPGL 작업 테스트
- [ ] 잘못된 설정/포트/패킷 테스트
- [ ] 공장 초기화 및 복구 테스트
- [ ] 최종 배선도, 업로드 방법, 사용 설명서 작성
- [ ] 펌웨어 버전 및 복구용 기본 설정 기록

## 6. 테스트 계획

### 기능 테스트

- 자동 WiFi 연결 성공/실패
- WPS 버튼 접속 성공 (향후 연결 편의성이 필요할 때 검토)
- WPS 30초 timeout 후 비밀번호 없는 WiFiManager 포털 대기 (향후 검토)
- DHCP와 정적 IP (향후 검토)
- TCP 포트 접속/거부/재접속
- HPGL 특수 바이트 및 긴 명령
- LCD 각 상태 화면
- BOOT 10초 초기화

### 장애 테스트

- WiFi가 없는 상태에서 부팅
- AP가 작업 중 사라짐
- TCP 클라이언트가 작업 중 종료
- Serial 케이블 분리/잘못된 레벨
- 링 버퍼 포화 (링 버퍼를 도입할 경우)
- 잘못된 IP/포트/NVS 값
- 빠른 버튼 반복과 전원 불안정

### 수용 테스트 예시

1. PC에서 테스트 HPGL 파일의 SHA-256과 ESP32가 Serial로 내보낸 캡처의 SHA-256을 비교한다.
2. 10회 연속 동일 파일 전송 후 플롯 결과와 바이트 수가 모두 동일한지 확인한다.
3. 전원을 껐다 켜도 IP와 WiFi 설정이 유지되는지 확인한다.
4. BOOT 버튼을 10초 누른 뒤 기존 설정으로 자동 연결되지 않는지 확인한다.

## 7. 위험 요소와 대응

| 위험 | 영향 | 대응 |
|---|---|---|
| HW44 전원/TTL 전압이 ESP32와 맞지 않음 | 보드 손상/통신 불량 | HW44 사양 확인, 3.3V UART 호환 확인, 전압 측정 |
| 플로터가 RS-232인데 ESP32를 직접 연결 | 보드/플로터 손상 | 반드시 HW44를 거쳐 연결하고 TX/RX 방향 확인 |
| UART 핀 충돌 또는 부트 스트랩 충돌 | 부팅 실패/데이터 손실 | 보드 실측 및 최소 펌웨어에서 검증 |
| WiFiManager 라이브러리 호환성 | 설정 불가 | Arduino-ESP32 버전 고정, 포털 설정을 독립 테스트 |
| TCP 속도가 Serial보다 빠름 | 데이터 처리 지연 또는 손실 가능성 | 링 버퍼, flow control 정책, overflow 오류 표시를 향후 검토 |
| LCD 갱신이 브릿지를 지연 | HPGL 처리 지연 가능 | 수신 시작과 UART 전송 완료 시에만 갱신하고 수신 중 갱신하지 않음 |
| 플로터별 flow control 요구가 다름 | 장시간 작업에서 플로터 버퍼 오류 가능 | 현재는 flow control 없음으로 사용. 모델별 필요성이 확인되면 별도 프로파일과 캡처 테스트를 향후 검토 |
| WiFiManager 설정 저장 오류 | 재부팅 후 연결 실패 | 설정 포털 재진입 및 BOOT 10초 초기화 |
| 작업 중 재연결로 데이터 중복 | 오작동/재플롯 | 1차는 작업 중 단일 연결만 허용하고 재개 기능 제외 |

## 8. 초기 파일 구조 제안

```text
PlotBridge/
├─ PlotBridge.ino
├─ Config.h
├─ Config.cpp
├─ WifiSetup.h
├─ WifiSetup.cpp
├─ TcpServer.h
├─ TcpServer.cpp
├─ PlotterSerial.h
├─ PlotterSerial.cpp
├─ Display.h
├─ Display.cpp
├─ Button.h
├─ Button.cpp
├─ partitions.csv
├─ libraries.txt
└─ README.md
```

초기에는 기능별 `.cpp`를 분리하되, 상태 머신의 소유권은 `PlotBridge.ino`에 둔다. 각 모듈은 `setup()`에서 오래 블로킹하지 않고 `tick()` 형태로 메인 루프에서 진행 가능하도록 설계한다.

## 9. 진행 순서와 다음 작업

1. 확정된 결정 항목과 미확정 하드웨어 조건을 검토한다.
2. 실제 플로터의 모델명과 Serial 규격을 확인한다.
3. 확정된 핀맵을 기준으로 Phase 1 최소 펌웨어를 만든다.
4. UART/LCD 단독 테스트 후 실제 HPGL로 TCP 브릿지를 검증한다.

WiFi 접속 방식은 현재 구현 기준으로 저장된 WiFi 자동 연결 → 연결 정보가 없으면 비밀번호 없는 WiFiManager AP와 captive portal 대기이다. WPS와 정적 IP는 향후 요구사항에 따라 검토한다.
