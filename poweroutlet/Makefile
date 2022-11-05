PROJECT_DEFINES := 

INCLUDE_PATHS := -I src -I ../libraries/arduino/ -I ../libraries/arduino/include -I ../libraries/common
CC := avr-gcc
CFLAGS := -std=gnu99 $(INCLUDE_PATHS) -Os -DF_CPU=16000000UL -mmcu=atmega328p -Wall $(WIFI_DEFINES) $(SOCKET_DEFINES) $(PROJECT_DEFINES)
LFLAGS := -std=gnu99 -mmcu=atmega328p -Wall $(WIFI_DEFINES) $(SOCKET_DEFINES) $(PROJECT_DEFINES)

SRC := $(shell cd src && ls *.c)
SRC_TMP := $(addprefix build/,$(SRC))

LIB_DIR := arduino common

LIB_SRC := $(foreach dir,$(LIB_DIR),$(shell ls ../libraries/$(dir)/src/*.c))
LIB_TMP := $(foreach src,$(LIB_SRC),$(lastword $(subst /, build/,$(src))))

OBJ := $(subst .c,.o,$(SRC_TMP)) $(subst .c,.o,$(LIB_TMP)) 

CRUFT := *.o *.elf

project:= power-outlet

all: project 

full: clean project

project: $(OBJ)
	@mkdir -p bin
	@echo "Building $(TARGET)..."
	$(CC) $(LFLAGS) -o ./build/$(TARGET).elf $(OBJ)
	avr-objcopy -O ihex -R .eeprom ./build/$(TARGET).elf bin/$(TARGET).hex

build/%.o: src/%.c | build_dir
	@echo "Compiling source code..."
	$(CC) $(CFLAGS) -o $@ -c $<

build/%.o: ../libraries/arduino/src/%.c | build_dir
	@echo "Compiling libraries..."
	$(CC) $(CFLAGS) -o $@ -c $<

build/%.o: ../libraries/common/src/%.c | build_dir
	@echo "Compiling libraries..."
	$(CC) $(CFLAGS) -o $@ -c $<

upload: 
	sudo avrdude -F -V -c arduino -p m328p -P /dev/ttyUSB0 -b 115200 -U flash:w:./bin/$(TARGET).hex:i

.PHONY: build_dir
build_dir:
	@mkdir -p build

.PHONY: clean
clean: 
	@echo "Cleaning..."
	rm -f ./bin/*
	rm -f $(foreach item,$(CRUFT),./build/$(item))
