#include <Arduino.h>

char incoming;

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  Serial.println("ESP32 READY");
}

void loop() {
  if (Serial.available()) {
    incoming = Serial.read();

    if (incoming == '1')
      digitalWrite(2, HIGH);

    if (incoming == '0')
      digitalWrite(2, LOW);
  }
}
