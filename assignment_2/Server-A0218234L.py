import sys
from socket import *
import hashlib
import zlib

# request method codes
REQUEST_CONNECTION = 'STID_';

# ---- HELPER FUNCTIONS ------------------------------------------------------

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

def get_response_message(socket):
	return socket.recv(64);

# ---- CONNECTION FUNCTIONS -------------------------------------------------------

def wait_for_turn(socket):
	queue_len = get_response_message(socket);

	while (True):
		if (queue_len == b'0_'):
			break;

		print(queue_len); # TO REMOVE
		queue_len = get_response_message(socket);

# ----- GENERATE PACKET FUNCTIONS --------------------------------------------

PACKET_HEADER_INDICATOR_INCOMING_PACKET = b'P';
PACKET_HEADER_INDICATOR_END_TRANSMISSION = b'E';

PACKET_HEADER_SEQNUM_SIZE = 6;
PACKET_HEADER_CHECKSUM_SIZE = 10;
PACKET_HEADER_LENGTH_SIZE = 4;

def generate_seqnum_header(curr_seqnum):
	# print(str(curr_seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0'));

	return str(curr_seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0');

def generate_checksum_header(data):
	checksum = zlib.crc32(data);

	# print(str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0'));

	return str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0');

def generate_length_header(data_length):
	# print(str(data_length).encode().rjust(PACKET_HEADER_LENGTH_SIZE, b'0'));

	return str(data_length).encode().rjust(PACKET_HEADER_LENGTH_SIZE, b'0');

def generate_packet(seqnum_header, checksum_header, length_header, data):
	return PACKET_HEADER_INDICATOR_INCOMING_PACKET + seqnum_header + checksum_header + length_header + data;

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
clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key + '_S'));
wait_for_turn(clientSocket);

""" open the file to be sent """
input_fd = open(input_file_name, 'rb');

"""
while (True):
	packet = input_fd.read(1024);

	if (len(packet) == 0):
		break;

	clientSocket.send(packet);
"""

MAX_PACKET_SIZE = 1024;
MAX_PACKET_DATA_SIZE = MAX_PACKET_SIZE - 1 - (PACKET_HEADER_SEQNUM_SIZE + PACKET_HEADER_CHECKSUM_SIZE + PACKET_HEADER_LENGTH_SIZE);

curr_seqnum = 0;
while (True):

	data_payload = input_fd.read(MAX_PACKET_DATA_SIZE);
	data_payload_length = len(data_payload);

	print(data_payload_length);

	if (data_payload_length == 0):
		clientSocket.send(PACKET_HEADER_INDICATOR_END_TRANSMISSION);
		print("ALL DATA SENT")
		break;

	seqnum_header = generate_seqnum_header(curr_seqnum);
	checksum_header = generate_checksum_header(data_payload);
	length_header = generate_length_header(data_payload_length);

	packet = generate_packet(seqnum_header, checksum_header, length_header, data_payload);

	clientSocket.send(packet);
	curr_seqnum = curr_seqnum + 1;

clientSocket.close();












""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================
- my student-key is 651723
- to test the code,
	python3 Server-A0218234L.py 651723 0 137.132.92.111 4445 hello.txt
"""