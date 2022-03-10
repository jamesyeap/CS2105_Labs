import zlib

s = b'I am some data that you just read in';
checksum = zlib.crc32(s);

encodedCheckSum = str(checksum).encode();

checksum2 = int(encodedCheckSum.decode());

print(len(encodedCheckSum));