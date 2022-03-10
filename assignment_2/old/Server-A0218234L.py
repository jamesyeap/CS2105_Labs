import sys
from socket import *
import hashlib
import zlib

# request method codes
REQUEST_CONNECTION = 'STID_';

""" ---- HELPER FUNCTIONS -------------------------------------------------- """

def send_connection_request(socket, student_key):
	print('[SENDING REQUEST MESSAGE] ' + 'STID_' + student_key); # TO REMOVE
	socket.send(('STID_' + student_key + '_S').encode());

def get_response_message(socket):
	return socket.recv(64);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print(queue_len); # TO REMOVE

	while (True):
		if (queue_len == b'0_'):
			break;

		print("[QUEUE_NUMBER]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);


""" ---- PACKET CREATION FUNCTIONS ------------------------------------------- """

PACKET_HEADER_SEQNUM_SIZE = 32;
PACKET_HEADER_CHECKSUM_SIZE = 16;
MAX_PACKET_SIZE = 1024;

def make_seqnum_header(seqnum):
	seqnum_header = str(seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0');

	return seqnum_header;

def make_checksum_header(data):
	checksum = zlib.crc32(data);
	checksum_header = str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0');

	return checksum_header;

def make_packet(data, seqnum):
	packet_header = make_seqnum_header(seqnum) + make_checksum_header(data);

	return packet_header + data; 

# ------ MAIN ----------------------------------------------------------------

""" readin input params """
student_key = sys.argv[1]; 		# get student key to establish connection with server
mode = sys.argv[2]; 			# get the simulator mode
ip_address = sys.argv[3]; 		# get the IP address of the machine running the simulators
port_num = int(sys.argv[4]); 	# get the port number of the TCP socket of the simulator on the machine
input_file_name = sys.argv[5];  # get the name of the file to write the hash to

print("[PARAM - STUDENT_KEY]: " + student_key);
print("[PARAM - MODE]: " + mode);
print("[PARAM - IP_ADDRESS]: " + ip_address);
print("[PARAM - port_num]: " + str(port_num));
print("[PARAM - INPUT_FILE_NAME]: " + input_file_name);

""" create client TCP socket
	connect to the remote TCP socket
	request connection
	wait for our turn 
"""
clientSocket = socket(AF_INET, SOCK_STREAM);
clientSocket.connect((ip_address, port_num));
send_connection_request(clientSocket, student_key);
wait_for_turn(clientSocket);

""" open the file to be sent
"""
filetosend = open(input_file_name, 'rb');

seqNum = 0;
while (True):

	dataToSend = filetosend.read(MAX_SIZE_OF_DATA);
	num_bytes_of_data = len(dataToSend);

	if (num_bytes_of_data == 0):
		break;

	packetToSend = make_packet(dataToSend, seqNum);
	clientSocket.send(packetToSend);

	seqNum = seqNum + num_bytes_of_data;
	# print("[NUM_BYTES_SENT]: " + str(seqNum));

clientSocket.close();












""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================

- my student-key is 651723

- to test the code,
	python3 Server-A0218234L.py 651723 0 137.132.92.111 4445 hello.txt


"""