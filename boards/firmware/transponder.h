/* 
 * Mech Warfare 2011
 * Scoring Transponders
 * Common Definitions
 */

// 2011 Transponder Reservations
//#define TRANSPONDER_ID   70    // Michael Ferguson, Issy2
//#define TRANSPONDER_ID   73    // Andrew Alter, Giger
//#define TRANSPONDER_ID   76    // Andrew Alter, Axeman
//#define TRANSPONDER_ID   79    // Mike Grundvig, Nostromo
//#define TRANSPONDER_ID   82    // Gary Warren, Bheka
//#define TRANSPONDER_ID   85    // Che Edoga, Aphid
#define TRANSPONDER_ID   88    // Ryan Lowerr, Second Amendment
//#define TRANSPONDER_ID   91    // Manny Ramirez, Clyde
//#define TRANSPONDER_ID   94    // Mathew Tsz Kiu Chan, RoboLoo
//#define TRANSPONDER_ID   97    // Seth Cook, Jeff (really, the bot's name is JEFF)
//#define TRANSPONDER_ID   100   // Robert E. Reynolds, ShadowCat
//#define TRANSPONDER_ID   103   // Darrell Taylor, Miss Alignment
//#define TRANSPONDER_ID   106   // Kevin Quigley, ?
//#define TRANSPONDER_ID   109   // Phillip Quebe, BOo
//#define TRANSPONDER_ID   112   // Scott Monsma, 
//#define TRANSPONDER_ID   115   // Matthew Lumpen, Nomous
//#define TRANSPONDER_ID   118   // Jim Frye, Hunchback
//#define TRANSPONDER_ID   121   // Connor, Odin
//#define TRANSPONDER_ID   124   // Edward Lee, LoTech
//#define TRANSPONDER_ID   127   // Team Mexico, Graves
//#define TRANSPONDER_ID    130  // Mark Ethridge
//#define TRANSPONDER_ID    133  // Mark Ethridge
//#define TRANSPONDER_ID    136  // David Fong, RA (R-Team Robotics Club)
//#define TRANSPONDER_ID    139  // Eric Diehr, Immortal (cire)
//#define TRANSPONDER_ID    142  // Manny Ramirez, Musa
//#define TRANSPONDER_ID    145  // Aaron Morand, Woodstock (Kamondelious) 
//#define TRANSPONDER_ID    148  // Ben Israeli 
//#define TRANSPONDER_ID    151  // Jesse Merritt, Ordog-6
//#define TRANSPONDER_ID    154  // Pryde, Khaos
//#define TRANSPONDER_ID    157  // Pryde, Orcus
//#define TRANSPONDER_ID    160  // Pryde, Pestilence
//#define TRANSPONDER_ID    163  //
//#define TRANSPONDER_ID    166  //
//#define TRANSPONDER_ID    169  // Team Indonesia, DU116 RP
//#define TRANSPONDER_ID    172  // Juan Damian, IG-88 (Team Avatar)
//#define TRANSPONDER_ID    175  // Mitchel Thompson
//#define TRANSPONDER_ID    178  // George Collins
//#define TRANSPONDER_ID    181  // Che Edoga, 
//#define TRANSPONDER_ID    184  // Ryan Lowerr, Gold Rush
//#define TRANSPONDER_ID    187  // Eric Laughlin, Draco 08

#define TIMEOUT          1000
#define BAUDRATE         38400

/* Which panel has been hit */
volatile int hit;

#ifdef MICRO_TRANSPONDER
  #define LED_OFF          (PORTA|=0x80);(PORTB|=0x01)
  #define LED_ON           (PORTA&=0x7F);(PORTB&=0xFE)
  #define SIGNAL_HIGH      (PORTB|=0x04)
  #define SIGNAL_LOW       (PORTB&=0xFB)
#else
  #define LED_OFF          digitalWrite(9,LOW)
  #define LED_ON           digitalWrite(9,HIGH)
  #define SIGNAL_HIGH      digitalWrite(12,HIGH)
  #define SIGNAL_LOW       digitalWrite(12,LOW)
#endif

