/* 
 * Mech Warfare 2011 
 * Scoring Transponder
 * 
 * Port Usage:
 *  Target Panels - Analog 0-3 (tie unused ones to VCC)
 *  Variable Pulse Output - Digital 12
 *  200ms Pulse Output & LED - Digital 9
 *  Jumper Digital 11 for variable pulse output
 *  
 * XBEE must be set to 38400bps:
 *  ATBD = 5 (38400)
 *  ATID - 6200 (PAN)
 *  MY  - 6200 + competitor ID
 *  DL  - 6201
 *  CH  - C
 */
 
#include "transponder.h"

void setup(){
  Serial.begin(BAUDRATE);
  // no hits yet
  hit = 0;
  // output pulse and LED
  pinMode(9, OUTPUT);
  pinMode(12, OUTPUT);
  // target plates
  pinMode(14, INPUT);
  pinMode(15, INPUT);
  pinMode(16, INPUT);
  pinMode(17, INPUT);
  // setup interrupt routine for target panels
  PCICR |= (1 << PCIE1);  // port C enable
  PCMSK1 = 0x0f;          // lower nibble
  interrupts();
}

void loop(){
  // if we've been hit
  if(hit > 0){
    unsigned long time = millis();
    // send hit over xbee
    Serial.write(0x55);
    Serial.write((unsigned char)TRANSPONDER_ID);
    Serial.write((unsigned char)255-TRANSPONDER_ID);
    Serial.write((unsigned char)hit);
    // send 50*plate# ms
    LED_ON;
    SIGNAL_HIGH;
    if(hit & 1){
      delay(50);
      SIGNAL_LOW;
      delay(150);
    }else if(hit & 2){
      delay(100);
      SIGNAL_LOW;
      delay(100);     
    }else if(hit & 4){
      delay(150);
      SIGNAL_LOW;
      delay(50);      
    }else{
      delay(200);
      SIGNAL_LOW;
    }
    LED_OFF;
    // 1 sec time
    while(time + TIMEOUT > millis());
    hit = 0;
  }
}

// interrupt routine for analog port
ISR(PCINT1_vect){
  hit = PINC;
}
