import sys
from socket import *
import hashlib
import zlib
from enum import Enum

# request method codes
REQUEST_CONNECTION = 'STID_';

# ---- HELPER FUNCTIONS ------------------------------------------------------

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

def get_response_message(socket):
	return socket.recv(32);

# ---- CONNECTION FUNCTIONS -------------------------------------------------------

def wait_for_turn(socket):
	queue_len = get_response_message(socket);

	while (True):
		if (queue_len == b'0_'):
			break;

		print("[POSITION IN QUEUE]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);

# ----- IMPORTANT INFO -------------------------------------------------------

PACKET_HEADER_SEQNUM_SIZE = 6;
PACKET_HEADER_CHECKSUM_SIZE = 10;
PACKET_HEADER_LENGTH_SIZE = 4;

SERVER_PACKET_SIZE = 1024;
MAX_PACKET_DATA_SIZE = SERVER_PACKET_SIZE - (PACKET_HEADER_SEQNUM_SIZE + PACKET_HEADER_CHECKSUM_SIZE + PACKET_HEADER_LENGTH_SIZE);

CLIENT_PACKET_SIZE = 64;
CLIENT_PACKET_PADDING_SIZE = CLIENT_PACKET_SIZE - PACKET_HEADER_SEQNUM_SIZE - PACKET_HEADER_CHECKSUM_SIZE;

# ----- GENERATE PACKET FUNCTIONS --------------------------------------------

def generate_seqnum_header(seqnum):
	# print(str(seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0'));

	return str(seqnum).encode().rjust(PACKET_HEADER_SEQNUM_SIZE, b'0');

def generate_checksum_header(data):
	checksum = zlib.crc32(data);

	# print(str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0'));

	return str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0');

def generate_length_header(data_length):
	print(str(data_length).encode().rjust(PACKET_HEADER_LENGTH_SIZE, b'0'));

	return str(data_length).encode().rjust(PACKET_HEADER_LENGTH_SIZE, b'0');

def generate_packet(fd, seqnum):
	data = fd.read(MAX_PACKET_DATA_SIZE);
	data_length = len(data);

	seqnum_header = generate_seqnum_header(seqnum);
	checksum_header = generate_checksum_header(data);
	length_header = generate_length_header(data_length);

	packet = seqnum_header + checksum_header + length_header + data;

	return packet.ljust(SERVER_PACKET_SIZE, b'0');

# -------- RECEIVE ACK PACKET FUNCTIONS --------------------------------------

def get_message_until_size_reached(socket, total_length):
	data = b'';
	length_received = 0;

	while (True):
		if (length_received == total_length):
			break;

		incoming_data = socket.recv(total_length - length_received);
		incoming_data_length = len(incoming_data);

		data = data + incoming_data;
		length_received = length_received + incoming_data_length;

	return data;

def get_packet_ack_inbytes(socket):
	ack_inbytes = get_message_until_size_reached(socket, PACKET_HEADER_SEQNUM_SIZE);

	# print("[ack]: " + ack_inbytes.decode());

	return ack_inbytes;

def get_packet_checksum(socket):
	checksum_inbytes = get_message_until_size_reached(socket, PACKET_HEADER_CHECKSUM_SIZE);
	checksum = int(checksum_inbytes.decode());

	# print("[checksum]: " + str(checksum));

	return checksum;

def remove_excess_padding(socket, padding_size):
	get_message_until_size_reached(socket, padding_size);

def is_corrupted(packet_data, packet_checksum):
	generated_checksum = zlib.crc32(packet_data);

	print(str(generated_checksum) + " VS " + str(packet_checksum));

	return generated_checksum != packet_checksum;

class Status(Enum):
	OK = 0;
	IS_CORRUPTED = 1;

def get_packet(socket):
	ack_inbytes = get_packet_ack_inbytes(socket);
	checksum = get_packet_checksum(socket);

	remove_excess_padding(socket, CLIENT_PACKET_PADDING_SIZE);

	if (is_corrupted(ack_inbytes, checksum)):
		return None, Status.IS_CORRUPTED;

	ack = int(ack_inbytes.decode());

	return ack, Status.OK;

# ------ BUFFER PACKET FUNCTIONS ---------------------------------------------

buffered_packets = dict();

def buffer_packet(packet_seqnum, packet_data):
	# print("====== [BUFFERED]: " + str(packet_seqnum) + "======");
	buffered_packets[packet_seqnum] = packet_data;

def send_buffered_packets(socket):
	sorted_seqnums = sorted(buffered_packets.keys());

	for s in sorted_seqnums:
		socket.send(buffered_packets[s]);

def remove_acked_packet(acked_seqnum):
	# print("====== [PACKET ACKED]: " + str(packet_seqnum) + "======");
	del(buffered_packets[acked_seqnum]);
	 
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

print("====== STARTING NOW =======");

""" open the file to be sent """
input_fd = open(input_file_name, 'rb');

# curr_seqnum = 0;
# while (True):
# 	data_payload = input_fd.read(MAX_PACKET_DATA_SIZE);
# 	data_payload_length = len(data_payload);

# 	seqnum_header = generate_seqnum_header(curr_seqnum);
# 	checksum_header = generate_checksum_header(data_payload);
# 	length_header = generate_length_header(data_payload_length);

# 	packet = generate_packet(seqnum_header, checksum_header, length_header, data_payload);
# 	padded_packet = generate_padded_packet(packet, SERVER_PACKET_SIZE);

# 	clientSocket.send(padded_packet);
# 	buffer_packet(curr_seqnum, padded_packet);

# 	curr_seqnum = curr_seqnum + 1;
# 	# print("[sent]: ({}, {}, {})".format(seqnum_header, checksum_header, length_header));

# 	ack, packet_status = get_packet(clientSocket);
# 	if (packet_status == Status.IS_CORRUPTED):
# 		print("<== ACK PACKET IS CORRUPTED ==>");
# 	if (packet_status == Status.OK):
# 		print("[RECEIVED ACK]: ", str(ack));
# 		remove_acked_packet(ack);

# 	if (data_payload_length == 0):
# 		print("====== ALL DATA SENT ======");
# 		break;

WINDOW_SIZE = 10;
NEGATIVE_ACK = -1;
ALL_DATA_SUCCESSFULLY_RECEIVED_ACK = -2;

next_seqnum = 0;
stop_transmitting = False;
while (True):
	if (stop_transmitting == True):
		print("====== ALL DATA SUCCESSFULLY RECEIVED BY CLIENT ====== ");
		break;

	# SENDING PACKETS
	for i in range(WINDOW_SIZE):
		packet = generate_packet(input_fd, next_seqnum);
		buffer_packet(next_seqnum, packet);
		clientSocket.send(packet);

		next_seqnum = next_seqnum + 1;

	# RECEIVING ACKs
	for i in range(WINDOW_SIZE):
		ack, packet_status = get_packet(clientSocket);

		if (packet_status == Status.OK and ack != NEGATIVE_ACK):
			remove_acked_packet(ack);

		if (packet_status == Status.OK and ack == ALL_DATA_SUCCESSFULLY_RECEIVED_ACK):
			stop_transmitting = True;
			break;

	# RESEND ANY UNACKED PACKETS IN THIS WINDOW
	num_unacked_packets = len(buffered_packets);
	while (True):

		print("[NUM UNACKED PACKETS]: "+ str(num_unacked_packets));

		if (num_unacked_packets == 0):
			break;			
		
		send_buffered_packets(clientSocket);

		for j in range(num_unacked_packets):
			ack, packet_status = get_packet(clientSocket);

			print("[ACK RECEIVED]: "+ str(ack));

			if (packet_status == Status.OK and ack != NEGATIVE_ACK):
				remove_acked_packet(ack);

		num_unacked_packets = len(buffered_packets);


clientSocket.close();




"""
	add 10 packets to buffer

	send all packets in buffer (in order of seqnum)

	receive ACK messages, a
		remove ACKed packet from buffer

		if a >= expectedseqnum:
			expectedseqnum = a + 1
		else:
			resend all remaining packets in buffer


"""







""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================
- my student-key is 651723
- to test the code,
	python3 Server-A0218234L.py 651723 0 137.132.92.111 4445 hello.txt
"""