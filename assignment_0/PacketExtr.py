import sys

def main():
	while True:
		# get the size of the packet (in bytes)
		#	from the packet-header
		packetSize = readHeader()

		# if no packet-header is found,
		#	stop processing data
		if (packetSize == -1):
			break

		# read the packet-payload
		readPayload(packetSize)

def readHeader():
	# read-in "Size: " first
	data = sys.stdin.buffer.read1(6)	

	# if the start of a packet-header cannot be found,
	#	then there are no more packets to read
	if (len(data) == 0):
		return -1

	# read-in "______B", where "______" is an integer
	#	that ranges from 0 to 1048576
	x = sys.stdin.buffer.read1(1)
	y = b''

	# read-in a single byte, x, at a time,
	# 	appending the x to the
	# 	bytes-object y that represents the size of the packet
	# 	until 'B' is reached 
	#	(note: don't append 'B' to the bytes-object)
	while (x != b'B'):
		y += x 
		x = sys.stdin.buffer.read1(1)		

	# convert the byte-representation of the
	#	packet size into a decimal number
	packetSize = int(y)

	return packetSize

def readPayload(packetSize):
	numBytesLeft = packetSize

	while (numBytesLeft > 0):
		payload = sys.stdin.buffer.read1(numBytesLeft)
		numBytesLeft -= len(payload)

		sys.stdout.buffer.write(payload)	
		sys.stdout.buffer.flush()
		
if __name__ == "__main__":
	main()