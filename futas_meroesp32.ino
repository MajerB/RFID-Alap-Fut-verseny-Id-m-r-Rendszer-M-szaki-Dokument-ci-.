#include <Arduino.h>

// BEKÖTÉS (Ellenőrizd le!):
// ESP32 P16 láb (RX2) ---> UHF Modul TXD
// ESP32 P17 láb (TX2) ---> UHF Modul RXD
#define RXD2 16
#define TXD2 17
#define BUZZER_PIN 4

// A gyári programból kiolvasott parancs (M100 firmware):
// AA 00 22 00 00 22 DD
byte cmdRead[] = {0xAA, 0x00, 0x22, 0x00, 0x00, 0x22, 0xDD};

void setup() {
  // 1. Csipogó beállítása (legyen csendben induláskor)
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); 

  // 2. Soros portok indítása
  Serial.begin(115200); // USB a számítógép felé
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2); // Kapcsolat az RFID modullal

  Serial.println("--- RENDSZER INDUL (AA parancs mod) ---");
  delay(1000);
}

void loop() {
  // 1. Parancs küldése a modulnak: "Olvass!"
  // Pontosan azt küldjük, ami a fotón a 'Send' mezőben volt
  Serial2.write(cmdRead, sizeof(cmdRead));
  
  // 2. Várunk kicsit a válaszra
  delay(100);

  // 3. Megnézzük, jött-e válasz
  if (Serial2.available()) {
    bool kartyaVolt = false;
    
    Serial.print("ADAT: ");
    while (Serial2.available()) {
      int adat = Serial2.read();
      
      // Szépen írjuk ki (HEX formátumban)
      if (adat < 0x10) Serial.print("0");
      Serial.print(adat, HEX);
      Serial.print(" ");
      
      kartyaVolt = true;
    }
    Serial.println(); // Új sor

    // Ha jött adat, csippantunk egy rövidet
    if (kartyaVolt) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(50); 
      digitalWrite(BUZZER_PIN, LOW);
    }
  }
  
  // 4. Nem zaklatjuk túl gyakran, másodpercenként kb. 2-3x olvasunk
  delay(400);
}