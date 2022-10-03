
#include <stdio.h>
#include <stdint.h>

uint16_t createCRC(uint8_t* Data, uint16_t Size)
{
	uint16_t crc = 0;

	for (uint32_t i = 0; i < Size; ++i)
	{

		uint16_t code = crc >> 8;
		code ^= Data[i];
		code ^= code >> 4;
		crc = crc << 8;
		crc ^= code;
		code = code << 5;
		crc ^= code;
		code = code << 7;
		crc ^= code;
	}

	return crc;
}

int main(int argc, char* argv[]) {

	char aTestA[] = {0x22, 0x04, 0x69};
	char aTestB[] = {0x12, 0x31, 0x00, 0xff, 0xff, 0xab};
	char aTestC[] = {0x31, 0x00, 0xff, 0xff, 0xab};

	uint16_t myCrcA = createCRC(aTestA, 3);
	uint16_t myCrcB = createCRC(aTestB, 6);
	uint16_t myCrcC = createCRC(aTestC, 5);

	printf("crcA: %x\n", myCrcA);
	printf("crcB: %x\n", myCrcB);
	printf("crcC: %x\n", myCrcC);

	return 0;

}
