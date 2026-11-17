/*
  SMARTCASE Arduino UNO diagnostic scaffold
  Reported modules: RC522 RFID, NEO-6M V2 GPS, HM-10 BLE, L298N.

  IMPORTANT:
  - Provisional pins below MUST be checked against the real wiring first.
  - This sketch does NOT drive motors and does NOT claim HM-10 beacon scanning.
  - HM-10 BLE central/scanning support depends on module firmware and must be verified.
  - UNO has no Wi-Fi. Serial output is for bench diagnostics; remote dashboard needs a gateway.

  Libraries: MFRC522, TinyGPSPlus
*/
#include <SPI.h>
#include <MFRC522.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>

// Common RC522-to-UNO wiring; verify with your actual circuit.
#define RFID_SS_PIN 10
#define RFID_RST_PIN 9
MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);

// Provisional GPS UART pins: UNO RX=4, TX=3. GPS TX -> UNO pin 4.
SoftwareSerial gpsSerial(4, 3);
TinyGPSPlus gps;

// HM-10 pins intentionally reserved pending verified wiring/firmware.
// SoftwareSerial bleSerial(7, 8); // RX, TX — do not enable until confirmed.

unsigned long lastReport = 0;

void setup() {
  Serial.begin(115200);
  SPI.begin();
  rfid.PCD_Init();
  gpsSerial.begin(9600);
  Serial.println(F("SMARTCASE_UNO_READY"));
  Serial.println(F("Diagnostic mode: motors disabled; BLE scan not configured."));
}

void loop() {
  while (gpsSerial.available()) gps.encode(gpsSerial.read());

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      if (rfid.uid.uidByte[i] < 0x10) uid += "0";
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.print(F("{\"type\":\"rfid_scan\",\"tag\":\""));
    Serial.print(uid);
    Serial.println(F("\"}"));
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  if (millis() - lastReport >= 5000) {
    lastReport = millis();
    Serial.print(F("{\"type\":\"telemetry\",\"gps_fix\":"));
    Serial.print(gps.location.isValid() ? "true" : "false");
    if (gps.location.isValid()) {
      Serial.print(F(",\"latitude\":")); Serial.print(gps.location.lat(), 6);
      Serial.print(F(",\"longitude\":")); Serial.print(gps.location.lng(), 6);
    }
    Serial.println(F("}"));
  }
}
