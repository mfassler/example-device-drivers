

def createCRC(data):
    crc = 0

    for oneByte in data:
        assert oneByte >= 0
        assert oneByte <= 255

        code = crc >> 8
        code ^= oneByte & 0xff
        code ^= code >> 4
        crc = crc << 8 & 0xffff
        crc ^= code
        code = code << 5 & 0xffff
        crc ^= code
        code = code << 7 & 0xffff
        crc ^= code

    return crc


if __name__ == "__main__":
    crcA = createCRC([0x22, 0x04, 0x69])
    crcB = createCRC([0x12, 0x31, 0x00, 0xff, 0xff, 0xab])
    crcC = createCRC([0x31, 0x00, 0xff, 0xff, 0xab])

    print("crcA: %x" % (crcA))
    print("crcB: %x" % (crcB))
    print("crcC: %x" % (crcC))


