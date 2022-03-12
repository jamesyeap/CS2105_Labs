import sys
from socket import *
import hashlib
import zlib

# request method codes
REQUEST_CONNECTION = 'STID_';

# ---- HELPER FUNCTIONS -------------------------------------------------------

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

def get_response_message(socket):
	return socket.recv(1024);

# ---- CONNECTION FUNCTIONS -------------------------------------------------------

def wait_for_turn(socket):
	queue_len = get_response_message(socket);

	while (True):
		if (queue_len == b'0_'):
			break;
			
		queue_len = get_response_message(socket);

# ----- RECEIVE PACKET FUNCTIONS ---------------------------------------------

def is_corrupted(packet_data, packet_checksum):
	generated_checksum = zlib.crc32(packet_data);

	return generated_checksum != packet_checksum;

PACKET_HEADER_SEQNUM_SIZE = 6;
PACKET_HEADER_CHECKSUM_SIZE = 10;
PACKET_HEADER_LENGTH_SIZE = 4;

def get_message_until_size_reached(socket, total_length):
	data = b'';
	length_received = 0;

	while (True):
		incoming_data = socket.recv(1);

		if (length_received == total_length):
			break;

		data = data + incoming_data;
		total_length = total_length + length_received;

	return data;

def get_packet_seqnum(socket):
	return get_message_until_size_reached(socket, PACKET_HEADER_SEQNUM_SIZE);

def get_packet_checksum(socket):
	return get_message_until_size_reached(socket, PACKET_HEADER_CHECKSUM_SIZE);

def get_packet_length(socket):
	return get_message_until_size_reached(socket, PACKET_HEADER_LENGTH_SIZE);

def get_packet_header(socket):
	seqnum = int(get_packet_seqnum(socket).decode());
	checksum = int(get_packet_checksum(socket).decode());
	length = int(get_packet_length(socket).decode());

	return seqnum, checksum, length;

def get_packet(socket):
	seqnum, checksum, length = get_packet_header();

	packet_data = get_message_until_size_reached(socket, total_length);

	if (is_corrupted(packet_data, checksum)):
		# TODO: send_nack(seqnum)
		# TODO: return None;

	return packet_data;

# ----- MAIN -----------------------------------------------------------------

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
clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key + '_C'));
wait_for_turn(clientSocket);

""" open the file where the hash is to be written to, if the file doesn't exist, create it """
output_fd = open(output_file_name, 'wb');

while (True):
	packet = clientSocket.recv(1024);
	output_fd.write(packet);

	if (len(packet) == 0):
		break;

output_fd.close();
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