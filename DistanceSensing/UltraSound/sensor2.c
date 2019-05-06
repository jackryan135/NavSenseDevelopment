#include <stdlib.h>
#include <stdio.h>
#include <wiringSerial.h>
#include <wiringPi.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

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

int main() {

	int uart0_filestream = -1;
	uart0_filestream = open(PORT, O_RDWR | O_NOCTTY | O_NDELAY);

	if (uart0_filestream == -1) {
		printf("Error\n");
		exit(255);
	}

	struct termios options;
	tcgetattr(uart0_filestream, &options);

	options.c_cflag = B9600 | CS8 | CLOCAL | CREAD;
	options.c_iflag = IGNPAR;
	options.c_oflag = 0;
	options.c_lflag = 0;

	tcflush(uart0_filestream, TCIFLUSH);
	tcsetattr(uart0_filestream, TCSANOW, &options);

	while (1) {
		if (uart0_filestream != 1) {
			unsigned char rx_buffer[256];
			int rx_length = read(uart0_filestream, (void*)rx_buffer, 255);

			if (rx_length < 0) {
				printf("Error reading\n");
			} else if (rx_length == 0) {
				printf("no data waiting\n");
			} else {
				rx_buffer[rx_length] = '\0';
				printf("%i bytes read: %s\n", rx_length, rx_buffer);
			}
		}
	}

	return 0;

}
