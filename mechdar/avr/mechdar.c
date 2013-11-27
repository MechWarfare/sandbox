/* MechDAR version A.0
 * http://www.vanadiumlabs.com/mechdar 
 * 
 * Copyright (c) 2009, Michael E. Ferguson
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, 
 *   this list of conditions and the following disclaimer.
 * - Redistributions in binary form must reproduce the above copyright notice, 
 *   this list of conditions and the following disclaimer in the documentation 
 *   and/or other materials provided with the distribution.
 * - Neither the name of MechDAR nor the names of its contributors 
 *   may be used to endorse or promote products derived from this software 
 *   without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
 * THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * Input Packet Format:
 *  0xFF COMMAND CHECKSUM = (255 - (COMMAND))
 *        |
 *        1-24 = A READING
 *        27 = STOP
 *        28 = GO (output frames) 
 *
 * Output Packet Format:
 *  0xFF SENSOR READING CHECKSUM = (255-(SENSOR + READING)%255)
 *        |      | 
 *        |      Readings are 0-254 inches
 *        |        
 *        |
 *        0 = new frame (reading always = 1) 
 *        1 = left IR
 *        2 = right IR
 *        3 = left rear IR
 *        4 = right rear IR
 *        5-14  = panning IR (5 = -90deg, 14=+90deg)
 *        25 = end frame (reading always = 1)
 * 
 * Program Structure:
 *  A system clock, running at 20Hz, triggers an interrupt which moves the
 *  servo and takes readings.  
 * 
 * Revisions:
 *  1. 
 */

#define FALSE           0
#define TRUE            1

// Robot specific port definitions
#define PIN_SERVO       0x09        // PB[1] - PANNING SERVO
#define PIN_NO_RX       0x0A        // PB[2] - JUMPER TO GROUND TO DISABLE RX

#define PIN_PAN_IR      0x10        // PC[0] - GP2DY0A2YK
#define PIN_LEFT_IR     0x11        // PC[1] - GP2D12
#define PIN_RIGHT_IR    0x12        // PC[2] - GP2D12
#define PIN_L_REAR_IR   0x13        // PC[3] - GP2D12 
#define PIN_R_REAR_IR   0x14        // PC[4] - GP2D12

#define NEW_FRAME       0 
#define REG_LEFT_IR     1
#define REG_RIGHT_IR    2
#define REG_L_REAR_IR   3
#define REG_R_REAR_IR   4
#define REG_PAN_BASE    5
#define REG_SNR_BASE    15
#define END_FRAME       25 
#define REG_STOP        27
#define REG_GO          28       

#include <avr/interrupt.h>
#include "avrra/dev/mini.h"
#include "avrra/serial.h"
#include "avrra/analog.h"
#include "avrra/sharpir.h"          // special sharpir in inches...
#include "avrra/servo.h"
	
volatile unsigned char count;       // count of where servo is located
volatile unsigned char TXgo;        // Should we transmit
volatile unsigned long systime;	    // system uptime (60 hz)

int data[10];       // Data frame of 10 IR readings from forward sensor

/** sendPacket() - Helper function that tries to send a packet containing a 
      sensor ID and reading. */
void sendPacket(unsigned char sensor, unsigned char reading){
    serialWrite(0xFF);
    serialWrite(sensor);
    serialWrite(reading);
    serialWrite(0xFF-((sensor+reading)%255));
}

/** finishFrame() - send the end of a frame. */
void finishFrame(){
    // send side and rear readings
    sendPacket(REG_LEFT_IR,gp2d12GetData(PIN_LEFT_IR));
    sendPacket(REG_RIGHT_IR,gp2d12GetData(PIN_RIGHT_IR));
    sendPacket(REG_L_REAR_IR,gp2d12GetData(PIN_L_REAR_IR));
    sendPacket(REG_R_REAR_IR,gp2d12GetData(PIN_R_REAR_IR));
    // send the IR part of the data frame
    for(count=0;count<10;count++){
        sendPacket(REG_PAN_BASE + count, data[count]);
    }
    // end of frame
    sendPacket(END_FRAME,1);      // end of frame
}             

/** startFrame() - send the beginning of new frame */
void startFrame(){
    sendPacket(NEW_FRAME,1);      // start of frame
}

/** main() - where all the setup happens. */
int main(){
    int RXbypass;       // Bypass rx?
    unsigned char input, checksum;
    serialInit(115200); // Startup serial port
    // setup variables
    count = 0;
    servoSetPosition(PIN_SERVO, -80);

    // setup sensors
    gp2longInit(PIN_PAN_IR);
    gp2d12Init(PIN_LEFT_IR);
    gp2d12Init(PIN_RIGHT_IR);    
    gp2d12Init(PIN_L_REAR_IR);
    gp2d12Init(PIN_R_REAR_IR);
    servoInit(PIN_SERVO,-15,1);

    // RX bypass enabled?
    digitalSetDirection(PIN_NO_RX, AVRRA_INPUT);
    digitalSetData(PIN_NO_RX, AVRRA_HIGH);
    if(digitalGetData(PIN_NO_RX) == AVRRA_LOW){
        // bypass RX;
        RXbypass = TRUE;
        TXgo = TRUE;        
        startFrame();
        delayms(5000);
    }else{        
        RXbypass = FALSE;
        Print("MechDAR V1.0 Alive\n");
        TXgo = FALSE;
    }

    // setup a 60Hz clock on Timer/Counter 2
    TCNT2 = 0;
	OCR2A = 240;			// this defines 60 Hz Clock
	TCCR2A = 0x03;          // no A|B compare, mode7 fast pwm
	TCCR2B = 0x0F;          // clock/1024
	TIMSK2 |= 0x01; 		// interrupt on overflow

    // start clock
    sei();
    while(1){   
        if((RXbypass == FALSE) && (serialAvailable() > 0)){
            // process incoming
            if(serialRead() == -1){ // 0xFF
                while(serialAvailable() == 0);
                input = (unsigned char) serialRead();
                while(serialAvailable() == 0);
                checksum = (unsigned char) serialRead();
                PrintNumber(input);
                PrintNumber(checksum);
                // if a valid packet...
                if((255 - ((input + checksum)%256)) == 0){
                    // process the data
                    switch(input){
                        case REG_LEFT_IR:
                            PrintNumber(gp2d12GetData(PIN_LEFT_IR));
                            Print("\n");
                            break;
                        case REG_RIGHT_IR:
                            PrintNumber(gp2d12GetData(PIN_LEFT_IR));
                            Print("\n");
                            break;
                        case REG_L_REAR_IR:
                            PrintNumber(gp2d12GetData(PIN_LEFT_IR));
                            Print("\n");
                            break;
                        case REG_R_REAR_IR:
                            PrintNumber(gp2d12GetData(PIN_LEFT_IR));
                            Print("\n");
                            break;
                        case REG_STOP:
                            TXgo = FALSE;
                            break;
                        case REG_GO:
                            TXgo = TRUE;
                            startFrame();
                            break;
                        default:
                            // Send a reading from the data frame                            
                            PrintNumber(data[(input-REG_PAN_BASE)%10]); 
                            Print("\n");
                            break;
                    }
                }                
            }                    
        }
        asm("nop");
    }
    return 0;
};

/** isr() - updates systime, on interrupt. */
ISR(TIMER2_OVF_vect){
	systime++;
    if(((systime % 3) == 0) && (TXgo == TRUE)){
        // record value of IR, where the servo is
        if(count < 10){
            data[count] = gp2longGetData(PIN_PAN_IR);
        }else{
            data[9-(count%10)] = gp2longGetData(PIN_PAN_IR); 
        }
        // update count
        count++;
        // get servo moving 
        if(count < 10){
            servoSetPosition(PIN_SERVO, -80 + (count*18));        
        }else if(count < 20){ 
            servoSetPosition(PIN_SERVO, 80 - ((count%10)*18));
        }else{  // count == 20 == 0
            servoSetPosition(PIN_SERVO, -80);
        }
        // send frame data, if neccessary
        if(count == 10){
            finishFrame();
            startFrame();
        }else if(count == 20){
            finishFrame();
            startFrame();        
            count = 0;      
        }
    }
}
