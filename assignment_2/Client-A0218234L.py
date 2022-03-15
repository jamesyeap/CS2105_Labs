import sys
from socket import *
import hashlib
import zlib
from enum import Enum

# request method codes
REQUEST_CONNECTION = 'STID_';

# ---- HELPER FUNCTIONS -------------------------------------------------------

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

def get_response_message(socket):
	return socket.recv(4);

# ---- CONNECTION FUNCTIONS -------------------------------------------------------

def wait_for_turn(socket):
	queue_len = get_response_message(socket);

	while (True):
		if (queue_len == b'0_'):
			break;
			
		print("[POSITION IN QUEUE]: " + str(queue_len)); # TO REMOVE
		queue_len = get_response_message(socket);


# ----- IMPORTANT INFO -------------------------------------------------------

SERVER_PACKET_SIZE = 1024;
PACKET_HEADER_SEQNUM_SIZE = 6;
PACKET_HEADER_CHECKSUM_SIZE = 10;
PACKET_HEADER_LENGTH_SIZE = 4;
TOTAL_PACKET_HEADER_SIZE = PACKET_HEADER_SEQNUM_SIZE + PACKET_HEADER_CHECKSUM_SIZE + PACKET_HEADER_LENGTH_SIZE;
MAX_PACKET_DATA_PAYLOAD_SIZE = SERVER_PACKET_SIZE - TOTAL_PACKET_HEADER_SIZE;

CLIENT_PACKET_SIZE = 64;

# ----- GENERATE ACK PACKET FUNCTIONS ----------------------------------------

def generate_ack_packet(seqnum):
	encoded_seqnum = str(seqnum).encode();
	ack_header = encoded_seqnum.rjust(PACKET_HEADER_SEQNUM_SIZE, b'0');

	checksum = zlib.crc32(ack_header);
	checksum_header = str(checksum).encode().rjust(PACKET_HEADER_CHECKSUM_SIZE, b'0');

	packet = ack_header + checksum_header;

	# print("[sent ack packet] (seqnum) | (checksum): " + str(seqnum) + " | " + str(checksum));

	return packet.ljust(CLIENT_PACKET_SIZE, b'0');

def send_ack(socket, seqnum):
	socket.send(generate_ack_packet(seqnum));

# ----- RECEIVE PACKET FUNCTIONS ---------------------------------------------

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

def get_packet_seqnum(socket):
	seqnum_inbytes = get_message_until_size_reached(socket, PACKET_HEADER_SEQNUM_SIZE);

	try:
		seqnum = int(seqnum_inbytes.decode());
		# print("[seqnum]: " + str(seqnum));
		return seqnum;
	except ValueError:
		# print("[seqnum]: " + "IS CORRUPTED");
		return None;

def get_packet_checksum(socket):
	checksum_inbytes = get_message_until_size_reached(socket, PACKET_HEADER_CHECKSUM_SIZE);

	try:
		checksum = int(checksum_inbytes.decode());
		# print("[checksum]: " + str(checksum));
		return checksum;
	except ValueError:
		# print("[checksum]: " + "IS CORRUPTED");
		return None;

def get_data_payload_length(socket):
	data_payload_length_inbytes = get_message_until_size_reached(socket, PACKET_HEADER_LENGTH_SIZE);

	try:
		data_payload_length = int(data_payload_length_inbytes.decode());
		# print("[data_payload_length] " + str(data_payload_length));
		return data_payload_length;
	except ValueError:
		# print("[data_payload_length]: " + "IS CORRUPTED");
		return None;

def get_packet_header(socket):
	seqnum = get_packet_seqnum(socket);
	checksum = get_packet_checksum(socket);
	data_payload_length = get_data_payload_length(socket);

	return seqnum, checksum, data_payload_length;

def remove_excess_padding(socket, padding_size):
	get_message_until_size_reached(socket, padding_size);

def is_corrupted(packet_data, packet_checksum):
	generated_checksum = zlib.crc32(packet_data);

	return generated_checksum != packet_checksum;

class Status(Enum):
	OK = 0;
	IS_CORRUPTED = 1;
	NO_MORE_DATA = 2;

def get_packet(socket):

	seqnum, checksum, data_payload_length = get_packet_header(socket);

	if (seqnum == None or checksum == None or data_payload_length == None):
		get_message_until_size_reached(socket, 1004); # ⚠️ just assume the packets are 1004 for now
		return -1, None, None, Status.IS_CORRUPTED;

	if (data_payload_length == 0):
		return None, None, None, Status.NO_MORE_DATA;
	else:
		packet_data = get_message_until_size_reached(socket, data_payload_length);

		padding_size = SERVER_PACKET_SIZE - data_payload_length - TOTAL_PACKET_HEADER_SIZE;
		remove_excess_padding(socket, padding_size);

		if (is_corrupted(packet_data, checksum)):
			return None, None, None, Status.IS_CORRUPTED;
		
		return seqnum, data_payload_length, packet_data, Status.OK;

# ----- BUFFER PACKET FUNCTIONS ----------------------------------------------

total_bytes_received = 0;
buffered_packets = dict();

def buffer_packet(packet_seqnum, packet_data):
	# print("====== [BUFFERED]: " + str(packet_seqnum) + "======");
	buffered_packets[packet_seqnum] = packet_data;

def write_buffered_packets(base_seqnum, fd):
	sorted_seqnums = sorted(buffered_packets.keys());

	lowest_seqnum = sorted_seqnums[0];
	highest_seqnum = sorted_seqnums[-1];

	total_bytes_read = 0;

	if (lowest_seqnum != base_seqnum + 1):
		return base_seqnum, total_bytes_read;

	for i in range(len(sorted_seqnums)):
		curr_seqnum = sorted_seqnums[i];
		data = buffered_packets[curr_seqnum];
		fd.write(data);
		# print("===== [FROM BUFFER]: WRITING SEQNUM: " + str(curr_seqnum) + " ======");
		total_bytes_read = total_bytes_read + len(data);

		del(buffered_packets[curr_seqnum]);

		if (i != len(sorted_seqnums)-1):
			adjacent_seqnum = sorted_seqnums[i+1];
			if (curr_seqnum != adjacent_seqnum - 1):
				return curr_seqnum, total_bytes_read;

	return highest_seqnum, total_bytes_read;

def print_buffer():
	w = "[PACKETS IN BUFFER]: ";

	for k in buffered_packets.keys():
		w = w + "[" + str(k) + "]";

	print(w);

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

print("====== STARTING NOW =======");

""" open the file where the hash is to be written to, if the file doesn't exist, create it """
output_fd = open(output_file_name, 'wb');

if (mode == '0'):
	# ================ for reliable-channel only ================================
	print("<< RUNNING RELIABLE-CHANNEL PROTOCOL >>");

	while (True):
		packet = clientSocket.recv(1024);
		output_fd.write(packet);

		if (len(packet) == 0):
			break;

if (mode == '1'):
	# ================ for error-channel only ================================
	print("<< RUNNING ERROR-CHANNEL PROTOCOL >>");

	NEGATIVE_ACK_SEQNUM = 999999;

	filesize = -1;

	# get file-size from server
	while (True):
		seqnum, data_payload_length, packet_data, packet_status = get_packet(clientSocket);

		if (packet_status == Status.IS_CORRUPTED):
			send_ackc(clientSocket, NEGATIVE_ACK_SEQNUM);
		else:
			filesize = int(packet_data.decode());
			send_ack(clientSocket, 0);
			break;

	# print("[FILESIZE RECEIVED]:" + str(filesize));

	seqnums_of_successfully_received_packets = set();
	expected_seqnum = 1;

	ALL_FILES_SUCCESSFULLY_RECEIVED_SEQNUM = 999998;

	while (True):

		# print("[TOTAL BYTES RECEIVED]: " + str(total_bytes_received));

		if (total_bytes_received == filesize):
			send_ack(clientSocket, 999998);
			print("=== ALL DATA RECEIVED. EXITING...... ===");
			break;
		seqnum, data_payload_length, packet_data, packet_status = get_packet(clientSocket);

		if (packet_status == Status.IS_CORRUPTED):
			# print("==> PACKET IS CORRUPTED");
			send_ack(clientSocket, NEGATIVE_ACK_SEQNUM);
			continue;

		if (seqnum == 0):
			# print("==> IGNORING DUPLICATE INIT PACKET");
			send_ack(clientSocket, 0);
			continue;

		if (packet_status == Status.OK):
			send_ack(clientSocket, seqnum);

			if (seqnum in seqnums_of_successfully_received_packets):
				# print("==> IGNORING DUPLICATE PACKET");
				continue;

			seqnums_of_successfully_received_packets.add(seqnum);

			if (seqnum == expected_seqnum):
				# print("==> WRITING PACKET");
				output_fd.write(packet_data);
				total_bytes_received = total_bytes_received + data_payload_length;

				if (len(buffered_packets) > 0):
					highest_received_seqnum, total_bytes_read = write_buffered_packets(expected_seqnum, output_fd);
					expected_seqnum = highest_received_seqnum + 1;
					total_bytes_received = total_bytes_received + total_bytes_read;
				else:
					expected_seqnum = expected_seqnum + 1;
			else:
				# print("==> BUFFERING PACKET");
				buffer_packet(seqnum, packet_data);

		if (packet_status == Status.NO_MORE_DATA):
			send_ack(clientSocket, 999998);

if (mode == '2'):
	# ================ for reordering-channel only ================================
	print("<< RUNNING REORDERING-CHANNEL PROTOCOL >>");

	PACKET_HEADER_FILESIZE_SIZE = 9;

	# get file-size from server first
	filesize_inbytes = get_message_until_size_reached(clientSocket, PACKET_HEADER_FILESIZE_SIZE);
	remove_excess_padding(clientSocket, SERVER_PACKET_SIZE - PACKET_HEADER_FILESIZE_SIZE);
	filesize = int(filesize_inbytes.decode());
	response_packet = (b'0').rjust(CLIENT_PACKET_SIZE, b'0');
	clientSocket.send(response_packet); # need to tell server that client knows the file-size as server will not send any packets until this to prevent re-ordering

	expected_seqnum = 0;
	while (True):
		if (expected_seqnum * MAX_PACKET_DATA_PAYLOAD_SIZE >= filesize):
			print("=== ALL DATA RECEIVED. EXITING...... ===");
			break;

		seqnum, checksum, data_payload_length = get_packet_header(clientSocket);

		packet_data = get_message_until_size_reached(clientSocket, data_payload_length);
		padding_size = SERVER_PACKET_SIZE - data_payload_length - TOTAL_PACKET_HEADER_SIZE;
		remove_excess_padding(clientSocket, padding_size);

		if (seqnum != expected_seqnum):
			print("===== BUFFERING SEQNUM: " + str(seqnum) + " =====");
			buffer_packet(seqnum, packet_data);
		else:
			output_fd.write(packet_data);
			print("===== WRITING SEQNUM: " + str(seqnum) + " ======");

			if (len(buffered_packets) == 0):
				expected_seqnum = expected_seqnum + 1;
			else:
				highest_received_seqnum = write_buffered_packets(expected_seqnum, output_fd);
				expected_seqnum = highest_received_seqnum + 1;
				print_buffer();

output_fd.close();
clientSocket.close();






























""" =============================================================================================
	======================== my own notes =======================================================
	=============================================================================================
- my student-key is 651723
- to test the code:
	python3 Client-A0218234L.py 651723 0 137.132.92.111 4445 myownoutput.txt
	python3 Server-A0218234L.py 651723 0 137.132.92.111 4445 myowninput.txt

	python3 Client-A0218234L.py 651723 1 137.132.92.111 4446 myownoutput.txt
	python3 Server-A0218234L.py 651723 1 137.132.92.111 4446 myowninput.txt

	python3 Client-A0218234L.py 651723 2 137.132.92.111 4447 myownoutput.txt
	python3 Server-A0218234L.py 651723 2 137.132.92.111 4447 myowninput.txt

- to run the reliable channel:
	On Terminal 1: (Client) ./test/FileTransfer.sh -i 651723 -n
	On Terminal 2: (server) ./test/FileTransfer.sh -s -i 651723 -n
	change the last option to
		-e  for error channel
		-r   for reorder channel
		-A  for running all three tests.

	./test/FileTransfer.sh -i 651723 -n
	./test/FileTransfer.sh -s -i 651723 -n

	./test/FileTransfer.sh -i 651723 -e
	./test/FileTransfer.sh -s -i 651723 -e

	./test/FileTransfer.sh -i 651723 -r
	./test/FileTransfer.sh -s -i 651723 -r

	./test/FileTransfer.sh -i 651723 -A
	./test/FileTransfer.sh -s -i 651723 -A


- link to faq:
	https://docs.google.com/document/d/1biPpAvd8F7VPTqY2QDVU4XY4xfnWuTnRDM1VGq3usg8/edit#heading=h.65tkp2u5p4vz
	
"""