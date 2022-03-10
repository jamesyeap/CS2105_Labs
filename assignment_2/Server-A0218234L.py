import sys
from socket import *
import hashlib
import zlib

# ---- CONNECTION FUNCTIONS --------------------------------------------------

def send_connection_request(socket, student_key):
	print('[SENDING REQUEST MESSAGE] ' + 'STID_' + student_key + '_S'); # TO REMOVE
	socket.send(('STID_' + student_key + '_S').encode());

def get_response_message(socket):
	return socket.recv(64);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print("[QUEUE_LENGTH]: " + str(queue_len)); # TO REMOVE

	while (True):
		if (queue_len == b'0_'):
			break;

		print("[QUEUE_LENGTH]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);

""" ---- PACKET CREATION FUNCTIONS ------------------------------------------- """
PACKET_HEADER_SEQNUM_SIZE = 32;
PACKET_HEADER_CHECKSUM_SIZE = 16;

def make_seqnum_header(seqnum):
	seqnum_header = str(seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0');

	print("[OUTGOING SEQNUM]: " + str(seqnum));

	return seqnum_header;

def make_checksum_header(data):
	checksum = zlib.crc32(data);
	checksum_header = str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0');

	print("[OUTGOING CHECKSUM]: " + str(checksum));

	return checksum_header;

def make_packet(data, seqnum):
	packet_header = make_seqnum_header(seqnum) + make_checksum_header(data);

	return packet_header + data; 

# ------ MAIN ----------------------------------------------------------------

""" STEP 1
	1. readin input params
	2. open the file to be sent
"""
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

file_to_send = open(input_file_name, 'rb');

""" STEP 2
	1. create client TCP socket
	2. connect to the remote TCP socket
	3. request connection
	4. wait for our turn 
"""
clientSocket = socket(AF_INET, SOCK_STREAM);
clientSocket.connect((ip_address, port_num));
send_connection_request(clientSocket, student_key);
wait_for_turn(clientSocket);

""" STEP 3 (once it's our turn)
	1. create packet
	2. send packet to client

	repeat until no more data is to be sent
"""
MAX_PACKET_SIZE = 1024;
MAX_PACKET_DATA_SIZE = MAX_PACKET_SIZE - PACKET_HEADER_SEQNUM_SIZE - PACKET_HEADER_CHECKSUM_SIZE - 1;

cumulative_seqnum = 0;
while (True):
	data_to_send = file_to_send.read(MAX_PACKET_DATA_SIZE);
	length_of_data = len(data_to_send);

	if (length_of_data == 0):
		print('NO MORE PACKETS TO BE SENT');
		break;

	# we add an underscore to mark the end of the data-part
	packet = make_packet(data_to_send + b'_', cumulative_seqnum);
	clientSocket.send(packet);

	cumulative_seqnum = cumulative_seqnum + length_of_data;

""" STEP 4
	1. close the input file
	2. close the client socket
"""
file_to_send.close();
clientSocket.close();















""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================

- to run the reliable channel:
	On Terminal 1: (Client) ./test/FileTransfer.sh -i 651723 -n
	On Terminal 2: (server) ./test/FileTransfer.sh -s -i 651723 -n

	change the last option to
		-e  for error channel
		-r   for reorder channel
		-A  for running all three tests.

"""
	


