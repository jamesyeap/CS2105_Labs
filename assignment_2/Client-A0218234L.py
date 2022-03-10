import sys
from socket import *
import hashlib
import zlib

# ---- CONNECTION FUNCTIONS --------------------------------------------------

def send_connection_request(socket, student_key):
	print('[SENDING REQUEST MESSAGE] ' + 'STID_' + student_key + '_C'); # TO REMOVE
	socket.send(('STID_' + student_key + '_C').encode());

def get_response_message(socket):
	return socket.recv(1024);

def wait_for_turn(socket):
	queue_len = get_response_message(socket);
	print("[QUEUE_LENGTH]: " + str(queue_len)); # TO REMOVE

	while (True):
		if (queue_len == b'0_'):
			break;

		print("[QUEUE_NUMBER]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);


# ---- PACKET RECEIVE FUNCTIONS --------------------------------------------------

PACKET_HEADER_SEQNUM_SIZE = 32;
PACKET_HEADER_CHECKSUM_SIZE = 16;
MAX_PACKET_SIZE = 1024;

def get_packet_header_seqnum(socket):
	data = socket.recv(PACKET_HEADER_SEQNUM_SIZE);

	if (len(data) == 0):
		return (b'1', True);

	print("[NUM BYTES RECEIVED FOR SEQNUM]: "+ str(len(data)));

	return (int(data.decode()), False);

def get_packet_header_checksum(socket):
	data = socket.recv(PACKET_HEADER_CHECKSUM_SIZE);

	print("[NUM BYTES RECEIVED FOR CHECKSUM]: "+ str(len(data)));

	return int(data.decode());

def get_packet_data(socket):
	data = socket.recv(MAX_PACKET_SIZE - PACKET_HEADER_SEQNUM_SIZE - PACKET_HEADER_CHECKSUM_SIZE);

	print("[NUM BYTES RECEIVED FOR PACKET DATA]: "+ str(len(data)));

def data_is_not_corrupted(data, checksum):
	dataChecksum = zlib.crc32(data);

	return dataChecksum == checksum;

def get_packet(socket):
	incoming_seqnum, has_no_more_packets = get_packet_header_seqnum(socket);
	incoming_checksum = get_packet_header_checksum(socket);
	incoming_data = get_packet_data(socket);

	print("[HAS NO MORE PACKETS?]: " + str(has_no_more_packets));

	return incoming_seqnum, incoming_checksum, incoming_data, has_no_more_packets;

def send_ack(socket, next_expected_seqnum):
	ackMessage = ("A" + str(next_expected_seqnum)).encode();
	socket.send(ackMessage);

def send_nack(socket, required_seqnum):
	nackMessage = ("B" + str(required_seqnum)).encode();
	socket.send(nackMessage);

# ------ MAIN ----------------------------------------------------------------

""" STEP 1
	1. readin input params
	2. open the file where the hash is to be written to
		if the file doesn't exist, create it
	3. create an instance of the MD5 hasher
"""
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

file_to_write_to = open(output_file_name, 'w+');
hasher = hashlib.md5();

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
	1. start reading-in packets sent from the server
"""
cumulative_seqnum = 0;

while (True):
	incoming_seqnum, incoming_checksum, incoming_data, has_no_more_packets = get_packet(clientSocket);

	print("[HAS NO MORE PACKETS?]: " + str(has_no_more_packets));

	if (has_no_more_packets == True):
		break;

	if (data_is_not_corrupted(incoming_data, incoming_checksum)):

		# send successful acknowledgement to server
		send_ack(clientSocket, incoming_seqnum);

		# increment cumulative seqnum
		length_of_data = len(incoming_data);
		cumulative_seqnum = cumulative_seqnum + length_of_data;

		# "deliver" data
		hasher.update(incoming_data);

	else:
		send_nack(clientSocket, incoming_seqnum);

""" STEP 4
	1. get the MD5 hash of the file received from server
	2. write the hash to the output file specified
	3. close the output file
	4. close the client socket
"""
file_to_write_to.write(hasher.hexdigest());
file_to_write_to.close();
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