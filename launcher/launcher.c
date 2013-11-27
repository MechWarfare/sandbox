/********************** Mech-Warfare Rocket Launcher VA.0 *********************
 * 
 * Rocket launcher takes a servo input. On reset, it must recieve a 900ms pulse
 *  to arm itself. Then, the servo input should be held at 1300ms for at least 
 *  half a second. To fire, the pulse should go to 2000ms, and must pass back to 
 *  1300ms before firing again. 
 * 
 * Electrical Connections
 *  PB0|MOSI - Ch0
 *  PB1|MISO - Ch1
 *  PB2|SCK|INT0 - Servo pulse 
 *  PB3 - Ch3
 *  PB4 - Ch2
 *  PB5 - Reset
 * 
 * Copyright (c) 2008-2009, Michael E. Ferguson
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms is under a BSD License
 *****************************************************************************/

#include <avr/io.h>

/** modes **/
#define MODE_UNARMED    0
#define MODE_ARMED      1
#define MODE_FIRED      2
/** which channels have been fired **/
#define CHANNEL0        0x10
#define CHANNEL1        0x20
#define CHANNEL2        0x40
#define CHANNEL3        0x80

/** main function */
int main(){
    unsigned char mode = MODE_UNARMED;
    unsigned long width = 0;
    // setup pin directions, 4 outgoing channels, CH 1&3 need to be held high
    // DDRB = 0x1B; do this below....?

    while(1){	

	    // wait for any previous pulse to end
	    while ((PINB & 0x04) == 0x04);
	    // wait for the pulse to start
	    while ((PINB & 0x04) == 0x00);
	    // wait for the pulse to stop
        while ((PINB & 0x04) == 0x04)
            width++;

	    // convert the reading to microseconds. The loop has been determined
	    // to be 10 clock cycles long and have about 16 clocks between the edge
	    // and the start of the loop. There will be some error introduced by
	    // the interrupt handlers.
        // 8MHz = 8clock cycles per microsecond
	    width = (width * 10 + 16)/8;

        // now do something with this 
        switch(mode&0x0F){
            case MODE_UNARMED:
                if((width > 900) && (width < 1100))
                    mode |= MODE_ARMED;
                break;
            case MODE_ARMED:
                if((width > 1900) && (width < 2100)){
                    if(mode > CHANNEL2){
                        // fire channel 3
                        PORTB = 0x00;
                        DDRB |= 0x02;
                        mode |= CHANNEL3;
                    }else if(mode > CHANNEL1){
                        // fire channel 2  
                        PORTB = 0x10;
                        DDRB |= 0x10;
                        mode |= CHANNEL2;
                    }else if(mode > CHANNEL0){
                        // fire channel 1
                        PORTB = 0x00;
                        DDRB |= 0x02; 
                        mode |= CHANNEL1;
                    }else{
                        // fire channel 0
                        PORTB |= 0x01;
                        DDRB |= 0x01;
                        mode |= CHANNEL0;
                    }
                }
                mode &= ~MODE_ARMED;
                mode |= MODE_FIRED;
                break;
            case MODE_FIRED:
                if((width < 1400) && (width > 1200))
                    mode &= ~MODE_FIRED;
                    mode |= MODE_ARMED;
                break;
        } // end switch(mode)  
        width = 0;       
    }    
}

