# MakeFile for Mech Wars Launcher
#
# on the command line:
#   make all      - build the program
#   make clean    - remove all built files
#   make program  - download program (using AVRDUDE defines below)
#   make setfuse  - set fuse bits (using AVRDUDE defines below)
#	make size	  - run avr-size on .elf file
#
# stuff you may want to edit:
#
#   PRG         - the name of the program
#   SRC         - the list of C files to be compiled
#   MCU_TARGET  - the microprocessor for which we're building
#
#   AVRDUDE_PART        - AVRDUDE's part id for the microprocessor
#   AVRDUDE_PROGRAMMER  - the programmer used for downloading
#   AVRDUDE_PORT        - the port the programmer is plugged into
#
# revisions:
#   02-07-08	added avr-size option

PRG            = launcher
SRC            = launcher.c 
MCU_TARGET     = attiny25
F_CPU 		   = 8000000

OBJ            = $(SRC:.c=.o)
OPTIMIZE       = -Os
DEFS           =
LIBS           =

# compile of .c auto with $(CC) -c $(CPPFLAGS) $(CFLAGS)
# compile of .cpp auto with (CXX) -c $(CPPFLAGS) $(CXXFLAGS)
CC             = avr-gcc
CXX            = avr-g++

# Override is only needed by avr-lib build system.
override CFLAGS        = -g -Wall $(OPTIMIZE) -mmcu=$(MCU_TARGET) $(DEFS)
override CPPFLAGS      = -g -Wall $(OPTIMIZE) -mmcu=$(MCU_TARGET) $(DEFS)
override LDFLAGS       = -Wl,-Map,$(PRG).map

OBJCOPY        = avr-objcopy
OBJDUMP        = avr-objdump
AVRDUDE        = avrdude     # for downloading

# AVRDUDE definitions; 
AVRDUDE_PART       = t25
ifndef AVRDUDE_PROGRAMMER
AVRDUDE_PROGRAMMER = stk500v2
endif
ifndef AVRDUDE_PORT
AVRDUDE_PORT       = /dev/ttyS0 
endif
AVRDUDE_FLAGS      = -p $(AVRDUDE_PART) -c $(AVRDUDE_PROGRAMMER) -P $(AVRDUDE_PORT) 

# (this is the default rule since it's first)
#all: $(PRG).elf bin
all: $(PRG).elf lst bin

clean:
#	rm -rf *.o $(PRG).elf *.bin
	rm -rf *.o $(PRG).elf *.lst *.map *.bin
	
size:
	avr-size $(PRG).elf

program: $(PRG).bin
	avrdude $(AVRDUDE_FLAGS) -e -U flash:w:$(PRG).bin:r

# make sure fuse bits are set:
#  CKSEL3:0 = 0010 8.0MHz
#  SUT1:0   = 10   slow rising power
setfuse:
	avrdude $(AVRDUDE_FLAGS) -u -U lfuse:w:0xF7:m
	avrdude $(AVRDUDE_FLAGS) -u -U hfuse:w:0xD7:m

# binary file (to download to robot)
bin:  $(PRG).bin

$(PRG).elf: $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LIBS)

%.bin: %.elf
	$(OBJCOPY) -j .text -j .data -O binary $< $@

# code/asm listing
lst:  $(PRG).lst

%.lst: %.elf
	$(OBJDUMP) -h -S $< > $@
