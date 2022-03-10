import sys
from socket import *
import hashlib
import zlib

# request method codes
REQUEST_CONNECTION_HEADER = 'STID_';

""" ---- HELPER FUNCTIONS -------------------------------------------------- """

def send_connection_request(socket, student_key):
	print('[SENDING REQUEST MESSAGE] ' + 'STID_' + student_key); # TO REMOVE
	socket.send(('STID_' + student_key + '_C').encode());

def get_response_message(socket):
	return socket.recv(1024);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print(queue_len); # TO REMOVE

	while (True):
		if (queue_len == b'0_'):
			break;

		print("[QUEUE_NUMBER]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);

def send_ack(socket, nextExpectedSeqNum):
	ackMessage = ("A" + str(nextExpectedSeqNum)).encode();
	socket.send(ackMessage);

def send_nack(socket, requiredSeqNum):
	nackMessage = ("B" + str(requiredSeqNum)).encode();
	socket.send(nackMessage);

def get_packet_header_field(socket):
	data = b'';

	while (True):
		incomingData = socket.recv(1);

		if (len(incomingData) == 0):
			raise StopIteration('NO MORE DATA');

		if (incomingData == b'_'):
			break;

		data = data + incomingData;

	return data, len(data)+1; # include "_", which takes up 1 byte

def extract_packet_seqnum(socket):
	packetSeqNum, num_bytes_of_packet = get_packet_header_field(socket);

	print("[PACKET - SEQNUM]: " + packetSeqNum.decode());

	return int(packetSeqNum.decode()), num_bytes_of_packet;

def extract_packet_checksum(socket):
	packetCheckSum, num_bytes_of_packet = get_packet_header_field(socket);

	print("[PACKET - CHECKSUM]: " + packetCheckSum.decode());

	return int(packetCheckSum.decode()), num_bytes_of_packet;

def extract_packet_data(socket, length_of_data):
	packetData = socket.recv(length_of_data);

	return packetData, len(packetData);
	
def is_not_corrupted(data, packetCheckSum):
	dataReceivedCheckSum = zlib.crc32(data);

	return dataReceivedCheckSum == packetCheckSum;

def deliver(data, receiver):
	# in this assignment, the "receiver" is the md5 object
	receiver.update(data);

def receive_packet(socket, receiver, expectedSeqNum):
	packetSeqNum, seqNumLength = extract_packet_checksum(socket);
	packetCheckSum, checkSumLength = extract_packet_checksum(socket);
	packetData, num_bytes_received = extract_packet_data(socket, 1009);

	if (is_not_corrupted(packetData, packetCheckSum)):
		nextExpectedSeqNum = expectedSeqNum + num_bytes_received
		send_ack(socket, nextExpectedSeqNum);

		return nextExpectedSeqNum;
	else:
		send_nack(socket, expectedSeqNum);

		return expectedSeqNum;

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = int(sys.argv[4]); 	# get the port number of the TCP socket of the simulator on the machine
output_file_name = sys.argv[5]; # get the name of the file to write the hash to

print("[PARAM - STUDENT_KEY]: " + student_key);
print("[PARAM - MODE]: " + mode);
print("[PARAM - IP_ADDRESS]: " + ip_address);
print("[PARAM - port_num]: " + str(port_num));
print("[PARAM - OUTPUT_FILE_NAME]: " + output_file_name);

""" create client TCP socket
	connect to the remote TCP socket
	request connection
	wait for our turn 
"""
clientSocket = socket(AF_INET, SOCK_STREAM);
clientSocket.connect((ip_address, port_num));
send_connection_request(clientSocket, student_key);
wait_for_turn(clientSocket);

""" open the file where the hash is to be written to
	if the file doesn't exist, create it
"""
fileToWriteTo = open(output_file_name, 'w+');
hasher = hashlib.md5();

expectedSeqNum = 0;
while (True):
	try:
		expectedSeqNum = receive_packet(clientSocket, hasher, expectedSeqNum);
	except StopIteration:
		print('[NO MORE DATA TO RECEIVE]');
		break;

fileToWriteTo.write(hasher.hexdigest());

fileToWriteTo.close();
clientSocket.close();





















""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================

- my student-key is 651723

- to test the code:
	python3 Client-A0218234L.py 651723 0 137.132.92.111 4445 output.txt

- to run the reliable channel:
	On Terminal 1: (Client) ./test/FileTransfer.sh -i 651723 -n    
	On Terminal 2: (server) ./test/FileTransfer.sh -s -i 651723 -n

	change the last option to
		-e  for error channel
		-r   for reorder channel
		-A  for running all three tests.

- link to faq:
	https://docs.google.com/document/d/1biPpAvd8F7VPTqY2QDVU4XY4xfnWuTnRDM1VGq3usg8/edit#heading=h.65tkp2u5p4vz
	
"""