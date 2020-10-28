
######
######   What are we building?
######

TARGET = main

# Objects that must be built in order to link
OBJECTS = main.o
OBJECTS += magnetometer.o


######
######   Binaries and flags
######

#INCDIRS = -I/usr/local/include

#CFLAGS = $(INCDIRS)

LD = gcc
#LDFLAGS = -L/usr/local/lib
#LDLIBS = -lsiftgpu



######
######   Targets and Rules
######
# Default target:
.PHONY: all
all: $(TARGET)


$(TARGET): $(OBJECTS)
	$(LD) $(LDFLAGS) $(OBJECTS) -o $@ $(LDLIBS)


.PHONY: clean
clean:
	rm -f $(OBJECTS)
	rm -f $(TARGET)

