import sys

def main():
	# read in the packet
	data = sys.stdin.buffer.read1(-1);

	# split the packet into the
	# 	packet-header section and 
	#	binary-data payload section
	pos = data.find(b'B')
	if pos >= 0:
		header = data[0:pos+1]
		payload = data[pos+1:]
	else:
		

if __name__ == "__main__":
	main()