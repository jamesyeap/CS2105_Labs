import sys

def main():
	hasNextPacket = True

	while hasNextPacket == True:
		hasNextPacket = readPacket()

def readPacket():
	data = sys.stdin.buffer.read1(14)

	if (len(data) == 0):
		return False

	# find the header and payload segments of the header
	headerEnd = data.find(b'B')
	header = data[0:headerEnd+1]
	payload = data[headerEnd+1:]

	# find the size of the packet from the header
	packetSize = 0
	headerSizeStart = header.find(b' ')
	headerSizeEnd = header.find(b'B')
	if headerSizeStart >= 0 & headerSizeEnd >= 0:
		packetSize = int(header[headerSizeStart : headerSizeEnd].decode());

	# write-out the rest of the bytes in the payload
	while packetSize > 0:
		sys.stdout.buffer.write(payload)	
		sys.stdout.buffer.flush()
		
		packetSize = packetSize - len(payload)
		
		if packetSize == 0:
			break

		payload = sys.stdin.buffer.read1(packetSize)

	return True
		
if __name__ == "__main__":
	main()

# Max header-case:
	# 	"Size: 1048576B"