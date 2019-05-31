#include <stdlib.h>
#include <stdio.h>
#include <wiringSerial.h>
#include <wiringPi.h>

#define BIN_PATTERN "%c%c%c%c%c%c%c%c"
#define BYTE_TO_BINARY(byte) \
	(byte & 0x80 ? '1' : '0'), \
	(byte & 0x40 ? '1' : '0'), \
	(byte & 0x20 ? '1' : '0'), \
	(byte & 0x10 ? '1' : '0'), \
	(byte & 0x08 ? '1' : '0'), \
	(byte & 0x04 ? '1' : '0'), \
	(byte & 0x02 ? '1' : '0'), \
	(byte & 0x01 ? '1' : '0')


#define PORT "/dev/ttyAMA0"
#define BAUD 9600
#define HALF_BIT_DELAY 52
#define BIT_DELAY 104
#define NUM_BYTES 5
#define rx 10
#define tx 8

void loop();
bool readSonar(char []);
void readSonarByte(char *);
void printSonarMessage(char []);
void printSonarData(char []);


int fd;

int main() {
	fd = serialOpen(PORT, BAUD);
	wiringPiSetup();
	pinMode(rx, INPUT);
	pinMode(tx, OUTPUT);
	
	digitalWrite(tx, HIGH);

	loop();

	return 0;
} 

void loop() {
	char range[NUM_BYTES];
	bool invalidReading = readSonar(range);

	if (!invalidReading) 
		printSonarMessage(range);

	delay(100);
}

bool readSonar(char range[]) {
	int i = 0;
	bool invalid = false;
	
	readSonarByte(&range[0]);

	if (range[0] == 'R') {

		while (i < NUM_BYTES) 
			readSonarByte(&range[++i]);

	} else invalid = true;

	return invalid;
}

void readSonarByte(char *value) {
	*value = 0;

	while (digitalRead(rx) == 0);

	if (digitalRead(rx) == HIGH) {
		delayMicroseconds(HALF_BIT_DELAY);
		
		for (int bitShift = 0; bitShift < 7; bitShift++) {
			delayMicroseconds(BIT_DELAY);
			*value |= ((!digitalRead(rx)) << bitShift);
		}
		delayMicroseconds(BIT_DELAY);
	}
}

void printSonarMessage(char range[]) {
	range[NUM_BYTES-1] = 0;
	printf("%s\n", range);
}


void printSonarData(char range[]) {
	printf("\tCHAR\tHEX\tDEC\tBIN\n");
	for (int i = 0; i < NUM_BYTES; i++) {
		printf("%i\t", i);
		printf("%c\t", range[i]);
		printf("%02X\t", range[i]);
		printf("%d\t", (int) range[i]);
		printf(BIN_PATTERN, BYTE_TO_BINARY(range[i]));
		printf("\n");
	}
}






