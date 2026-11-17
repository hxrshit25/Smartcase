# Hardware integration checklist

## Reported hardware (not independently verified)
- Arduino UNO
- RC522 + keychain RFID tags
- HM-10 BLE receiver
- Beacon described as “nRF5122” — confirm exact printed model (possibly nRF51822)
- NEO-6M V2 GPS
- L298N + Johnson 100 RPM motors
- Battery “3+2” — clarify series/parallel arrangement, chemistry, voltage and capacity

## Still required from hardware developer
1. Wi-Fi/network gateway model and wiring (UNO has no built-in Wi-Fi).
2. HM-10 exact board marking, firmware/version and AT-command response; confirm it can scan as BLE central and report beacon RSSI.
3. Exact beacon model and broadcast format/UUID/MAC.
4. Battery cell count, arrangement, chemistry, nominal/full-charge voltage and mAh.
5. Full wiring diagram and pin map for UNO, RC522, HM-10, GPS and L298N.
6. Existing Arduino `.ino` source if available.

## Provisional pin plan in scaffold
- RC522: SS/SDA D10, RST D9, MOSI D11, MISO D12, SCK D13; power per module specification.
- GPS: GPS TX -> UNO D4 (SoftwareSerial RX), GPS RX <- UNO D3 (optional; verify voltage levels).
- HM-10: not assigned until exact wiring and firmware are confirmed.
- L298N: not assigned; motor control remains disabled pending safety review.

Do not connect or power using this provisional plan until compared with the actual wiring. RC522 is a 3.3V device; protect its signal pins from 5V logic as required. Check common ground and supply ratings. Do not power motors from the UNO 5V pin.
