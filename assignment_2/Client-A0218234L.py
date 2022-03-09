import sys
from socket import *
import hashlib

# numbers indicating the mode of the simulators
RELIABLE_CHANNEL_MODE = 0;
ERROR_CHANNEL_MODE = 1;
REORDERING_CHANNEL_MODE = 2;

# port numbers of the 3 channels
RELIABLE_CHANNEL_PORT_NUMBER = 4445;
ERROR_CHANNEL_PORT_NUMBER = 4446;
REORDERING_CHANNEL_PORT_NUMBER = 4447;

# request method codes
REQUEST_CONNECTION = 'STID_';

""" ---- HELPER FUNCTIONS -------------------------------------------------- """

def create_request_message(method_code, data=''):
	print('[SENDING REQUEST MESSAGE] ' + method_code + data); # TO REMOVE
	return (method_code + data).encode();

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
clientSocket.send(create_request_message(REQUEST_CONNECTION, student_key + '_C'));
wait_for_turn(clientSocket);

""" open the file where the hash is to be written to
	if the file doesn't exist, create it
"""
fileToWriteTo = open(output_file_name, 'w+');
hasher = hashlib.md5();

num_bytes_received = 0;
while (True):
	dataReceived = clientSocket.recv(1024);

	if (len(dataReceived) == 0):
		break;

	num_bytes_received = num_bytes_received + len(dataReceived);
	print("[NUM_BYTES_RECEIVED]: " + str(num_bytes_received));
	
	hasher.update(dataReceived);

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