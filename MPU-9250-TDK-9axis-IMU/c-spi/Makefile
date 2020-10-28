
######
######   What are we building?
######

TARGET = mpu9250_simple

# Objects that must be built in order to link
OBJECTS = main.o
OBJECTS += mpu9250_accel_and_gyro.o


######
######   Binaries and flags
######

#INCDIRS = -I/usr/local/include
#CFLAGS = $(INCDIRS)

LD = gcc
#LDFLAGS = -L/usr/local/lib
#LDLIBS = -lm


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

