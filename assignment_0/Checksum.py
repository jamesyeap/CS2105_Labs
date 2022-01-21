import sys
import zlib

def main():
	# get the relative-path of the target file
	filepath = sys.argv[1]

	# open the file in binary-reading mode
	file = open(filepath, "rb")

	# read data from the file
	bytes = file.read();

	# calculate the CRC-32 checksum for the file
	checksum = zlib.crc32(bytes)

	# print the unsinged 32-bit checksum
	print(checksum);

if __name__ == "__main__":
	main()